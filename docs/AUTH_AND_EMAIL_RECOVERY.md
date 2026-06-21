# Auth & Email — Recovery Runbook

Use this document to recreate sign-in, email delivery, and the custom domain if Supabase, Resend, Cloudflare, or Render are reset or rebuilt. Secrets live in each provider’s dashboard — **do not commit API keys or SMTP passwords to git**.

**Production URLs (June 2026):**

| Service | URL |
|---------|-----|
| Site (primary) | https://igiari.us |
| Site (Pages default) | https://igiari.pages.dev |
| Backend API | https://igiari-backend.onrender.com |
| Supabase project | https://yvkrihgjcoyqytwoisgw.supabase.co |

---

## 1. Supabase project (database + auth)

### 1.1 Create project

1. [supabase.com/dashboard](https://supabase.com/dashboard) → New project
2. Recommended settings at creation:
   - **Enable Data API:** On
   - **Automatically expose new tables:** Off (grant manually — see migrations)
   - **Enable automatic RLS:** On
3. Note **Project URL** and keys under **Project Settings → API Keys** (publishable + secret)

### 1.2 Database schema

Run in **SQL Editor** (in order):

1. `supabase/migrations/20250620200000_initial_billing_schema.sql`
2. `supabase/migrations/20250620210000_grant_billing_api_access.sql` (required when auto-expose is off)

Confirm **Table Editor** shows `accounts` and `credit_transactions`.

### 1.3 Auth provider

**Authentication → Providers → Email:** enabled (magic link / OTP).

### 1.4 URL configuration

**Authentication → URL Configuration:**

| Setting | Value |
|---------|--------|
| **Site URL** | `https://igiari.us` |
| **Redirect URLs** | `https://igiari.us/**` |
| (optional backup) | `https://igiari.pages.dev/**` |

### 1.5 Custom SMTP (Resend)

**Authentication → SMTP Settings** → Enable custom SMTP:

| Field | Value |
|-------|--------|
| Sender email | `noreply@igiari.us` |
| Sender name | `Igiari` |
| Host | `smtp.resend.com` |
| Port | `587` |
| Username | `resend` |
| Password | Resend API key (`re_...`) from [resend.com/api-keys](https://resend.com/api-keys) |

After SMTP is enabled, raise **Authentication → Rate Limits → Email sent** if needed (default ~30/hour with custom SMTP).

### 1.6 Magic Link email template

**Do not use `{{ .ConfirmationURL }}` alone** on this static site. It uses Supabase PKCE redirects that break on Cloudflare Pages, and mail clients may prefetch the link and burn the one-time token.

**Authentication → Email Templates → Magic Link** — paste the full body from:

`supabase/email-templates/magic-link.html`

Contents (keep in sync with that file):

```html
<h2>Sign in to Igiari</h2>
<p><a href="{{ .RedirectTo }}?token_hash={{ .TokenHash }}&type=email">Sign in to Igiari</a></p>
<p>Or enter this code on the site: {{ .Token }}</p>
<p>This link and code expire in 1 hour and work once only.</p>
```

**How sign-in works on the site:**

- Link lands on `https://igiari.us/?token_hash=...&type=email` → `auth.js` calls `verifyOtp({ token_hash, type: 'email' })`
- User can instead enter the **6-digit `{{ .Token }}`** → **Verify code** on the site
- Each link/code is **one-time**; if the link is prefetched or clicked first, request a **new** email and use the code only

---

## 2. Resend (transactional email)

### 2.1 Account & API key

1. [resend.com](https://resend.com) → sign up
2. **API Keys** → Create → **Sending access** → copy `re_...` (used as Supabase SMTP password)

### 2.2 Domain

1. **Domains → Add Domain** → `igiari.us`
2. **Auto configure** → connect Cloudflare → verify until status **Verified**
3. Sending address: `noreply@igiari.us` (any local-part on verified domain works)

Free tier limits apply (~100 emails/day); sufficient for early launch.

---

## 3. Custom domain (igiari.us)

### 3.1 Register

Registered via **Cloudflare Registrar** (5-year term). Zone DNS is managed in the same Cloudflare account.

### 3.2 Cloudflare Pages

**Workers & Pages → igiari → Custom domains:**

| Hostname | Points to |
|----------|-----------|
| `igiari.us` | `igiari.pages.dev` (CNAME, proxied) |

If **Complete DNS setup** shows a blank CNAME target, use **`igiari.pages.dev`**.

Production branch: **`master`** (repo root = site root, no build command).

### 3.3 Frontend Supabase config

File: `site-config.js` (publishable key only — safe in git):

```javascript
window.IGIARI_SUPABASE_URL = 'https://yvkrihgjcoyqytwoisgw.supabase.co';
window.IGIARI_SUPABASE_ANON_KEY = 'sb_publishable_...'; // Project Settings → API Keys
```

---

## 4. Render backend

Service: **igiari-backend** — [dashboard.render.com](https://dashboard.render.com/)

### 4.1 Required environment variables

| Variable | Value |
|----------|--------|
| `ANTHROPIC_API_KEY` | From Anthropic Console |
| `SUPABASE_URL` | `https://yvkrihgjcoyqytwoisgw.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase secret key (`sb_secret_...`) |
| `SUPABASE_ANON_KEY` | Supabase publishable key (`sb_publishable_...`) — used to verify user JWTs |

Billing/account endpoints fail without all three Supabase vars.

### 4.2 Auth behavior (code)

- **Signed-in scans:** require Bearer token; debit credits after successful scan
- **Anonymous scans:** disabled when billing env is configured
- See `backend/billing.py`, `backend/server.py`, `auth.js`

---

## 5. Verification checklist

After rebuild, test in order:

1. [ ] https://igiari.us loads the scanner
2. [ ] Sign-in email arrives **from** `noreply@igiari.us`
3. [ ] **6-digit code** → **Verify code** → shows scan balance
4. [ ] Reload page → still signed in (session persisted)
5. [ ] Scan debits balance; sign-out works

---

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|----------------|-----|
| Balance unavailable after sign-in | DB tables not exposed to Data API | Run `20250620210000_grant_billing_api_access.sql` |
| Email rate limit (2/hour) | Still on Supabase default SMTP | Enable Resend SMTP (§1.5) |
| Link + code both fail | Old token consumed or wrong template | New email; use code **without** clicking link; fix template (§1.6) |
| Link fails, code works | Expected with prefetch / PKCE | Prefer code; template uses `token_hash` not `ConfirmationURL` |
| Magic link PKCE error | Opened link in different browser than request | Same browser, or use code |
| Template edit blocked | No custom SMTP | Complete §1.5 + §2 first |

---

## 7. Related repo files

| Path | Purpose |
|------|---------|
| `supabase/email-templates/magic-link.html` | Copy-paste Magic Link template |
| `supabase/migrations/` | Database schema + API grants |
| `auth.js` | Magic link `token_hash`, OTP verify, session restore |
| `site-config.js` | Supabase URL + publishable key |
| `specs/10_monetization.md` | Credits, pricing, data model |
| `specs/11_monetization_rollout_plan.md` | Step 1–3 rollout order |

---

**Last updated:** June 2026
