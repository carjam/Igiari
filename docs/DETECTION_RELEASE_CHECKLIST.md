# Fallacy Detection Release Checklist

Use this checklist whenever changing **prompt**, **taxonomy**, **eval set**, or **golden examples**. Igiari is canonical; the Cursor skill is synced from it.

## 1. Edit canonical sources only (Igiari)

| Change | Edit here |
|--------|-----------|
| Prompt / calibration rules | `backend/prompt_template.txt` |
| Taxonomy | `backend/fallacy_reference/fallacies.json` |
| Eval benchmark | `backend/fallacy_reference/eval_set.json` |
| Golden examples | `backend/fallacy_reference/examples.json` |

Do **not** edit skill `reference/*` by hand.

## 2. Run tests (required before push)

```bash
cd backend
python -m venv venv   # first time only
# Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest tests/ -v --cov=. --cov-config=.coveragerc --cov-fail-under=100
```

This suite includes:
- Prompt / injection guards
- Eval set schema validation
- **Phase 5 quality gate** (F1 ≥ 0.75, precision ≥ 0.65, recall ≥ 0.80, TN accuracy ≥ 1.0) against `fallacy_reference/eval_baseline_predictions.json`

CI runs the same command on every push (`.github/workflows/backend-tests.yml`).

## 3. Sync Cursor skill

```bash
python backend/scripts/sync_cursor_skill.py
# or from the skill directory:
python scripts/sync_from_igiari.py
```

If new skill files were added, run `install-junctions.ps1` in AIDevTools (Windows junctions).

## 4. Live eval (prompt/taxonomy changes only)

Requires `ANTHROPIC_API_KEY` and a running server:

```bash
# Terminal 1
$env:IGIARI_DISABLE_RATE_LIMIT="1"   # PowerShell
cd backend
python server.py

# Terminal 2
cd backend
python run_eval.py
```

`run_eval.py` exits non-zero if Phase 5 gates fail on the live run.

## 5. Update CI baseline (after intentional quality improvement)

If live eval meets gates and you accept the new behavior:

```bash
python scripts/export_eval_baseline.py
python -m pytest tests/test_eval_quality_gate.py -v
git add fallacy_reference/eval_baseline_predictions.json
```

## 6. Commit both repos

- **igiari** — prompt, taxonomy, eval, examples, tests, baseline, observability
- **AIDevTools** — synced `logical-fallacy-detection/reference/*` and `SKILL.md`

## 7. Deploy note

Igiari backend push triggers production CI/CD. Never push without step 2 passing locally.

---

## Observability (Phase 6)

Each successful `/api/scan` emits one JSON log line:

```json
{
  "event": "scan_complete",
  "input_length": 842,
  "finding_count": 2,
  "spans_dropped": 1,
  "parse_retries": 0,
  "latency_ms": 1240,
  "cache_hit": false,
  "raw_finding_count": 3,
  "model_latency_ms": 1180,
  "request_id": "b7b6e2b0-..."
}
```

| Field | Meaning |
|-------|---------|
| `finding_count` | Findings returned to client |
| `spans_dropped` | Model spans rejected (not verbatim in input) |
| `parse_retries` | JSON parse retries (0 or 1) |
| `latency_ms` | Total request time |
| `model_latency_ms` | Anthropic call time (cache miss only) |
| `cache_hit` | Response served from in-memory cache |
| `request_id` | Correlates this line to the `x-request-id` response header and any error logs/Sentry events for the same request |

Filter production logs: `event=scan_complete`.

**Alerting is wired, not just aspirational**: any scan with `spans_dropped > 0` or
`parse_retries > 0` also fires a `scan_quality_degraded` Sentry message (warning level,
telemetry attached) — see `scan_observability.log_scan_complete`. Requires `SENTRY_DSN` to
be set (see `docs/DEPLOYMENT_GUIDE.md` § Error Tracking); configure a Sentry alert rule on
that message to get paged on detection-quality regressions instead of manually grepping logs.

---

## Quick reference

| Artifact | Path |
|----------|------|
| Canonical prompt | `backend/prompt_template.txt` |
| CI quality baseline | `backend/fallacy_reference/eval_baseline_predictions.json` |
| Eval history | `backend/eval_history.json` |
| Sync script | `backend/scripts/sync_cursor_skill.py` |
| Export baseline | `backend/scripts/export_eval_baseline.py` |
| Cursor skill | `AIDevTools/Claude/cursor-skills/logical-fallacy-detection/` |
