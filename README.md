# Igiari! (異議あり!)

**Objection!** — A logical fallacy scanner for text.

Paste an argument, email, article, or transcript and see logical fallacies highlighted inline with explanations. Think "Grammarly, but for bad reasoning instead of bad grammar."

🚧 **Status:** Phases 0-3 complete. Ready for local testing before deployment.

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

```bash
cd frontend
python -m http.server 8080
```

Open `http://localhost:8080` in your browser.

Click "Try an Example" to see it in action.

---

## Build Specification

This project was built following a complete specification designed for AI agents to execute autonomously.

**Start here:** [`specs/00_master_spec.md`](specs/00_master_spec.md)

Then work through `specs/04_build_phases.md` as the main task list, referring back to the other numbered documents as each phase requires.

## Why this spec exists

This is a deliberately small, demand-testing version of a larger idea (a browser extension / consumer product for fallacy detection). The goal of this specific build is to answer "will anyone actually use this" as cheaply as possible — see `specs/00_master_spec.md` and `specs/07_monetization_notes.md` for the full reasoning. Resist the urge to build beyond what's in `specs/01_product_requirements.md`'s MUST list; see `specs/08_future_ideas.md` for where to park good ideas that come up mid-build instead of implementing them early.

## Build Progress

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 0** | ✅ Complete | Setup: repo structure, taxonomy files, .env.example |
| **Phase 1** | ✅ Complete | Backend: FastAPI + Anthropic API + rate limiting |
| **Phase 2** | ✅ Complete | Quality validation script (`backend/run_eval.py`) |
| **Phase 3** | ✅ Complete | Frontend: Vanilla HTML/CSS/JS, copyeditor aesthetic |
| **Phase 4** | ⏳ Next | Deployment: Backend + frontend to production |
| **Phase 5** | ⏳ Pending | Soft launch + analytics + signal collection |

**Current blockers:**
- Need to test Phase 2 eval (requires ANTHROPIC_API_KEY in `backend/.env`)
- Need to choose hosting providers for Phase 4

## Document index

| File | Purpose |
|---|---|
| `specs/00_master_spec.md` | Entry point, scope summary, file structure |
| `specs/01_product_requirements.md` | Functional requirements, explicit in/out of scope |
| `specs/02_design_direction.md` | Visual identity guidance |
| `specs/03_architecture.md` | Stack, hosting, model choice, cost controls — concrete decisions |
| `specs/04_build_phases.md` | **The task list** — sequenced phases with acceptance criteria |
| `specs/05_api_contract.md` | Exact frontend/backend request-response schema |
| `specs/06_testing_and_launch_checklist.md` | Pre-launch verification |
| `specs/07_monetization_notes.md` | Why monetization (incl. ads) is deferred/rejected for this phase |
| `specs/08_future_ideas.md` | Parking lot — explicitly not in scope yet |

## Prerequisite materials

This spec assumes access to a prior project's outputs (a fallacy-detection taxonomy and eval set). If you don't have these files, ask before proceeding — see `specs/00_master_spec.md`'s "Source materials" section for the exact list of files needed.
