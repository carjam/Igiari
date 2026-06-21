"""
Fallacy Scanner Backend - Phase 1
Minimal FastAPI server for detecting logical fallacies via Anthropic API.
"""
import json
import os
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import anthropic

from billing import (
    billing_enabled,
    debit_scan_credit,
    load_account_from_token,
    require_credits,
)
from stripe_billing import (
    create_checkout_session,
    create_portal_session,
    handle_webhook_payload,
    list_public_products,
    stripe_enabled,
)

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="Fallacy Scanner API")

# Configure CORS - allow all origins for now (tighten in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Constants
MAX_INPUT_LENGTH = 4000
RATE_LIMIT_REQUESTS = 10
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
MODEL_NAME = "claude-haiku-4-5-20251001"
CACHE_MAX_SIZE = 1000  # Max entries before LRU eviction

# Global state
fallacy_taxonomy: List[Dict] = []
rate_limit_store: Dict[str, List[float]] = defaultdict(list)
response_cache: Dict[str, Dict] = {}  # SHA-256 hash -> API response

# Pydantic models
class ScanRequest(BaseModel):
    text: str = Field(..., min_length=1)

class Finding(BaseModel):
    span: str
    start_index: int
    end_index: int
    fallacy: str
    category: str
    subcategory: str
    confidence: str
    explanation: str

class ScanResponse(BaseModel):
    input_length: int
    findings: List[Finding]
    credits_remaining: Optional[int] = None


class CheckoutRequest(BaseModel):
    product_key: str = Field(..., min_length=1)


class CheckoutResponse(BaseModel):
    url: str


class PortalResponse(BaseModel):
    url: str


class ErrorResponse(BaseModel):
    error: Dict[str, str]


def load_taxonomy():
    """Load fallacy taxonomy from JSON file at startup."""
    global fallacy_taxonomy
    taxonomy_path = Path(__file__).parent / "fallacy_reference" / "fallacies.json"
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        fallacy_taxonomy = json.load(f)
    print(f"Loaded {len(fallacy_taxonomy)} fallacies from taxonomy")


def check_rate_limit(client_ip: str) -> bool:
    """
    IP-based rate limiting: 10 requests per hour per IP.
    Returns True if allowed, False if rate limited.
    """
    now = time.time()
    cutoff = now - RATE_LIMIT_WINDOW
    
    # Clean old timestamps
    rate_limit_store[client_ip] = [
        ts for ts in rate_limit_store[client_ip] if ts > cutoff
    ]
    
    # Check if under limit
    if len(rate_limit_store[client_ip]) >= RATE_LIMIT_REQUESTS:
        return False
    
    # Record this request
    rate_limit_store[client_ip].append(now)
    return True


def hash_text(text: str) -> str:
    """
    Create SHA-256 hash of trimmed/normalized text for cache key.
    """
    normalized = text.strip().lower()
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()


def load_prompt_template() -> str:
    """
    Load the prompt template from file.
    Template can be edited without touching server code.
    """
    template_path = Path(__file__).parent / "prompt_template.txt"
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def build_system_prompt() -> str:
    """
    Construct system prompt with taxonomy and calibration guidance.
    Using full taxonomy (option a) per spec 03_architecture.md.
    """
    # Create condensed taxonomy entries
    taxonomy_text = "\n".join([
        f"- **{f['name']}** ({f['category']}, {f['subcategory']}): {f['definition']}"
        for f in fallacy_taxonomy
    ])
    
    # Load template and inject taxonomy
    template = load_prompt_template()
    prompt = template.replace("{TAXONOMY}", taxonomy_text)
    
    return prompt


def find_span_indices(text: str, span: str) -> Optional[tuple[int, int]]:
    """
    Find start and end indices of span in text.
    Returns None if exact span not found.
    """
    start = text.find(span)
    if start == -1:
        return None
    return (start, start + len(span))


async def call_anthropic_api(user_text: str) -> Dict:
    """
    Call Anthropic API with the user text.
    Returns parsed JSON response.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")
    
    client = anthropic.Anthropic(api_key=api_key)
    system_prompt = build_system_prompt()
    
    try:
        message = client.messages.create(
            model=MODEL_NAME,
            max_tokens=4096,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_text}
            ]
        )
        
        # Extract text content
        response_text = message.content[0].text
        
        # Strip markdown code fences if present
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]  # Remove ```json
        elif response_text.startswith("```"):
            response_text = response_text[3:]  # Remove ```
        if response_text.endswith("```"):
            response_text = response_text[:-3]  # Remove closing ```
        response_text = response_text.strip()
        
        # Parse JSON
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            # Retry once if JSON parsing fails
            print(f"JSON parse error on first attempt: {e}")
            print(f"Response text: {response_text[:500]}")
            
            # Second attempt with explicit instruction
            retry_prompt = system_prompt + "\n\nIMPORTANT: Return ONLY valid JSON, no markdown code fences or other text."
            message = client.messages.create(
                model=MODEL_NAME,
                max_tokens=4096,
                system=retry_prompt,
                messages=[
                    {"role": "user", "content": user_text}
                ]
            )
            response_text = message.content[0].text.strip()
            
            # Strip markdown again on retry
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            return result
            
    except Exception as e:
        print(f"Anthropic API error: {e}")
        raise


@app.on_event("startup")
async def startup_event():
    """Load taxonomy on startup."""
    load_taxonomy()


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "fallacy-scanner-api"}


def extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    token = parts[1].strip()
    return token or None


@app.get("/api/account/me")
async def get_account_me(authorization: Optional[str] = Header(default=None)):
    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "NOT_SIGNED_IN",
                "message": "Sign in to view your account.",
            },
        )

    account = load_account_from_token(token)
    return {
        "email": account["email"],
        "credit_balance": account["credit_balance"],
        "free_trial_granted": account["free_trial_granted"],
        "subscription_status": account["subscription_status"],
        "stripe_customer_id": account.get("stripe_customer_id"),
        "payments_enabled": stripe_enabled(),
    }


@app.get("/api/billing/products")
async def get_billing_products():
    return {"products": list_public_products()}


@app.post("/api/billing/checkout", response_model=CheckoutResponse)
async def post_billing_checkout(
    body: CheckoutRequest,
    authorization: Optional[str] = Header(default=None),
):
    if not stripe_enabled():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "STRIPE_UNAVAILABLE",
                "message": "Payments are not configured on this server yet.",
            },
        )

    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "NOT_SIGNED_IN",
                "message": "Sign in to purchase scans.",
            },
        )

    account = load_account_from_token(token)
    url = create_checkout_session(account, body.product_key.strip())
    return {"url": url}


@app.post("/api/billing/portal", response_model=PortalResponse)
async def post_billing_portal(authorization: Optional[str] = Header(default=None)):
    if not stripe_enabled():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "STRIPE_UNAVAILABLE",
                "message": "Payments are not configured on this server yet.",
            },
        )

    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "NOT_SIGNED_IN",
                "message": "Sign in to manage billing.",
            },
        )

    account = load_account_from_token(token)
    url = create_portal_session(account)
    return {"url": url}


@app.post("/api/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    handle_webhook_payload(payload, signature)
    return {"received": True}


@app.post("/api/scan", response_model=ScanResponse)
async def scan_text(
    request: Request,
    body: ScanRequest,
    authorization: Optional[str] = Header(default=None),
):
    """
    Main endpoint: analyze text for logical fallacies.
    When billing is enabled: sign-in and credits required (no anonymous scans).
    When billing is disabled: anonymous IP rate limit (local dev only).
    """
    token = extract_bearer_token(authorization)
    account = None
    user_id = None

    if token and billing_enabled():
        account = load_account_from_token(token)
        require_credits(account)
        user_id = account["id"]
    elif token and not billing_enabled():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "BILLING_UNAVAILABLE",
                "message": "Sign-in is not available on this server yet.",
            },
        )
    elif billing_enabled():
        raise HTTPException(
            status_code=401,
            detail={
                "code": "NOT_SIGNED_IN",
                "message": "Sign in to scan. New accounts get 20 free scans.",
            },
        )
    else:
        client_ip = request.client.host
        if not check_rate_limit(client_ip):
            raise HTTPException(
                status_code=429,
                detail={
                    "code": "RATE_LIMITED",
                    "message": "You've exceeded the rate limit of 10 scans per hour. Please try again later.",
                },
            )
    
    # Trim and validate input
    text = body.text.strip()
    
    if not text:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "EMPTY_TEXT",
                "message": "Please provide some text to analyze."
            }
        )
    
    if len(text) > MAX_INPUT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "TEXT_TOO_LONG",
                "message": f"Text exceeds the {MAX_INPUT_LENGTH} character limit. Please shorten your input."
            }
        )
    
    # Check cache first (Phase 3.5)
    cache_key = hash_text(text)
    if cache_key in response_cache:
        print(f"Cache hit for hash: {cache_key[:16]}...")
        cached_response = response_cache[cache_key]
        credits_remaining = account["credit_balance"] if account else None
        return ScanResponse(
            input_length=cached_response["input_length"],
            findings=[Finding(**f) for f in cached_response["findings"]],
            credits_remaining=credits_remaining,
        )
    
    # Cache miss - proceed with API call
    print(f"Cache miss for hash: {cache_key[:16]}...")
    
    # Call Anthropic API
    try:
        raw_result = await call_anthropic_api(text)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=502,
            detail={
                "code": "MODEL_ERROR",
                "message": "The AI model returned an invalid response. Please try again."
            }
        )
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred. Please try again later."
            }
        )
    
    # Process findings
    findings = []
    for finding in raw_result.get("findings", []):
        span = finding.get("span", "")
        
        # Find exact span in original text
        indices = find_span_indices(text, span)
        
        if indices is None:
            # Span not found exactly - skip this finding per spec
            print(f"Warning: Could not locate span in text: {span[:50]}...")
            continue
        
        start_idx, end_idx = indices
        
        findings.append(Finding(
            span=span,
            start_index=start_idx,
            end_index=end_idx,
            fallacy=finding.get("fallacy", "Unknown"),
            category=finding.get("category", "Unknown"),
            subcategory=finding.get("subcategory", "Unknown"),
            confidence=finding.get("confidence", "medium"),
            explanation=finding.get("explanation", "")
        ))
    
    # Store in cache (Phase 3.5)
    response_data = {
        "input_length": len(text),
        "findings": [f.model_dump() for f in findings]
    }
    response_cache[cache_key] = response_data
    
    # LRU eviction: remove oldest entry if over max size
    if len(response_cache) > CACHE_MAX_SIZE:
        oldest_key = next(iter(response_cache))
        del response_cache[oldest_key]
        print(f"Cache evicted oldest entry (size was {CACHE_MAX_SIZE + 1})")

    credits_remaining = None
    if user_id:
        credits_remaining = debit_scan_credit(user_id)

    return ScanResponse(
        input_length=len(text),
        findings=findings,
        credits_remaining=credits_remaining,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
