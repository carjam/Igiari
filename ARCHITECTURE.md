# Architecture & Technical Highlights

> **Portfolio Project** - This document highlights the technical decisions and full-stack capabilities demonstrated in this SaaS application.

## Overview

**Igiari** is a production-ready logical fallacy detection tool that showcases:
- LLM integration with structured output parsing
- Complete monetization stack (Stripe billing, subscriptions, webhooks)
- Authentication & authorization with row-level security
- Modern async Python backend with comprehensive testing
- Clean vanilla JavaScript frontend (no framework bloat)
- Production deployment with proper observability

## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **Anthropic Claude API** - LLM integration for fallacy detection
- **Stripe** - Payment processing, subscriptions, webhook handling
- **Supabase** - PostgreSQL database + JWT authentication
- **Sentry** - Error tracking and monitoring
- Structured logging with request correlation
- Comprehensive test suite (pytest)

### Frontend
- **Vanilla JavaScript** - No framework dependencies, clean and maintainable
- **Supabase Auth** - Magic link + OTP email authentication
- **Stripe Checkout** - Hosted payment flows
- Server-driven UI (pricing/products loaded from backend)

### Infrastructure
- **Cloudflare Pages** - Static site hosting with global CDN
- **Render** - Backend API hosting (auto-deploy from git)
- **Supabase** - Database, auth, and RLS policies
- **Resend** - Transactional email via SMTP

## Key Technical Achievements

### 1. Complete Billing System

**Credit-based monetization** with:
- Account balance tracking with transaction ledger (source of truth)
- One-time purchases and recurring subscriptions
- Idempotent webhook processing (Stripe events)
- Row-level security to protect user data
- Service role vs authenticated role separation

**Files:** `backend/billing.py`, `backend/stripe_billing.py`, `supabase/migrations/`

### 2. LLM Integration with Quality Controls

- Structured prompt engineering with taxonomy injection
- Response parsing and validation
- Token usage tracking for cost monitoring
- Rate limiting (IP-based for anonymous, account-based for authenticated)
- Evaluation framework with ground truth dataset

**Files:** `backend/server.py`, `backend/run_eval.py`, `source-materials/eval/`

### 3. Authentication & Security

- Magic link + OTP email authentication (handles email prefetch issues)
- JWT verification on backend
- PostgreSQL Row-Level Security (RLS) policies
- Service role key isolation (backend only)
- CORS configuration for production

**Files:** `auth.js`, `supabase/migrations/20250620200000_initial_billing_schema.sql`

### 4. Production Observability

- Structured JSON logging with request correlation
- Sentry integration for error tracking
- Per-scan telemetry (tokens, cost, duration)
- Health checks and monitoring endpoints

**Files:** `backend/logging_config.py`, `backend/scan_observability.py`, `backend/error_tracking.py`

### 5. Testing & Quality

- Comprehensive test suite (unit + integration)
- Mocked Stripe/Supabase for isolated testing
- Eval framework with F1 scoring against ground truth
- CI-ready test structure

**Files:** `backend/tests/`, `backend/run_eval.py`

## Architecture Decisions

### Why this stack?

**FastAPI over Flask/Django:**
- Native async support for LLM API calls
- Automatic OpenAPI documentation
- Pydantic validation built-in
- Modern Python typing

**Vanilla JS over React/Vue:**
- No build step for frontend
- Instant deployments (Cloudflare Pages)
- Easier to maintain for solo dev
- Demonstrates core JavaScript skills

**Supabase over custom auth:**
- Managed PostgreSQL with instant APIs
- Built-in JWT handling
- Email delivery integration
- RLS policies for data security

**Stripe over custom billing:**
- PCI compliance handled
- Hosted checkout (no card storage)
- Subscription management built-in
- Reliable webhook system

### Data Flow

```
User Browser
    ↓
Cloudflare Pages (HTML/CSS/JS)
    ↓
FastAPI Backend (Render)
    ↓
    ├─→ Anthropic API (fallacy detection)
    ├─→ Supabase (auth verification, account balance)
    └─→ Stripe (checkout, webhook processing)
```

### Database Schema

**`accounts` table:**
- 1:1 with Supabase auth users
- Tracks credit balance (cached from ledger)
- Stripe customer ID mapping
- Subscription status

**`credit_transactions` table:**
- Append-only ledger (source of truth)
- Each row = credit change with reason
- Idempotency via `stripe_event_id` unique constraint
- Foreign key to accounts with cascade delete

**RLS policies:**
- Users can read their own account
- Backend service role handles all writes
- Transaction history protected (service role only)

## Deployment

### Current Status
**Archived (2026-10-16)** - Services paused to avoid ongoing costs. All code is production-ready and can be reactivated by:
1. Deploying backend to Render (auto-deploy from `master`)
2. Deploying frontend to Cloudflare Pages (auto-deploy from `master`)
3. Setting environment variables per `docs/INTEGRATIONS.md`

### Configuration Management

**Environment-based:**
- `backend/.env.example` - Template for local development
- `render.yaml` - Infrastructure as code for backend
- `site-config.js` - Frontend config (Supabase URL + anon key)

**Secrets management:**
- All secrets in environment variables (never committed)
- Supabase anon key safe for frontend (public-facing by design)
- Service role key backend-only

## Code Quality

### Project Organization
```
igiari/
├── backend/           # FastAPI app + billing logic
│   ├── tests/        # Comprehensive test suite
│   ├── billing.py    # Account/credit operations
│   ├── stripe_billing.py  # Stripe integration
│   └── server.py     # API endpoints
├── supabase/         # Database migrations
├── specs/            # Original build specifications
├── docs/             # Deployment runbooks
├── source-materials/ # Fallacy taxonomy + eval dataset
└── (root)            # Frontend static files
```

### Testing Strategy
- **Unit tests** - Pure functions (billing logic, parsing)
- **Integration tests** - API endpoints with mocked externals
- **Eval framework** - LLM output quality vs ground truth
- **Manual smoke tests** - Full user flows documented

### Documentation
- **Specs** - Original AI agent build instructions (showcases planning)
- **Docs** - Operational runbooks and integration guides
- **Code comments** - Inline explanations where logic is complex
- **API contract** - Request/response schemas documented

## Skills Demonstrated

✅ **Full-stack development** - Frontend to backend to database  
✅ **LLM integration** - Prompt engineering, structured outputs, cost control  
✅ **Payment processing** - Stripe checkout, subscriptions, webhooks  
✅ **Authentication** - Magic links, JWT, session management  
✅ **Database design** - Schema design, RLS, migrations  
✅ **Testing** - Unit, integration, and quality evaluation  
✅ **DevOps** - Git-based deployments, environment management  
✅ **Security** - RLS, CORS, rate limiting, secret management  
✅ **Observability** - Logging, error tracking, telemetry  
✅ **Documentation** - Comprehensive specs and runbooks

## Production Readiness

This project includes:
- ✅ Error handling and user-friendly messages
- ✅ Rate limiting and abuse prevention
- ✅ HTTPS-only in production
- ✅ Proper CORS configuration
- ✅ Idempotent operations (webhooks)
- ✅ Transactional consistency (credit ledger)
- ✅ Monitoring and alerting (Sentry)
- ✅ Cost controls (rate limits, spend caps)
- ✅ Legal compliance (terms, privacy policy)

---

**Contact:** [github.com/carjam](https://github.com/carjam)

**See also:**
- [README.md](README.md) - Quick start and project overview
- [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) - Service integration reference
- [specs/](specs/) - Complete build specifications
