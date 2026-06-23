# Fallacy Scanner Backend

FastAPI server for detecting logical fallacies using Claude Haiku 4.5.

## Setup

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   - Copy `.env.example` to `.env`
   - Add `ANTHROPIC_API_KEY` (required for scans)
   - For billing locally, add `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY` — see [docs/INTEGRATIONS.md](../docs/INTEGRATIONS.md)
   - **Never commit the `.env` file** (already in `.gitignore`)

## Running Locally

```bash
python server.py
```

Server runs on `http://localhost:8000`

API endpoint: `POST /api/scan`

### Full-stack UI (static site + backend)

1. Add at least `ANTHROPIC_API_KEY` to `backend/.env` (Supabase/Stripe optional for local scans).
2. Start the backend (above).
3. From the repo root, serve the static frontend on any port (e.g. `python -m http.server 49200`).
4. Open `http://127.0.0.1:49200/` — `site-config.js` points the UI at `http://127.0.0.1:8000` and skips sign-in/billing.

If your browser still has a production Supabase session, local mode ignores it so scans use the anonymous rate limit (10/hour per IP) instead of returning 503.

## Testing

### Quick Manual Test

```bash
curl -X POST http://localhost:8000/api/scan \
  -H "Content-Type: application/json" \
  -d '{"text": "Everyone I know loves this product, so it must be the best on the market."}'
```

### Phase 2: Quality Validation (Eval Set)

Run the backend against all 30 eval cases and compute quality metrics:

```bash
python run_eval.py
```

This will:
- Send each eval case to the running backend
- Compare predictions against ground truth
- Compute precision/recall/F1 and true-negative accuracy
- Check if quality meets the Phase 2 gate criteria

**Acceptance criteria:**
- ✅ Precision and recall computed (no fixed threshold for MVP)
- ✅ True-negative accuracy > 60% (don't hallucinate fallacies in clean text)
- ✅ Results reviewed by human before proceeding to Phase 3

## Observability

Each `/api/scan` emits a structured JSON log line (`event: scan_complete`) with finding count, spans dropped, parse retries, latency, and cache hit status. See `docs/DETECTION_RELEASE_CHECKLIST.md` for field definitions.

## Release workflow

See [`docs/DETECTION_RELEASE_CHECKLIST.md`](../docs/DETECTION_RELEASE_CHECKLIST.md) for the full edit → test → sync → eval → commit checklist.

### Unit tests

```bash
cd backend
python -m venv venv
# Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest tests/ -v --cov=. --cov-config=.coveragerc --cov-fail-under=100
```

CI runs the same suite on every push to `master` / `main` (`.github/workflows/backend-tests.yml`).

**Phase 5 quality gate (offline, no API key):** `tests/test_eval_quality_gate.py` grades the frozen baseline in `fallacy_reference/eval_baseline_predictions.json` and fails if F1 &lt; 0.75, precision &lt; 0.65, recall &lt; 0.80, or true-negative accuracy &lt; 1.0.

After an intentional prompt improvement via live eval:

```bash
python run_eval.py          # requires server + ANTHROPIC_API_KEY
python scripts/export_eval_baseline.py
python -m pytest tests/test_eval_quality_gate.py -v
```

## Rate Limiting

- 10 requests per IP per hour
- Enforced server-side for cost control

## Prompt Engineering

The system prompt is now **extracted to a separate file** for easy tweaking:

**📝 Edit the prompt**: `prompt_template.txt`

No need to touch Python code - just edit the template file and restart the server.

**See [docs/PROMPT_GUIDE.md](../docs/PROMPT_GUIDE.md)** for:
- How to test prompt changes
- Tips for improving precision/recall
- Deployment workflow

## Architecture Notes

- **Model**: Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)
- **Input limit**: 4,000 characters
- **Rate limiting**: In-memory token bucket (legacy; production scans require auth + credits)
- **Billing**: Supabase Postgres via REST — see `billing.py`, [docs/DEPLOY_RENDER.md](../docs/DEPLOY_RENDER.md)
- **Taxonomy**: 136 fallacies loaded at startup from `fallacy_reference/fallacies.json`
- **Prompt**: Loaded from `prompt_template.txt` at runtime
