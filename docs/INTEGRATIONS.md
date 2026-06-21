# Integrations — Supabase, Resend, Render, Cloudflare, Anthropic

Concise reference for every external service Igiari uses. **Secrets stay in dashboards** — never commit SMTP passwords, secret keys, or API keys (except Supabase publishable key in `site-config.js`).

**Full disaster rebuild:** [AUTH_AND_EMAIL_RECOVERY.md](AUTH_AND_EMAIL_RECOVERY.md)

---

## At a glance

| Integration | Role | Production URL / ID |
|---------------|------|---------------------|
| **Cloudflare Pages** | Static site (HTML/JS/CSS) | https://igiari.us · https://igiari.pages.dev |
| **Render** | FastAPI backend (`/api/scan`, `/api/account/me`) | https://igiari-backend.onrender.com |
| **Supabase** | Postgres, auth, account/credit data | `yvkrihgjcoyqytwoisgw` · https://yvkrihgjcoyqytwoisgw.supabase.co |
| **Resend** | Sign-in email delivery (via Supabase SMTP) | From: `noreply@igiari.us` |
| **Anthropic** | Fallacy detection (Claude Haiku) | API only — no public URL |

**Data flow:** Browser → Cloudflare Pages → Render API → Anthropic; sign-in → Supabase Auth → email via Resend → credits in Supabase Postgres (Render uses service role).

---

## Cloudflare (site + domain)

| | |
|---|---|
| **Dashboard** | https://dash.cloudflare.com/ |
| **Pages project** | Workers & Pages → **igiari** |
| **Domain zone** | Websites → **igiari.us** |
| **Repo branch** | `master` · root `/` · no build command |

**Custom domain:** Pages → **igiari** → Custom domains → `igiari.us` CNAME → `igiari.pages.dev` (proxied). If CNAME target is blank, enter `igiari.pages.dev`.

**Frontend config:** `site-config.js` (Supabase publishable key), `auth.js`, `app.js` (API URL → Render).

**Deploy:** Push to `master` → auto-deploy. Manual: Deployments → Retry deployment.

---

## Render (backend API)

| | |
|---|---|
| **Dashboard** | https://dashboard.render.com/ |
| **Service name** | `igiari-backend` |
| **Live API** | https://igiari-backend.onrender.com |
| **Health** | `GET /` → `{"status":"ok"}` |
| **Config in repo** | `render.yaml`, `backend/Procfile`, `backend/requirements.txt`, `backend/runtime.txt` |

### Environment variables (Environment tab)

| Variable | Where to get it | Required for |
|----------|-----------------|--------------|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com/settings/keys | Scans |
| `SUPABASE_URL` | Supabase → Settings → API → Project URL | Accounts, credits |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Settings → API → Secret key | DB writes (backend only) |
| `SUPABASE_ANON_KEY` | Supabase → Settings → API → Publishable key | Verify user JWTs |

Missing any Supabase var → balance/sign-in API errors. Set spend cap: https://console.anthropic.com/settings/limits

**Deploy:** Push to `master` → auto-redeploy. Logs: service → **Logs**. Free tier cold-starts (~30s) after sleep.

**Optional later:** Custom domain `api.igiari.us` → Render Settings → Custom Domains.

---

## Supabase (database + auth)

| | |
|---|---|
| **Dashboard** | https://supabase.com/dashboard/project/yvkrihgjcoyqytwoisgw |
| **SQL Editor** | …/sql |
| **Table Editor** | …/editor |
| **API keys** | …/settings/api-keys |
| **Auth → URL config** | …/auth/url-configuration |
| **Auth → SMTP** | …/auth/smtp |
| **Auth → Email templates** | …/auth/templates |
| **Auth → Rate limits** | …/auth/rate-limits |
| **Auth → Providers** | …/auth/providers |

*(Replace path prefix with `/project/yvkrihgjcoyqytwoisgw` on any Supabase dashboard URL.)*

### Database

Run in **SQL Editor** (repo files):

1. `supabase/migrations/20250620200000_initial_billing_schema.sql` — `accounts`, `credit_transactions`, RLS
2. `supabase/migrations/20250620210000_grant_billing_api_access.sql` — Data API grants (if auto-expose tables was off)

Backend talks to Postgres via **REST + service role** (`backend/billing.py`), not Supabase client library.

### Auth

| Setting | Value |
|---------|--------|
| **Site URL** | `https://igiari.us` |
| **Redirect URLs** | `https://igiari.us/**` |
| **Email provider** | Enabled |
| **Sign-in on site** | Magic link (`token_hash`) + 6-digit code — see email template below |

**Frontend:** `site-config.js` — `IGIARI_SUPABASE_URL`, `IGIARI_SUPABASE_ANON_KEY`  
**Backend:** three `SUPABASE_*` env vars on Render (above)

### SMTP (Resend — configured inside Supabase)

| Field | Value |
|-------|--------|
| Sender | `noreply@igiari.us` · name `Igiari` |
| Host | `smtp.resend.com` |
| Port | `587` |
| Username | `resend` |
| Password | Resend API key (`re_...`) |

Do **not** use Supabase’s built-in email in production (2 emails/hour). Custom SMTP unlocks template editing.

### Magic Link email template

Paste from `supabase/email-templates/magic-link.html` into **Auth → Email templates → Magic Link**:

```html
<h2>Sign in to Igiari</h2>
<p><a href="{{ .RedirectTo }}?token_hash={{ .TokenHash }}&type=email">Sign in to Igiari</a></p>
<p>Or enter this code on the site: {{ .Token }}</p>
<p>This link and code expire in 1 hour and work once only.</p>
```

Do **not** rely on `{{ .ConfirmationURL }}` alone — breaks on static Pages + email prefetch.

---

## Resend (email sending)

| | |
|---|---|
| **Dashboard** | https://resend.com/home |
| **Domains** | https://resend.com/domains |
| **API keys** | https://resend.com/api-keys |
| **Docs (SMTP)** | https://resend.com/docs/send-with-smtp |

Resend does **not** send mail directly from our code — Supabase Auth sends via SMTP using the API key as password.

### Setup summary

1. Create API key (**Sending access**) → paste into Supabase SMTP password field.
2. Add domain **igiari.us** → **Auto configure** with Cloudflare → **Verified**.
3. Send from `noreply@igiari.us` (any `@igiari.us` address on verified domain).

**Limits:** Free tier ~100 emails/day (enough for early launch). Raises deliverability vs Supabase default mail.

---

## Anthropic (AI scans)

| | |
|---|---|
| **Console** | https://console.anthropic.com/ |
| **API keys** | https://console.anthropic.com/settings/keys |
| **Usage / limits** | https://console.anthropic.com/settings/limits |
| **Model in code** | `claude-haiku-4-5-20251001` (`backend/server.py`) |

Only Render holds `ANTHROPIC_API_KEY`. Set a monthly spend cap as a backstop below app rate limits.

---

## Quick verification

1. https://igiari.us — site loads  
2. Sign-in email from `noreply@igiari.us`  
3. 6-digit code or link → signed in, balance shown  
4. Reload — still signed in  
5. Scan debits credit  

**Troubleshooting:** [AUTH_AND_EMAIL_RECOVERY.md §6](AUTH_AND_EMAIL_RECOVERY.md#6-troubleshooting)

---

**Last updated:** June 2026
