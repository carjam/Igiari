# Auth & Email — Recovery Runbook

Use this document to recreate sign-in, email delivery, and the custom domain if anything is reset or rebuilt.

**Integration quick reference (all dashboards + URLs):** [INTEGRATIONS.md](INTEGRATIONS.md)  
**Secrets:** store only in provider dashboards — never commit to git.

**Production (June 2026):**

| Service | URL |
|---------|-----|
| Site (primary) | https://igiari.us |
| Site (Pages default) | https://igiari.pages.dev |
| Backend API | https://igiari-backend.onrender.com |
| Supabase | https://yvkrihgjcoyqytwoisgw.supabase.co |
| Supabase dashboard | https://supabase.com/dashboard/project/yvkrihgjcoyqytwoisgw |
| Resend | https://resend.com/domains |
| Render service | https://dashboard.render.com/ → **igiari-backend** |
| Cloudflare Pages | https://dash.cloudflare.com/ → Workers & Pages → **igiari** |

---

## 1. Supabase (database + auth)

**Dashboard:** https://supabase.com/dashboard/project/yvkrihgjcoyqytwoisgw

### 1.1 Create project (if starting fresh)

1. https://supabase.com/dashboard → New project
2. Settings: **Data API** On · **Automatically expose new tables** Off · **Automatic RLS** On
3. Copy keys from https://supabase.com/dashboard/project/_/settings/api-keys (publishable + secret)

### 1.2 Database schema

Run in **SQL Editor** (in order):

1. `supabase/migrations/20250620200000_initial_billing_schema.sql`
2. `supabase/migrations/20250620210000_grant_billing_api_access.sql` (required when auto-expose is off)

Confirm **Table Editor** shows `accounts` and `credit_transactions`.

### 1.3 Auth provider

https://supabase.com/dashboard/project/yvkrihgjcoyqytwoisgw/auth/providers → **Email** enabled.

### 1.4 URL configuration

https://supabase.com/dashboard/project/yvkrihgjcoyqytwoisgw/auth/url-configuration

| Setting | Value |
|---------|--------|
| **Site URL** | `https://igiari.us` |
| **Redirect URLs** | `https://igiari.us/**` |
| (optional backup) | `https://igiari.pages.dev/**` |

### 1.5 Custom SMTP (Resend)

https://supabase.com/dashboard/project/yvkrihgjcoyqytwoisgw/auth/smtp → Enable custom SMTP:

| Field | Value |
|-------|--------|
| Sender email | `noreply@igiari.us` |
| Sender name | `Igiari` |
| Host | `smtp.resend.com` |
| Port | `587` |
| Username | `resend` |
| Password | Resend API key from https://resend.com/api-keys |

Rate limits: https://supabase.com/dashboard/project/yvkrihgjcoyqytwoisgw/auth/rate-limits (raise **Email sent** after SMTP is on).

### 1.6 Magic Link email template

https://supabase.com/dashboard/project/yvkrihgjcoyqytwoisgw/auth/templates → **Magic Link**

`supabase/email-templates/magic-link.html`

**Do not use `{{ .ConfirmationURL }}` alone** — breaks on static Pages; mail clients may prefetch and burn the token.

Paste from:

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

| | |
|---|---|
| Dashboard | https://resend.com/home |
| Domains | https://resend.com/domains |
| API keys | https://resend.com/api-keys |

Resend sends mail **through Supabase SMTP** (not from app code).

### 2.1 API key

Create key (**Sending access**) → use as Supabase SMTP **Password**.

### 2.2 Domain

1. **Domains → Add Domain** → `igiari.us`
2. **Auto configure** → connect Cloudflare → verify until status **Verified**
3. Sending address: `noreply@igiari.us` (any local-part on verified domain works)

Free tier limits apply (~100 emails/day); sufficient for early launch.

---

## 3. Cloudflare (site + domain igiari.us)

| | |
|---|---|
| Dashboard | https://dash.cloudflare.com/ |
| Pages | Workers & Pages → **igiari** |
| DNS zone | Websites → **igiari.us** |

### 3.1 Domain

Registered via Cloudflare Registrar; DNS in same account.

### 3.2 Pages custom domain

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

## 4. Render (backend API)

| | |
|---|---|
| Dashboard | https://dashboard.render.com/ |
| Service | **igiari-backend** |
| Live URL | https://igiari-backend.onrender.com |
| Repo config | `render.yaml`, `backend/` |

Environment tab — required variables:

| Variable | Value |
|----------|--------|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com/settings/keys |
| `SUPABASE_URL` | `https://yvkrihgjcoyqytwoisgw.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase secret key |
| `SUPABASE_ANON_KEY` | Supabase publishable key |

Billing fails without all three Supabase vars. See also [INTEGRATIONS.md](INTEGRATIONS.md#render-backend-api).

### 4.1 Auth behavior (code)

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
| `docs/INTEGRATIONS.md` | All services — dashboards, env vars, URLs |

---

**Last updated:** June 2026
