# Build Spec: Fallacy Scanner — Demand-Test MVP

## Read this first

This is a spec for building a **minimal web tool**, not the full product. The goal is narrow: find out, as cheaply as possible, whether real people will use and pay for a tool that detects logical fallacies in text. Everything in this spec is scoped to that goal. Resist scope creep — if a task isn't in this document, don't build it yet, even if it seems obviously good. Flag it instead (see `08_future_ideas.md`) and move on.

If you are an agent picking this up cold: read 00–03 for context, then check **`11_monetization_rollout_plan.md`** for the current execution plan. Phases 0–4 in `04_build_phases.md` are complete; Phase 5 (soft launch) and monetization Steps 0–3 in spec 11 are active work.

## What this product is

A web page where someone pastes in text (an email, an article, an ad, a transcript) and gets back the same text with logical fallacies highlighted inline, each with a short explanation and the fallacy's name. Think "Grammarly, but for bad reasoning instead of bad grammar."

## What this product explicitly is NOT (yet)

- Not a browser extension (no DOM injection into arbitrary websites)
- Not yet a service with user accounts, billing, or subscriptions in the **original MVP scope** — monetization is now planned in `10_monetization.md` and rolled out incrementally per `11_monetization_rollout_plan.md`
- Not a mobile app
- Not a tool that fetches/scrapes arbitrary URLs server-side (legal/scraping complexity — out of scope; users paste text directly)
- Not multi-language (English only for v1)
- Not a fine-tuned or custom model — this calls the Anthropic API with the fallacy-detection skill's taxonomy as context, nothing more exotic

## Repo / file structure (actual layout)

The MVP spec originally assumed a `frontend/` subdirectory. **Production static files live at the repository root** (Cloudflare Pages deploys `/`). The empty `frontend/` folder only holds a pointer README.

```
igiari/
├── index.html, app.js, auth.js, styles.css, analytics.js
├── site-config.js          # Supabase publishable key, analytics token (committed)
├── legal/                  # privacy, terms, copyright
├── backend/                # FastAPI — holds API key + billing
│   ├── server.py, billing.py
│   ├── fallacy_reference/
│   ├── requirements.txt, Procfile, runtime.txt
│   └── .env.example
├── supabase/               # SQL migrations, email templates
│   ├── migrations/
│   └── email-templates/
├── specs/                  # build + monetization specifications
├── docs/                   # deployment, integrations, runbooks
├── source-materials/       # original taxonomy + eval set (read-only reference)
├── render.yaml             # Render service definition
└── README.md
```

## Source materials you already have

A prior project produced a fallacy-detection skill with a full taxonomy and an eval set. **Reuse these, don't recreate them.** They are bundled in `../source-materials/` alongside this specs folder:
- `source-materials/references/fallacies.json` — 136 fallacies, structured
- `source-materials/references/fallacy_taxonomy.md` — same data as readable markdown
- `source-materials/eval/eval_set.json` — 30 labeled test cases, used in Phase 2 to validate the backend's detection quality
- `source-materials/eval/grade_eval.py` — the original grading script; adapt its matching logic for Phase 2 rather than rewriting it
- `source-materials/SKILL.md` — contains the prompting logic (output schema, calibration notes) that should inform the backend's prompt to the model

If these files are missing from your working directory for any reason, stop and ask the human rather than recreating the taxonomy from scratch — recreating it risks drifting from the eval set's ground truth.

## Files in this spec folder

1. `00_master_spec.md` — this file
2. `01_product_requirements.md` — what the tool must do, from a user's perspective, with explicit in/out scope
3. `02_design_direction.md` — visual identity guidance (not generic AI-template look)
4. `03_architecture.md` — concrete technical decisions: stack, hosting, API key handling, why
5. `04_build_phases.md` — the actual sequenced task list with dependencies and acceptance criteria — **the main thing to execute against**
6. `05_api_contract.md` — exact request/response schema between frontend and backend
7. `06_testing_and_launch_checklist.md` — what "done enough to launch" means
8. `07_monetization_notes.md` — why the MVP deferred monetization; ads still rejected
9. `08_future_ideas.md` — explicitly out of scope, parking lot for later
10. `09_legal_positioning_and_pricing..md` — legal beachhead copy and pricing
11. `10_monetization.md` — full monetization architecture and pricing
12. `11_monetization_rollout_plan.md` — **phased execution plan (start here for current work)**

## Definition of done

**MVP (Phases 0–4) — complete:** A working public URL where a stranger can paste text, click a button, and within ~10 seconds see fallacies highlighted — with rate limiting in place. See `06_testing_and_launch_checklist.md`.

**Monetization experiment — in progress:** Step 0 launch readiness, then consumer billing (Step 1), then first revenue channel via legal landing (Step 2). See `11_monetization_rollout_plan.md`.
