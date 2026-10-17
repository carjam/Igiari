# Deployment Status

**Current Status:** ⏸️ **Archived (October 2026)**

Services have been paused to avoid ongoing hosting costs. All code is production-ready and fully functional.

## Why Archived?

This project was built as a demand-testing MVP and later evolved into a portfolio showcase. To demonstrate full-stack SaaS capabilities without ongoing expenses, the live deployment has been paused.

**What's preserved:**
- ✅ Complete source code (backend + frontend + database)
- ✅ All deployment configurations (`render.yaml`, migrations, etc.)
- ✅ Infrastructure documentation and runbooks
- ✅ Test suite and evaluation framework

## Quick Restart Guide

### Prerequisites

You'll need accounts/API keys for:
- [Anthropic](https://console.anthropic.com/) - For Claude API (fallacy detection)
- [Supabase](https://supabase.com/) - Database and authentication
- [Stripe](https://stripe.com/) - Payment processing (test or live mode)
- [Render](https://render.com/) - Backend hosting (or alternative)
- [Cloudflare](https://www.cloudflare.com/) - Frontend hosting (or alternative)
- [Resend](https://resend.com/) - Email delivery

### Backend (Render or Local)

**Option A: Deploy to Render**

1. Fork/clone this repo
2. Create Render web service from `render.yaml`
3. Set environment variables (see `backend/.env.example`):
   - `ANTHROPIC_API_KEY`
   - `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY`
   - `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
   - `STRIPE_PRICE_*` (product IDs from Stripe)
   - `SITE_URL` (your frontend URL)
4. Deploy triggers automatically on push to `master`

**Option B: Run Locally**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python server.py
```

Backend runs on `http://localhost:8000`

### Database (Supabase)

1. Create new Supabase project
2. Run migrations from `supabase/migrations/` in SQL Editor:
   - `20250620200000_initial_billing_schema.sql`
   - `20250620210000_grant_billing_api_access.sql`
3. Configure Auth:
   - Enable Email provider
   - Set Site URL and redirect URLs
   - Configure SMTP (Resend recommended)
   - Update magic link template from `supabase/email-templates/`
4. Copy Project URL and API keys to backend `.env`

**See:** [docs/SUPABASE.md](docs/SUPABASE.md) for detailed setup

### Stripe (Optional - for payments)

1. Create products in [Stripe Dashboard](https://dashboard.stripe.com/test/products)
2. Copy price IDs to backend environment variables
3. Create webhook endpoint pointing to `YOUR_BACKEND_URL/api/webhooks/stripe`
4. Select events: `checkout.session.completed`, `customer.subscription.*`
5. Copy webhook signing secret to `STRIPE_WEBHOOK_SECRET`

**See:** [docs/STRIPE_SETUP.md](docs/STRIPE_SETUP.md) for step-by-step guide

### Frontend (Cloudflare Pages or Local)

**Option A: Deploy to Cloudflare Pages**

1. Create Pages project connected to repo
2. Set build settings:
   - Build command: (none)
   - Build output directory: `/` (root)
   - Branch: `master`
3. Update `site-config.js` with your Supabase project details
4. Deploy

**See:** [docs/DEPLOY_CLOUDFLARE.md](docs/DEPLOY_CLOUDFLARE.md)

**Option B: Run Locally**

```bash
# In repo root (where index.html lives)
python -m http.server 8080
```

Open `http://localhost:8080` in your browser.

### Update API URL

**For production:** Update `app.js` line ~8 to point to your backend URL:
```javascript
const API_BASE = window.API_BASE || 'https://YOUR-BACKEND.onrender.com';
```

**For local dev:** `site-config.js` already handles localhost detection.

## Cost Estimates (if reactivated)

Based on light usage (~100 scans/day):

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| **Render** | Free (with cold starts) | $0 |
| **Render** | Starter (always-on) | $7 |
| **Supabase** | Free (2 projects, 500MB) | $0 |
| **Cloudflare Pages** | Free (unlimited) | $0 |
| **Anthropic API** | Pay-per-token | ~$5-20 |
| **Resend** | Free (100 emails/day) | $0 |
| **Stripe** | Transaction fees only | % of revenue |

**Minimum to run:** $5-20/month (mostly Anthropic API usage)  
**With guaranteed uptime:** ~$12-27/month (add Render Starter)

## Minimal Demo Mode

Want to run a free demo without ongoing costs?

1. **Frontend only** - Deploy to Cloudflare Pages, show UI/UX (no API calls)
2. **Localhost only** - Run backend locally when needed, no cloud costs
3. **Recorded demo** - Take screenshots/screen recording, embed in portfolio

## Full Documentation

- [docs/INTEGRATIONS.md](docs/INTEGRATIONS.md) - Complete service integration guide
- [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) - Deployment overview
- [docs/AUTH_AND_EMAIL_RECOVERY.md](docs/AUTH_AND_EMAIL_RECOVERY.md) - Auth setup deep-dive
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture and decisions

---

**Questions?** This project is maintained as a portfolio piece. For technical details or inquiries, see [github.com/carjam](https://github.com/carjam).
