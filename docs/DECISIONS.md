# Decisions Log

Append-only. Each entry: what default was changed, why, and which spec section it deviates from.

## 2026-06-19: Model name investigation

**Issue:** Initial 404 errors when testing the API with model `claude-haiku-4-5-20251001`.

**Resolution:** Confirmed with Anthropic site that `claude-haiku-4-5-20251001` IS available with this API key. Reverted to original spec model name.

**Status:** Using `claude-haiku-4-5-20251001` as specified in `specs/03_architecture.md`.

## 2026-06-19: Caching upgraded from SHOULD to MUST

**Deviation from:** `specs/03_architecture.md` (marks caching as "nice-to-have, not blocking")

**Decision:** Response caching upgraded to REQUIRED before launch.

**Reason:** Cost control is critical for a free public tool. Caching identical requests (SHA-256 hash of input) prevents redundant API calls, especially important if a text goes viral or gets shared widely.

**Implementation deferred:** Not implemented during Phases 0-3 to avoid interfering with quality validation testing. Will be added as **Phase 3.5** (post-validation, pre-deployment).

**Implementation plan:**
- In-memory dict keyed by SHA-256 hash of trimmed/normalized input
- Store full API response (findings array)
- Optional: Max size (e.g., 1000 entries) with LRU eviction
- Optional: TTL (e.g., 24 hours)

**Status:** ✅ Implemented in `backend/server.py` (in-memory SHA-256 cache).

## 2026-06-20: Static files at repo root

**Deviation from:** `specs/00_master_spec.md` (assumed `frontend/` subdirectory)

**Decision:** Deploy static site from repository root for Cloudflare Pages (no build step).

**Reason:** Simpler Pages config; `frontend/` retained as pointer README only.

## 2026-06-20: Sign-in required in production

**Deviation from:** `specs/10_monetization.md` (anonymous taste path unchanged)

**Decision:** When Supabase billing env vars are set on Render, `/api/scan` requires a valid Bearer token; anonymous IP-only scans disabled.

**Reason:** Anonymous free scans undermined signup conversion for Step 1 monetization experiment.

## 2026-06-20: Supabase REST from backend

**Decision:** Use `requests` against Supabase REST with service role key (`backend/billing.py`), not `supabase-py`.

**Reason:** `supabase-py` hung on Render during initial deploy.

## 2026-06-20: Free trial reduced to 5 scans

**Decision:** `TRIAL_CREDITS = 5` (was 20 in spec).

**Reason:** Lower API exposure per signup while still enough to evaluate the tool. Existing accounts retain prior balances.

## 2026-06-20: Consumer Stripe live; legal billing deferred

**Decision:** Render uses Stripe **live** keys for consumer Starter ($8) and Casual ($9/mo). Legal price env vars (`STRIPE_PRICE_LEGAL_*`) remain unset until outreach prep.

**Reason:** Ship real consumer revenue first; legal funnel uses interim consumer checkout until [LEGAL_BILLING_SETUP.md](LEGAL_BILLING_SETUP.md) is completed.

**Docs:** [STRIPE_GO_LIVE.md](STRIPE_GO_LIVE.md), [MONETIZATION_ROLLOUT.md](MONETIZATION_ROLLOUT.md).
