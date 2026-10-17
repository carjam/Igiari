# Igiari! (異議あり!)

> 🎯 **Portfolio Project** - A production-ready SaaS application demonstrating full-stack development, LLM integration, and complete monetization architecture.
>
> **Skills showcased:** FastAPI · Anthropic Claude API · Stripe billing · Supabase auth · PostgreSQL RLS · Structured logging · Pytest · Vanilla JS

**Objection!** — A logical fallacy scanner for text.

Paste an argument, email, article, or transcript and see logical fallacies highlighted inline with explanations. Think "Grammarly, but for bad reasoning instead of bad grammar."

---

## 🏗️ Technical Highlights

- **LLM Integration** - Anthropic Claude API with structured output parsing and cost tracking
- **Complete Billing Stack** - Stripe checkout, subscriptions, idempotent webhooks, credit ledger
- **Authentication** - Magic link + OTP email auth with JWT verification and RLS policies
- **Production Observability** - Structured logging, Sentry error tracking, request correlation
- **Comprehensive Testing** - Unit tests, integration tests, and LLM output quality evaluation

👉 **[See ARCHITECTURE.md for technical deep-dive](ARCHITECTURE.md)**

## 📦 Deployment Status

**Currently archived (2026-10-16)** - Services paused to avoid ongoing costs. All code is production-ready and can be quickly reactivated. See deployment docs for setup instructions.

<details>
<summary>Previous live deployment details</summary>

- **Frontend:** https://igiari.us (Cloudflare Pages)
- **Backend API:** https://igiari-backend.onrender.com (Render)
- **Status:** Consumer billing fully implemented (Stripe Starter pack + Casual subscription)

</details>

📖 **Docs:** [ARCHITECTURE.md](ARCHITECTURE.md) · [docs/README.md](docs/README.md) · [specs/README.md](specs/README.md) · [CONVENTIONS.md](docs/CONVENTIONS.md)

---

## 📂 Repository Structure

```
igiari/
├── index.html, app.js, auth.js, styles.css    # Frontend (vanilla JS)
├── site-config.js                             # Frontend config
├── backend/                                   # FastAPI server
│   ├── server.py                              # API endpoints
│   ├── billing.py, stripe_billing.py          # Monetization logic
│   ├── tests/                                 # Comprehensive test suite
│   └── requirements.txt
├── supabase/                                  # Database migrations
│   ├── migrations/                            # SQL schema + RLS
│   └── email-templates/                       # Auth email templates
├── specs/                                     # Original build specifications
├── docs/                                      # Deployment runbooks
├── legal/                                     # Terms, privacy policy
├── ARCHITECTURE.md                            # 👈 Start here for technical overview
├── DEPLOYMENT_STATUS.md                       # How to restart services
└── LICENSE                                    # MIT
```

## 🚀 Quick Start

> **Note:** Services are currently paused. See [DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md) for activation instructions. For local development:

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

## 📋 Build Specifications

This project was built following a complete specification designed for AI-assisted development.

The [`specs/`](specs/) directory contains the original build plans, architecture decisions, and phased execution:
- [`specs/00_master_spec.md`](specs/00_master_spec.md) - Overview and scope
- [`specs/03_architecture.md`](specs/03_architecture.md) - Stack and design decisions
- [`specs/04_build_phases.md`](specs/04_build_phases.md) - Phased build plan (completed)
- [`specs/10_monetization.md`](specs/10_monetization.md) - Billing architecture

**Why specs matter:** Demonstrates ability to plan, document, and execute complex full-stack projects systematically.

## 📊 Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| **MVP Build** | ✅ Complete | All phases (0-5) finished |
| **Monetization** | ✅ Implemented | Stripe billing, subscriptions, webhooks |
| **Testing** | ✅ Complete | Unit + integration tests + LLM eval |
| **Deployment** | ⏸️ Archived | Ready to restart (see DEPLOYMENT_STATUS.md) |
| **Documentation** | ✅ Complete | Full specs, runbooks, and architecture docs |

See [docs/MONETIZATION_ROLLOUT.md](docs/MONETIZATION_ROLLOUT.md) for detailed implementation status.

---

## 📞 Contact

**Developer:** [carjam](https://github.com/carjam)

**Portfolio:** This project demonstrates production-ready full-stack SaaS development with modern tooling. See [ARCHITECTURE.md](ARCHITECTURE.md) for technical deep-dive.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
