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

## Rate Limiting

- 10 requests per IP per hour
- Enforced server-side for cost control

## Prompt Engineering

The system prompt is now **extracted to a separate file** for easy tweaking:

**📝 Edit the prompt**: `prompt_template.txt`

No need to touch Python code - just edit the template file and restart the server.

**See [PROMPT_GUIDE.md](PROMPT_GUIDE.md)** for:
- How to test prompt changes
- Tips for improving precision/recall
- Deployment workflow

## Architecture Notes

- **Model**: Claude Haiku 4.5 (`claude-haiku-4-5-20251001`)
- **Input limit**: 4,000 characters
- **Rate limiting**: In-memory token bucket (legacy; production scans require auth + credits)
- **Billing**: Supabase Postgres via REST — see `billing.py`, [DEPLOY_RENDER.md](DEPLOY_RENDER.md)
- **Taxonomy**: 136 fallacies loaded at startup from `fallacy_reference/fallacies.json`
- **Prompt**: Loaded from `prompt_template.txt` at runtime
