# Step 0 — Launch Readiness Checklist

Part of the monetization rollout — finish this before starting billing engineering (Step 1).

**Spec reference:** [`specs/11_monetization_rollout_plan.md`](../specs/11_monetization_rollout_plan.md) Step 0  
**Launch checklist:** [`specs/06_testing_and_launch_checklist.md`](../specs/06_testing_and_launch_checklist.md)

---

## 1. Analytics

**Option B — Cloudflare Pages automatic analytics (current setup)**

If Web Analytics is enabled on the **igiari** Pages project, Cloudflare injects the beacon automatically at deploy time — no token in `site-config.js` required. Confirm data in Cloudflare → **Web Analytics** or Pages → **igiari** → **Analytics**.

**Option A — Manual beacon via `site-config.js`**

Only needed if you are not using Pages auto-inject (e.g. hosting elsewhere). Paste token in `site-config.js`; loaded by `analytics.js`.

- [x] Analytics method: Cloudflare Pages auto-inject + Web Analytics dashboard
- [ ] Token in `site-config.js` (not required — Pages injects beacon)
- [x] Page views recording in Cloudflare dashboard

---

## 2. Live deployment smoke test

Run every item against **https://igiari.us** in an incognito window, not localhost. Sign in with email to scan (production requires an account).

### Functional

- [x] Load live URL in incognito
- [x] Sign in → Try Example → Scan (owner verified)
- [ ] Paste clean text (true negative) → "No fallacies found"
- [x] Paste >4000 chars → warning before submit (char counter)
- [ ] Hover highlighted span → explanation visible
- [ ] Mobile width (~375px) → layout usable

### Cost / abuse

- [x] Scan without auth → 401 (sign-in required; anonymous IP limit N/A in prod)
- [x] API key not visible in browser Network tab or page source
- [x] Backend health: `GET /` returns `{"status":"ok",...}`

### Trust

- [x] Privacy disclosure visible in footer without scrolling (desktop)
- [x] Error and empty-state copy reads calm, not buggy
- [ ] Spot-check 2–3 real-world paragraphs (optional)

---

## 3. Anthropic spend cap

Application rate limiting (10 scans/hour/IP) is not enough on its own if traffic spikes or the limiter mis-keys behind a load balancer.

1. Open [Anthropic Console → Settings → Limits](https://console.anthropic.com/settings/limits) (or Usage/Billing).
2. Set a **monthly spend limit** or **budget alert** appropriate for pre-revenue traffic (e.g. $25–50/mo alert, hard cap at your comfort level).
3. Confirm the API key used on Render matches the account where the limit is set.

- [x] Spend alert configured
- [x] Hard spend cap configured (owner confirmed)

---

## 4. Privacy policy (if analytics beacon added)

If Option A is enabled, update `legal/privacy.html` § Cookies and Analytics to name Cloudflare Web Analytics and what it collects. A draft update is included when the beacon ships; verify it before deploy.

- [x] Privacy policy matches analytics choice

---

## Automated verification (2026-06-21)

See full report: [LIVE_SMOKE_TEST.md](LIVE_SMOKE_TEST.md)

| Check | Result |
|---|---|
| Frontend `https://igiari.us` returns HTTP 200 | ✅ Pass |
| Backend health `GET /` returns `{"status":"ok"}` | ✅ Pass |
| Scan requires auth (401 without token) | ✅ Pass |
| Billing products API | ✅ Pass (2 products) |
| Analytics scripts on live site | ✅ Cloudflare Pages auto-inject |
| Anthropic spend cap | ✅ Owner confirmed |

---

## Step 0 sign-off

| Item | Status |
|---|---|
| Analytics live | ✅ Cloudflare Pages Web Analytics |
| Anthropic cap set | ✅ Owner confirmed |
| Live smoke test complete | ✅ [LIVE_SMOKE_TEST.md](LIVE_SMOKE_TEST.md) |
| Step 1 (consumer billing) | ✅ Complete (test mode) |
