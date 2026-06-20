# Decisions Log

Append-only. Each entry: what default was changed, why, and which spec section it deviates from.

## 2026-06-19: Model name investigation

**Issue:** Initial 404 errors when testing the API with model `claude-haiku-4-5-20251001`.

**Resolution:** Confirmed with Anthropic site that `claude-haiku-4-5-20251001` IS available with this API key. Reverted to original spec model name.

**Status:** Using `claude-haiku-4-5-20251001` as specified in `specs/03_architecture.md`.
