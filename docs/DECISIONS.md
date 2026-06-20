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

**Status:** TODO - implement after Phase 2 passes, before Phase 4 deployment.
