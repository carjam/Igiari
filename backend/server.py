"""
Fallacy Scanner Backend - Phase 1
Minimal FastAPI server for detecting logical fallacies via Anthropic API.
"""
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import anthropic

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

# Global state
fallacy_taxonomy: List[Dict] = []
rate_limit_store: Dict[str, List[float]] = defaultdict(list)

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
    
    prompt = f"""You are a logical fallacy detection system. Your task is to analyze text and identify logical fallacies.

TAXONOMY OF 136 FALLACIES:
{taxonomy_text}

OUTPUT FORMAT:
Return ONLY valid JSON matching this schema (no other text):
{{
  "findings": [
    {{
      "span": "exact substring from input",
      "fallacy": "canonical name from taxonomy",
      "category": "Formal or Informal",
      "subcategory": "from taxonomy",
      "confidence": "high, medium, or low",
      "explanation": "1-2 sentences explaining why this span matches the pattern"
    }}
  ]
}}

CRITICAL CALIBRATION RULES:
1. **Confidence matters more than coverage.** A text may contain ZERO fallacies. Do not manufacture findings.
2. **Distinguish real fallacies from merely weak arguments.** Not every bad argument is a named fallacy.
3. **Quote exact substrings.** The span MUST be an exact substring from the input, not a paraphrase.
4. **True negatives are valid.** Returning an empty findings array is a correct, expected outcome for clean text.
5. **No dark patterns.** Do not over-flag or fabricate results to seem more useful. Trustworthiness is paramount.
6. **Ambiguous cases**: If borderline, mark confidence as "low" rather than forcing a binary call.

Return valid JSON only. If no fallacies found, return {{"findings": []}}"""
    
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
        
        # Parse JSON
        try:
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError as e:
            # Retry once if JSON parsing fails
            print(f"JSON parse error on first attempt: {e}")
            print(f"Response text: {response_text[:500]}")
            
            # Second attempt
            message = client.messages.create(
                model=MODEL_NAME,
                max_tokens=4096,
                system=system_prompt + "\n\nIMPORTANT: Return ONLY valid JSON, no markdown or other text.",
                messages=[
                    {"role": "user", "content": user_text}
                ]
            )
            response_text = message.content[0].text
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


@app.post("/api/scan", response_model=ScanResponse)
async def scan_text(request: Request, body: ScanRequest):
    """
    Main endpoint: analyze text for logical fallacies.
    """
    # Get client IP
    client_ip = request.client.host
    
    # Check rate limit
    if not check_rate_limit(client_ip):
        raise HTTPException(
            status_code=429,
            detail={
                "code": "RATE_LIMITED",
                "message": "You've exceeded the rate limit of 10 scans per hour. Please try again later."
            }
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
    
    return ScanResponse(
        input_length=len(text),
        findings=findings
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
