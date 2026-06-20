# TODO: Implement Response Caching (Phase 3.5)

**Priority:** REQUIRED before deployment  
**When:** After Phase 2 validation passes, before Phase 4 deployment  
**Estimated time:** 15-20 minutes

---

## Why This Is Required

Response caching was upgraded from SHOULD to MUST (see `DECISIONS.md`). Cost control is critical for a free public tool. If a text goes viral or gets shared, we need to avoid redundant API calls for identical inputs.

---

## Implementation Plan

### 1. Add Cache Storage (In-Memory Dict)

```python
# At top of server.py with other global state
response_cache: Dict[str, Dict] = {}  # SHA-256 hash -> API response
CACHE_MAX_SIZE = 1000  # Optional: LRU eviction
```

### 2. Create Hash Function

```python
import hashlib

def hash_text(text: str) -> str:
    """Create SHA-256 hash of trimmed/normalized text for cache key."""
    normalized = text.strip().lower()
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()
```

### 3. Check Cache Before API Call

In `scan_text()` endpoint, before calling `call_anthropic_api()`:

```python
# Check cache
cache_key = hash_text(text)
if cache_key in response_cache:
    print(f"Cache hit for hash: {cache_key[:16]}...")
    cached_response = response_cache[cache_key]
    return ScanResponse(**cached_response)
```

### 4. Store Response After API Call

After successful API response:

```python
# Store in cache
response_data = {
    "input_length": len(text),
    "findings": findings
}
response_cache[cache_key] = response_data

# Optional: Evict oldest if over max size
if len(response_cache) > CACHE_MAX_SIZE:
    # Remove oldest entry (dict is ordered in Python 3.7+)
    oldest_key = next(iter(response_cache))
    del response_cache[oldest_key]
```

### 5. Optional Enhancements (If Time Allows)

**TTL (Time-To-Live):**
```python
import time

cache_with_ttl: Dict[str, tuple[Dict, float]] = {}  # hash -> (response, timestamp)
CACHE_TTL = 86400  # 24 hours in seconds

# When storing:
cache_with_ttl[cache_key] = (response_data, time.time())

# When checking:
if cache_key in cache_with_ttl:
    response_data, timestamp = cache_with_ttl[cache_key]
    if time.time() - timestamp < CACHE_TTL:
        # Cache hit, not expired
        return ScanResponse(**response_data)
    else:
        # Expired, remove
        del cache_with_ttl[cache_key]
```

---

## Testing

### Test 1: Cache Hit
```bash
# First request (cache miss, calls API)
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Test text for caching"}'

# Second identical request (cache hit, no API call)
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Test text for caching"}'
```

**Expected:** 
- First request: Normal API call (~5-10 sec)
- Second request: Instant response (<100ms)
- Server logs: "Cache hit for hash: ..."

### Test 2: Cache Normalization
```bash
# Different whitespace/casing should hit same cache entry
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "  TEST TEXT  "}'
```

**Expected:** Cache hit (same normalized hash)

### Test 3: Different Text
```bash
# Different text should miss cache
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Different text entirely"}'
```

**Expected:** Cache miss, new API call

---

## Verification Checklist

Before deploying to production:

- [ ] Cache implementation added to `server.py`
- [ ] Cache hit/miss logged for monitoring
- [ ] Test 1 (identical text) passes - instant second response
- [ ] Test 2 (whitespace variations) passes - normalized correctly
- [ ] Test 3 (different text) passes - cache miss works
- [ ] Optional: LRU eviction tested (if implemented)
- [ ] Optional: TTL expiration tested (if implemented)
- [ ] Documented in backend README
- [ ] Committed with clear message referencing Phase 3.5

---

## Success Criteria

- ✅ Identical requests return instantly (no API call)
- ✅ Server logs show "Cache hit" for repeated text
- ✅ Different text still triggers API call (cache not over-matching)
- ✅ Cost savings measurable (track cache hit rate in production)

---

**DO NOT implement this until Phase 2 validation passes!**

Testing (especially eval) needs real API calls, not cached responses.
