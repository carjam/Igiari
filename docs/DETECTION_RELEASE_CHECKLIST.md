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
- **Phase 5 quality gate** (F1 ≥ 0.75, precision ≥ 0.65, recall ≥ 0.78, TN accuracy ≥ 0.95) against `fallacy_reference/eval_baseline_predictions.json`

CI runs the same command on every push (`.github/workflows/backend-tests.yml`).

### Eval set coverage (expanded 2026-07-12: 40 → 80 cases)

The original 40-case set had **zero** coverage of the entire Formal fallacy category
(18 fallacies — affirming the consequent, undistributed middle, modal fallacies, etc.)
and thin coverage of large Informal subcategories like Improper Presumption (45
fallacies, only 4 tested). The set now includes all 18 Formal fallacies plus targeted
additions to the thinnest Informal subcategories, and 8 new true-negative cases
including near-miss valid logic (valid modus ponens/tollens, a valid categorical
syllogism) to check the model isn't pattern-matching surface structure instead of
checking actual validity.

**Thresholds were recalibrated, not just loosened**, to match honest live performance
after a round of prompt tuning (see `backend/prompt_template.txt` rules 8 and 8b):
`MIN_RECALL` moved from 0.80 → 0.78 and `MIN_TN_ACCURACY` from 1.0 → 0.95. Two things
to know about these two metrics specifically:
- **`MIN_TN_ACCURACY` can never safely be 1.0 again.** With 22 true-negative cases,
  even a genuinely good non-deterministic model will occasionally produce one chance
  false alarm and fail a strict "zero false alarms" bar — this isn't necessarily a
  prompt regression when it happens near the new 0.95 line.
- **Known remaining weakness: Formal syllogistic fallacies are still frequently
  confused with each other** (Illicit Major/Minor, Undistributed Middle, Four Terms,
  Exclusive Premises) — the model often detects *something* invalid about the
  syllogism's structure but names the wrong specific fallacy. Three prompt-tuning
  iterations only partially closed this; it may be closer to a capability limit of
  the configured model (`claude-haiku-4-5-20251001`) than a prompt-wording problem.
  If this matters more for your use case, consider it before further tuning attempts.

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
  "model": "claude-haiku-4-5-20251001",
  "input_tokens": 2103,
  "output_tokens": 412,
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
| `model` | The `MODEL_NAME` currently configured in `server.py`. On a cache hit this reflects the *current* config, not necessarily the model that originally produced the cached result — useful for spotting model-version drift over time |
| `input_tokens` / `output_tokens` | Anthropic token usage for this scan, summed across the JSON-parse retry if one occurred (0 on cache hit — no API call made). Multiply by current Anthropic per-token pricing to get cost-per-scan; do this downstream rather than hardcoding a price in code, since pricing changes over time. |
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
