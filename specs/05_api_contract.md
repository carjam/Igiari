# 05 — API Contract

Exact request/response shapes. Treat this as the source of truth — if the implementation diverges, update this document in the same commit, don't let it drift.

## Endpoint

```
POST /api/scan
Content-Type: application/json
```

## Request body

```json
{
  "text": "the pasted text to analyze, max 4000 characters"
}
```

| Field | Type | Required | Notes |
|---|---|---|---|
| `text` | string | yes | Trimmed of leading/trailing whitespace server-side before length check. Reject if empty after trimming. |

## Success response (200)

```json
{
  "input_length": 412,
  "findings": [
    {
      "span": "the exact substring from the input text",
      "start_index": 88,
      "end_index": 142,
      "fallacy": "Straw Man",
      "category": "Informal",
      "subcategory": "Other Informal Fallacy",
      "confidence": "high",
      "explanation": "One sentence explaining why this span matches the fallacy's pattern in context.",
      "what_would_strengthen_this": "One sentence naming what evidence, qualifier, or missing link would address the gap — not a rewritten version of the span."
    }
  ]
}
```

| Field | Type | Notes |
|---|---|---|
| `input_length` | int | Character count of the submitted text, echoed back for frontend display/debugging |
| `findings` | array | Can be empty — an empty array is a valid, expected, non-error result (see `01_product_requirements.md` F7) |
| `findings[].span` | string | Must be an exact substring of the original input — needed so the frontend can locate and highlight it. If the model returns a paraphrase instead of an exact substring, the backend should attempt to locate the closest matching substring server-side before responding; if no reasonable match is found, drop that finding rather than sending an unlocatable span to the frontend. |
| `findings[].start_index` / `end_index` | int | Character offsets into the original input, computed server-side once `span` is matched. The frontend should use these for highlighting, not re-search for the span string itself (avoids issues with repeated substrings). |
| `findings[].fallacy` | string | Canonical name, matching a `name` field in `fallacies.json` |
| `findings[].category` / `subcategory` | string | Pulled from `fallacies.json` for the matched fallacy name |
| `findings[].confidence` | string | One of `"high"`, `"medium"`, `"low"` |
| `findings[].explanation` | string | One to two sentences, plain language, specific to the quoted span — not a copy-pasted dictionary definition |
| `findings[].what_would_strengthen_this` | string | One sentence diagnosing what's missing (fact, qualifier, causal link, source). Must not be replacement prose for the flagged span — may be empty if the model omits it |

## Error responses

All errors return a consistent shape so the frontend can handle them uniformly:

```json
{
  "error": {
    "code": "TEXT_TOO_LONG",
    "message": "human-readable message safe to show directly in the UI"
  }
}
```

| HTTP status | `code` | When |
|---|---|---|
| 400 | `EMPTY_TEXT` | Text is empty/whitespace-only after trimming |
| 400 | `TEXT_TOO_LONG` | Text exceeds 4000 characters |
| 429 | `RATE_LIMITED` | IP has exceeded the rate limit — message should suggest a retry time if known |
| 502 | `MODEL_ERROR` | The Anthropic API call failed or returned unparseable output after retry |
| 500 | `INTERNAL_ERROR` | Anything else unexpected |

The frontend should display `message` directly for all error codes — don't write separate frontend copy per error code, keep the message itself UI-ready and in the product's voice (per `02_design_direction.md`), so there's a single source of truth for error copy.

## Notes for the backend implementer

- `start_index`/`end_index` existing means the frontend never needs to do its own text-search/highlighting logic — all positional work happens server-side, where the original text and the model's output are both already in hand. Keep this responsibility on the backend; don't push substring-matching logic into frontend JS.
- If the model flags overlapping spans, that's acceptable — don't try to silently merge or deduplicate overlaps in v1; render them as nested/adjacent highlights and treat any visual awkwardness here as a future-iteration polish item, not a blocker.
