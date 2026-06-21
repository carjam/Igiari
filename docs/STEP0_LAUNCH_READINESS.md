# Step 0 — Launch Readiness Checklist

Part of the monetization rollout — finish this before starting billing engineering (Step 1).

**Spec reference:** [`specs/11_monetization_rollout_plan.md`](../specs/11_monetization_rollout_plan.md) Step 0  
**Launch checklist:** [`specs/06_testing_and_launch_checklist.md`](../specs/06_testing_and_launch_checklist.md)

---

## 1. Analytics

**Option A — Cloudflare Web Analytics beacon (recommended)**

Privacy-preserving, no cookies, fits the product voice. Requires a one-time dashboard setup plus a token in the repo.

1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/) → **Web Analytics** → **Add a site**.
2. Enter `igiari.us` (primary) or `igiari.pages.dev`.
3. Copy the **token** from the setup instructions.
4. Paste it in `site-config.js`:
   ```javascript
   window.IGIARI_CF_ANALYTICS_TOKEN = 'your-token-here';
   ```
5. Deploy (push to GitHub; Cloudflare Pages redeploys automatically).
6. Confirm events in Web Analytics within ~24 hours (can take a few minutes for first hit).

**Option B — Cloudflare Pages dashboard analytics only**

No code change. Go to Cloudflare → Workers & Pages → **igiari** → **Analytics**. Shows page views and bandwidth but not the same event detail as Web Analytics. Acceptable for Step 0 if you skip the beacon — check the box below and note "dashboard only" in the tracker.

- [ ] Analytics method chosen: _______________
- [ ] Token configured in `site-config.js` (if Option A)
- [ ] First page view recorded

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
| Analytics scripts on live site | ⏳ Pending deploy (wired in repo; token still empty in `site-config.js`) |
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
