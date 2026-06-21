# Monetization Rollout — Summary & Tracker

This is the human-readable companion to [`specs/11_monetization_rollout_plan.md`](../specs/11_monetization_rollout_plan.md). Full architecture and pricing numbers live in [`specs/10_monetization.md`](../specs/10_monetization.md).

## The plan in one paragraph

The free tool is built and live. We finish launch readiness (analytics, live smoke tests, spend caps), then add **consumer billing only** (auth, credits, Stripe) before building the legal landing or developer API. Legal outreach is the best first revenue bet; developer API comes last. No ads, no three-surface parallel build.

---

## Progress tracker

### Step 0 — Launch readiness

See [`STEP0_LAUNCH_READINESS.md`](STEP0_LAUNCH_READINESS.md) for the full checklist.

| Task | Status |
|---|---|
| Analytics enabled (Cloudflare Web Analytics beacon or Pages dashboard) | ⏳ Beacon wired; paste token in `site-config.js` |
| Live deployment smoke test (`06_testing_and_launch_checklist.md`) | ⏳ See automated checks below |
| Anthropic API spend cap / budget alert | ⏳ Manual — [Anthropic Console](https://console.anthropic.com/settings/limits) |
| Privacy policy updated for analytics (if beacon added) | ✅ Updated in `legal/privacy.html` |

### Step 1 — Consumer monetization MVP

| Task | Status |
|---|---|
| Postgres + credit ledger | ✅ Migrations in `supabase/migrations/` |
| Auth (magic link + OTP code) + 20 trial credits | ✅ See `docs/AUTH_AND_EMAIL_RECOVERY.md` |
| Sign-in required to scan (no anonymous path in prod) | ✅ |
| Custom domain + Resend SMTP | ✅ `igiari.us` |
| Stripe Checkout + webhooks (test mode) | ⬜ |
| Account UI (balance, buy, Billing Portal) | ⬜ |

### Step 2 — First revenue channel

| Task | Status |
|---|---|
| `/legal` landing page + PI example | ⬜ |
| Targeted outreach (PI / debate communities) | ⬜ |
| First paying customer | ⬜ |

### Step 3 — Expand

| Task | Status |
|---|---|
| Full pricing tiers from spec | ⬜ |
| Developer API (`/v1/scan`, `/docs`) | ⬜ |
| Stripe live mode | ⬜ |

---

## Economics (quick reference)

| Milestone | Rough target |
|---|---|
| Cover hosting (~$10/mo) | ~2 legal Starter packs ($29) or ~2 consumer Starter packs ($8) |
| Meaningful side income (~$200/mo) | ~7 legal Standard ($79) or ~25 consumer Standard ($20) |
| API cost per scan | ~$0.01 (Haiku); hosting dominates at low volume |

Early margins are thin at low scan volume — normal for the first weeks. Revisit pricing only after ~1,000–2,000 scans/month if margins stay thin.

---

## What we're not building (yet)

- Ads (credibility conflict — see `specs/07_monetization_notes.md`)
- Team billing, enterprise invoicing, SDKs, scan history
- All three paid surfaces in parallel

---

**Last updated:** June 2026
