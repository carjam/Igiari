# Igiari! (異議あり!)

**Objection!** — A logical fallacy scanner for text.

Paste an argument, email, article, or transcript and see logical fallacies highlighted inline with explanations. Think "Grammarly, but for bad reasoning instead of bad grammar."

## 🚀 Live Deployment

**Try it now:** https://igiari.us

- **Frontend:** https://igiari.us (Cloudflare Pages; also https://igiari.pages.dev/)
- **Backend API:** https://igiari-backend.onrender.com (Render)

✅ **Status:** Phases 0–4 deployed. **Step 1 complete** (auth, credits, Stripe test mode) — see [MONETIZATION_ROLLOUT.md](docs/MONETIZATION_ROLLOUT.md). **Next:** Step 2 legal landing or Stripe live mode.

📖 **Docs:** [INTEGRATIONS.md](docs/INTEGRATIONS.md) · [STRIPE_SETUP.md](docs/STRIPE_SETUP.md) · [MONETIZATION_ROLLOUT.md](docs/MONETIZATION_ROLLOUT.md)

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env from .env.example and add your ANTHROPIC_API_KEY
cp .env.example .env
# Edit .env and add your API key

python server.py
```

Backend runs on `http://localhost:8000`

### Frontend

Static files live at the **repository root** (`index.html`, `app.js`, `styles.css`):

```bash
python -m http.server 8080
```

Open `http://localhost:8080` in your browser.

Click "Try an Example" to see it in action.

---

## Build Specification

This project was built following a complete specification designed for AI agents to execute autonomously.

**Start here for current work:** [`specs/11_monetization_rollout_plan.md`](specs/11_monetization_rollout_plan.md)

For the original MVP build (complete), see [`specs/04_build_phases.md`](specs/04_build_phases.md).

## Why this spec exists

Built as a demand-testing MVP first; now moving to a paid launch experiment. See [`docs/MONETIZATION_ROLLOUT.md`](docs/MONETIZATION_ROLLOUT.md) for the phased plan. Resist building beyond the current step's scope; park ideas in `specs/08_future_ideas.md`.

## Build Progress

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 0** | ✅ Complete | Setup: repo structure, taxonomy files, .env.example |
| **Phase 1** | ✅ Complete | Backend: FastAPI + Anthropic API + rate limiting |
| **Phase 2** | ✅ Complete | Quality validation script (`backend/run_eval.py`) |
| **Phase 3** | ✅ Complete | Frontend: Vanilla HTML/CSS/JS, copyeditor aesthetic |
| **Phase 4** | ✅ Complete | Deployment: Backend (Render) + Frontend (Cloudflare Pages) |
| **Phase 5** | ⏳ In progress | Soft launch + analytics + signal collection — [Step 0 checklist](docs/STEP0_LAUNCH_READINESS.md) |
| **Monetization** | ✅ Step 1 (test) | Stripe test mode live; Step 2 next — [MONETIZATION_ROLLOUT.md](docs/MONETIZATION_ROLLOUT.md) |

## Project structure

```
igiari/
├── index.html, app.js, auth.js, styles.css   # static site (repo root)
├── site-config.js                            # Supabase + analytics config
├── legal/                                    # privacy, terms
├── backend/                                  # FastAPI + billing
├── supabase/                                 # migrations, email templates
├── specs/                                    # build specifications
├── docs/                                     # deployment & runbooks
└── source-materials/                         # original taxonomy + eval
```

See [specs/README.md](specs/README.md) and [docs/README.md](docs/README.md) for full indexes.

| File | Purpose |
|---|---|
| `specs/00_master_spec.md` | Entry point, scope summary, file structure |
| `specs/01_product_requirements.md` | Functional requirements, explicit in/out of scope |
| `specs/02_design_direction.md` | Visual identity guidance |
| `specs/03_architecture.md` | Stack, hosting, model choice, cost controls — concrete decisions |
| `specs/04_build_phases.md` | **The task list** — sequenced phases with acceptance criteria |
| `specs/05_api_contract.md` | Exact frontend/backend request-response schema |
| `specs/06_testing_and_launch_checklist.md` | Pre-launch verification |
| `specs/07_monetization_notes.md` | MVP deferral rationale; ads rejected |
| `specs/08_future_ideas.md` | Parking lot — explicitly not in scope yet |
| `specs/09_legal_positioning_and_pricing..md` | Legal beachhead positioning and pricing |
| `specs/10_monetization.md` | Full monetization architecture and Stripe/pricing design |
| `specs/11_monetization_rollout_plan.md` | **Phased execution plan — current work** |
| `docs/MONETIZATION_ROLLOUT.md` | Human-readable rollout tracker |
| `docs/INTEGRATIONS.md` | Supabase, Resend, Render, Cloudflare dashboards |
| `docs/STEP0_LAUNCH_READINESS.md` | Step 0 checklist (analytics, live tests, spend cap) |
| `specs/README.md` | Spec folder index |

## Prerequisite materials

This spec assumes access to a prior project's outputs (a fallacy-detection taxonomy and eval set). If you don't have these files, ask before proceeding — see `specs/00_master_spec.md`'s "Source materials" section for the exact list of files needed.
