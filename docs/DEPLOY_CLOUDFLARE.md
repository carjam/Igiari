# Cloudflare Pages Deployment

**Live site:** https://igiari.us · https://igiari.pages.dev  
**Backend API:** https://igiari-backend.onrender.com (configured in `app.js` / `auth.js`)

Full integration reference: **[INTEGRATIONS.md](INTEGRATIONS.md)**

---

## Dashboard

| | |
|---|---|
| **Cloudflare** | https://dash.cloudflare.com/ |
| **Pages project** | Workers & Pages → **igiari** |
| **Domain zone** | Websites → **igiari.us** |

---

## Quick Setup

1. Cloudflare Dashboard → Workers & Pages → Create → **Pages**
2. Connect GitHub repo: `carjam/Igiari`
3. Configure:
   - **Project name:** `igiari`
   - **Build command:** (empty)
   - **Output directory:** `/` (repo root)
   - **Branch:** `master`
4. Save and Deploy

Frontend files (`index.html`, `app.js`, `auth.js`, `site-config.js`, `styles.css`) are at repo root — no build step.

---

## Custom domain

Pages → **igiari** → Custom domains → add `igiari.us`:

- CNAME → `igiari.pages.dev` (proxied)
- Supabase **Site URL** must match: `https://igiari.us` ([Auth URL config](https://supabase.com/dashboard/project/yvkrihgjcoyqytwoisgw/auth/url-configuration))

---

## Frontend config

| File | Purpose |
|------|---------|
| `site-config.js` | Supabase URL + publishable key |
| `app.js` | Scan UI, API base → Render |
| `auth.js` | Magic link / OTP sign-in |

No Cloudflare env vars — secrets live in `site-config.js` (publishable key only) and Render (backend).

---

## Redeploy

Push to `master` → auto-deploy. Manual: Deployments → **Retry deployment** on latest build.
