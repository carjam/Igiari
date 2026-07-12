# Deployment Management Guide

Quick reference for managing your live Igiari deployment.

## 🌐 Live URLs

- **Frontend (primary):** https://igiari.us
- **Frontend (Pages default):** https://igiari.pages.dev/
- **Backend API (Public):** https://igiari-backend.onrender.com
- **Backend Health Check:** https://igiari-backend.onrender.com/ (returns `{"status":"ok","service":"fallacy-scanner-api"}`)
- **API Endpoint:** https://igiari-backend.onrender.com/api/scan

Auth, email, and domain recovery: **[AUTH_AND_EMAIL_RECOVERY.md](AUTH_AND_EMAIL_RECOVERY.md)**  
All integrations (Supabase, Resend, Render, Cloudflare): **[INTEGRATIONS.md](INTEGRATIONS.md)**

## 🎛️ Dashboard Access

| Service | Dashboard | Notes |
|---------|-----------|--------|
| **Render** | https://dashboard.render.com/ | Service: `igiari-backend` |
| **Cloudflare Pages** | https://dash.cloudflare.com/ → Workers & Pages → **igiari** | Custom domain: `igiari.us` |
| **Supabase** | https://supabase.com/dashboard/project/yvkrihgjcoyqytwoisgw | DB, auth, SMTP, email templates |
| **Resend** | https://resend.com/domains | Domain `igiari.us`; API key → Supabase SMTP |
| **Anthropic** | https://console.anthropic.com/settings/keys | `ANTHROPIC_API_KEY` on Render |

Details per service: **[INTEGRATIONS.md](INTEGRATIONS.md)**

## 📁 Configuration Files

### Backend Configuration

**File:** `render.yaml` (repository root)
- Defines service type, build commands, and environment variables
- Render auto-detects this file and uses it for deployment
- Any changes pushed to GitHub will trigger a redeploy

**File:** `backend/runtime.txt`
- Specifies Python version: `python-3.11.9`
- Critical: Don't upgrade to 3.13+ (causes maturin/Rust build errors)

**File:** `backend/requirements.txt`
- Python dependencies
- Uses `--only-binary=:all:` flag in build to prevent source compilation
- Key dependencies: FastAPI, Anthropic, Pydantic

**File:** `backend/Procfile`
- Defines how to start the service: `web: uvicorn server:app --host 0.0.0.0 --port $PORT`

### Frontend Configuration

**Files:** `index.html`, `app.js`, `styles.css` (repository root)
- Pure static files, no build process needed
- Cloudflare Pages serves these directly

**File:** `app.js` (Line 2)
- Contains API URL: `const API_URL = 'https://igiari-backend.onrender.com/api/scan';`
- Change this if you move the backend

## 🔄 How to Update & Redeploy

### Backend Changes

1. Make code changes in `backend/` directory
2. Test locally: `cd backend && uvicorn server:app --reload`
3. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your change description"
   git push
   ```
4. Render automatically detects the push and redeploys
5. Monitor deployment in Render dashboard → "Logs" tab

**Manual Redeploy:**
- Go to Render dashboard → Your service → "Manual Deploy" → "Deploy latest commit"

### Frontend Changes

1. Make changes to `index.html`, `app.js`, or `styles.css`
2. Test locally: `python -m http.server 8080` and visit http://localhost:8080
3. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your change description"
   git push
   ```
4. Cloudflare Pages automatically detects the push and redeploys
5. Monitor deployment in Cloudflare dashboard → Your project → "Deployments" tab

**Manual Redeploy:**
- Go to Cloudflare dashboard → Your project → "Deployments" → Click "Retry deployment" on any previous deploy

## 🔐 Environment Variables

### Backend (Render)

**Required:**
- `ANTHROPIC_API_KEY` — https://console.anthropic.com/settings/keys
- `SUPABASE_URL` — `https://yvkrihgjcoyqytwoisgw.supabase.co`
- `SUPABASE_SERVICE_ROLE_KEY` — Supabase → Settings → API → Secret key
- `SUPABASE_ANON_KEY` — Supabase → Settings → API → Publishable key

Without the three Supabase vars, sign-in works but balance/scans fail. See [INTEGRATIONS.md](INTEGRATIONS.md#render-backend-api).

**Optional (observability):**
- `SENTRY_DSN` — enables error tracking; unset means Sentry is fully inert (see § Error Tracking below)
- `SENTRY_ENVIRONMENT` — defaults to `ENVIRONMENT` or `"production"`
- `SENTRY_TRACES_SAMPLE_RATE` — defaults to `0`
- `LOG_LEVEL` — defaults to `INFO`

**How to update:** Render → **igiari-backend** → Environment → Save Changes (auto-redeploy).

### Frontend (Cloudflare Pages)

No Cloudflare env vars. Supabase publishable key in `site-config.js`; API URL in `app.js` / `auth.js` → Render.

### Supabase / Resend

Configured in Supabase dashboard (not Render). See [INTEGRATIONS.md](INTEGRATIONS.md#supabase-database--auth) and [INTEGRATIONS.md](INTEGRATIONS.md#resend-email-sending).

## 📊 Monitoring & Logs

### Backend Logs (Render)

1. Go to Render dashboard → Your service
2. Click "Logs" tab
3. View real-time logs (auto-refreshes)
4. Look for errors, API calls, rate limiting messages

Backend logs are structured JSON, one object per line (`logging_config.py`), so they're
directly filterable/greppable in the Render log view. Every log line includes `level`,
`logger`, `message`, and (when set) `request_id`. Set `LOG_LEVEL` (default `INFO`) to
change verbosity; `x-request-id` is echoed on every response and threads through to the
matching `scan_complete` telemetry line for correlation.

**What to watch for:**
- `HTTP 200` - Successful requests
- `HTTP 429` - Rate limit exceeded
- `HTTP 500` - Server errors
- Build failures - Usually Python dependency issues
- `"level":"ERROR"` - Application errors (Stripe, Anthropic, Supabase failures)

### Error Tracking (Sentry)

Set `SENTRY_DSN` on Render to enable Sentry error capture (unhandled exceptions, Stripe
errors, Anthropic API errors are all reported explicitly; see `error_tracking.py`). Without
`SENTRY_DSN` set, Sentry is fully inert — no calls are made. Optional: `SENTRY_ENVIRONMENT`
(defaults to `ENVIRONMENT` or `"production"`) and `SENTRY_TRACES_SAMPLE_RATE` (default `0`).

`/api/scan` requests with dropped spans or a JSON parse retry also emit a
`scan_quality_degraded` Sentry message (warning level) with the scan telemetry attached —
configure a Sentry alert rule on this message to catch prompt/model regressions in
production, closing the loop described in `docs/DETECTION_RELEASE_CHECKLIST.md`.

### Health Check

`GET /healthz` returns `{"status": "ok", "service": "fallacy-scanner-api", "taxonomy_loaded": true}`
with no auth and no external dependencies (billing/Anthropic). Point Render's health check
and any uptime monitor (e.g. UptimeRobot, Better Uptime) at this path.

### Frontend (Cloudflare Pages)

1. Go to Cloudflare dashboard → Your project
2. Click "Deployments" tab
3. View deployment status and build logs
4. Click any deployment to see detailed logs

**Analytics:**

Two options (see `docs/STEP0_LAUNCH_READINESS.md`):

1. **Cloudflare Web Analytics (recommended)** — privacy-preserving beacon. Token goes in `site-config.js`; loaded by `analytics.js`. Enable the site at dash.cloudflare.com → Web Analytics → Add site → `igiari.pages.dev`.
2. **Pages dashboard only** — Cloudflare → Workers & Pages → **igiari** → **Analytics** tab (page views, no code change).

After enabling the beacon, update `legal/privacy.html` § Cookies and Analytics.

## 🐛 Common Issues & Fixes

### Backend won't deploy - "maturin" or Rust errors

**Cause:** Python version too new (3.13+) or missing wheels

**Fix:**
1. Check `backend/runtime.txt` says `python-3.11.9`
2. Check `render.yaml` has `--only-binary=:all:` in build command
3. Check `backend/requirements.txt` uses `pydantic>=2.10` (not pinned to old version)

### Backend deployed but returns 500 errors

**Cause:** Missing `ANTHROPIC_API_KEY` or invalid key

**Fix:**
1. Go to Render dashboard → Environment
2. Check `ANTHROPIC_API_KEY` is set
3. Verify the key is valid at https://console.anthropic.com/

### Frontend shows old version

**Cause:** Browser cache or deployment in progress

**Fix:**
1. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. Check Cloudflare dashboard → Deployments to see if build is in progress
3. Try incognito/private window

### Frontend can't reach backend (CORS errors)

**Cause:** Backend not allowing requests from frontend domain

**Fix:**
1. Check `backend/server.py` has `allow_origins=["*"]` in CORS middleware
2. If you want stricter CORS, add your frontend URL: `allow_origins=["https://igiari.pages.dev"]`
3. Commit and push changes

### Render free tier puts service to sleep

**Issue:** First request after inactivity takes 30+ seconds

**Not really fixable on free tier, but you can:**
- Upgrade to paid tier ($7/month) for always-on service
- Add a status page that pings the API every 10 minutes (but Render may block this)
- Accept the cold start delay for low-traffic MVP

## 💰 Cost Management

### Current Setup (Free Tiers)

**Render Free:**
- 750 hours/month free compute
- Sleeps after 15 minutes of inactivity
- $0.02/hour if you exceed free tier (~$15/month max)

**Cloudflare Pages Free:**
- 500 builds/month
- Unlimited requests
- 20,000 files
- Free bandwidth

**Anthropic API:**
- Pay per token used
- Claude Haiku: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens
- Rate limited to 10 requests/hour per IP in your code

**Estimated monthly cost for low traffic:** $0-5

### Monitoring Costs

**Anthropic:**
- Dashboard: https://console.anthropic.com/settings/usage
- Set budget alerts in Anthropic dashboard
- **Required for Step 0:** Set a monthly spend limit or alert at https://console.anthropic.com/settings/limits — backstop below app rate limiting (see `docs/STEP0_LAUNCH_READINESS.md`)

**Render:**
- Dashboard shows usage hours
- Upgrade to $7/month paid tier if you exceed free hours

## 🔧 Making Configuration Changes

### Change Python Version

**Files to update:**
1. `backend/runtime.txt` - Change version number
2. `render.yaml` - No changes needed (uses runtime.txt)

**Recommendation:** Stay on Python 3.11.x for best package compatibility

### Change Backend URL

**If you move to different hosting:**

1. Update `app.js` line 2:
   ```javascript
   const API_URL = 'https://your-new-backend.com/api/scan';
   ```
2. Commit and push

### Add Environment Variables

**Backend:**
1. Edit `render.yaml` → add to `envVars` section:
   ```yaml
   - key: YOUR_VAR_NAME
     value: your-value  # or sync: false for manual entry
   ```
2. Commit and push
3. If using `sync: false`, set the value in Render dashboard → Environment

## 🚀 Custom Domains (Optional)

### Frontend (Cloudflare Pages)

1. Go to Cloudflare dashboard → Your project → "Custom domains"
2. Click "Set up a custom domain"
3. Enter your domain (must be managed by Cloudflare DNS)
4. Follow instructions to add DNS records
5. SSL is automatic

### Backend (Render)

1. Go to Render dashboard → Your service → "Settings" → "Custom Domain"
2. Add your domain
3. Add CNAME record in your DNS: `backend.yourdomain.com` → `your-service.onrender.com`
4. SSL is automatic

## 📚 Additional Resources

- **Render Docs:** https://docs.render.com/
- **Cloudflare Pages Docs:** https://developers.cloudflare.com/pages/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Anthropic API Docs:** https://docs.anthropic.com/

## 🆘 Quick Troubleshooting Checklist

If something's not working:

- [ ] Check Render dashboard → Logs for backend errors
- [ ] Check Cloudflare dashboard → Deployments for frontend build status
- [ ] Verify `ANTHROPIC_API_KEY` is set in Render
- [ ] Test backend directly: `curl https://igiari-backend.onrender.com/`
- [ ] Test API endpoint: `curl -X POST https://igiari-backend.onrender.com/api/scan -H "Content-Type: application/json" -d '{"text":"test"}'`
- [ ] Hard refresh frontend: Ctrl+Shift+R
- [ ] Check browser console (F12) for JavaScript errors
- [ ] Verify latest commit is deployed (check GitHub commit hash vs deployed version)

---

**Last Updated:** June 2026  
**Questions?** Check the deployment config files or reach out to Render/Cloudflare support.
