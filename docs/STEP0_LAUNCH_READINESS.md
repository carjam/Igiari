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

- [ ] Load live URL in incognito
- [ ] Click "Try an Example" → Scan → highlighted results within ~10s
- [ ] Paste clean text (true negative) → "No fallacies found" (not an error state)
- [ ] Paste >4000 chars → warning before submit
- [ ] Hover highlighted span → explanation visible
- [ ] Mobile width (~375px) → layout usable

### Cost / abuse

- [ ] 11th scan from same IP within an hour → rate limit message (test carefully; uses real API spend)
- [ ] API key not visible in browser Network tab or page source
- [ ] Backend health: `curl https://igiari-backend.onrender.com/` returns `{"status":"ok",...}`

### Trust

- [ ] Privacy disclosure visible in footer without scrolling (desktop)
- [ ] Error and empty-state copy reads calm, not buggy
- [ ] Spot-check 2–3 real-world paragraphs (news, email, social post)

---

## 3. Anthropic spend cap

Application rate limiting (10 scans/hour/IP) is not enough on its own if traffic spikes or the limiter mis-keys behind a load balancer.

1. Open [Anthropic Console → Settings → Limits](https://console.anthropic.com/settings/limits) (or Usage/Billing).
2. Set a **monthly spend limit** or **budget alert** appropriate for pre-revenue traffic (e.g. $25–50/mo alert, hard cap at your comfort level).
3. Confirm the API key used on Render matches the account where the limit is set.

- [ ] Spend alert configured
- [ ] Hard spend cap configured (optional but recommended): $________ / month

---

## 4. Privacy policy (if analytics beacon added)

If Option A is enabled, update `legal/privacy.html` § Cookies and Analytics to name Cloudflare Web Analytics and what it collects. A draft update is included when the beacon ships; verify it before deploy.

- [ ] Privacy policy matches analytics choice

---

## Automated verification (2026-06-20)

Run from CI or local shell against production:

| Check | Result |
|---|---|
| Frontend `https://igiari.us` returns HTTP 200 | ✅ Pass |
| Backend health `GET /` returns `{"status":"ok"}` | ✅ Pass |
| Live scan `POST /api/scan` returns findings JSON | ✅ Pass (Argumentum ad Populum on bandwagon test sentence) |
| Analytics scripts on live site | ✅ Cloudflare Pages auto-inject (Web Analytics) |
| Anthropic spend cap | ⏳ Manual — owner must set in Console |

---

## Step 0 sign-off

| Item | Owner | Date |
|---|---|---|
| Analytics live | | |
| Live smoke test complete | | |
| Anthropic cap set | | |
| Ready for Step 1 (consumer billing) | | |

When all boxes are checked, proceed to Step 1 in [`MONETIZATION_ROLLOUT.md`](MONETIZATION_ROLLOUT.md).
