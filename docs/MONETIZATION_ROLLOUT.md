# Monetization Rollout — Summary & Tracker

This is the human-readable companion to [`specs/11_monetization_rollout_plan.md`](../specs/11_monetization_rollout_plan.md). Full architecture and pricing numbers live in [`specs/10_monetization.md`](../specs/10_monetization.md).

## Current state (June 2026)

| Layer | Status |
|-------|--------|
| Consumer billing | ✅ **Stripe live** on Render — Starter ($8) + Casual ($9/mo) |
| Legal billing | ⬜ **Not configured** — `/legal` users checkout at interim consumer prices until `STRIPE_PRICE_LEGAL_*` is set |
| Free trial | ✅ **5 scans** on new signup |
| Sandbox | Still useful for local dev — see [STRIPE_SETUP.md](STRIPE_SETUP.md) |

Go-live history: [STRIPE_GO_LIVE.md](STRIPE_GO_LIVE.md) · Legal setup when ready: [LEGAL_BILLING_SETUP.md](LEGAL_BILLING_SETUP.md)

---

## The plan in one paragraph

The free tool is built and live. We finished launch readiness, added consumer billing, flipped Stripe to **live mode** for the main site, and shipped the `/legal` landing. **Legal-tier Stripe products are not on Render yet** — outreach should wait until those are configured, or accept interim $8/$9 checkout from the legal funnel. Developer API remains deferred.

---

## Progress tracker

### Step 0 — Launch readiness ✅

See [`STEP0_LAUNCH_READINESS.md`](STEP0_LAUNCH_READINESS.md) for the full checklist.

| Task | Status |
|---|---|
| Analytics enabled | ✅ Cloudflare Pages auto-inject (Web Analytics in dashboard) |
| Live deployment smoke test | ✅ [LIVE_SMOKE_TEST.md](LIVE_SMOKE_TEST.md) |
| Anthropic API spend cap / budget alert | ✅ Configured in [Anthropic Console](https://console.anthropic.com/settings/limits) |
| Privacy policy updated (accounts, analytics, subprocessors) | ✅ `legal/privacy.html`, `legal/terms.html` |

### Step 1 — Consumer monetization ✅ (live)

| Task | Status |
|---|---|
| Postgres + credit ledger | ✅ Migrations in `supabase/migrations/` |
| Auth (magic link + OTP code) + **5 trial credits** | ✅ [AUTH_AND_EMAIL_RECOVERY.md](AUTH_AND_EMAIL_RECOVERY.md) · [INTEGRATIONS.md](INTEGRATIONS.md) |
| Sign-in required to scan (no anonymous path in prod) | ✅ |
| Custom domain + Resend SMTP | ✅ `igiari.us` |
| Stripe Checkout + webhooks | ✅ Idempotency verified in sandbox; **production uses live keys** |
| Account UI (balance, buy, Billing Portal) | ✅ |
| Stripe live on Render (Phase C) | ✅ Consumer Starter + Casual live `price_...` |
| Live prep (dual catalog, legal surface tagging) | ✅ Code deployed — [STRIPE_GO_LIVE.md](STRIPE_GO_LIVE.md) |

**Verify if not done:** [STRIPE_GO_LIVE.md § Phase D](STRIPE_GO_LIVE.md#phase-d--verify-live-real-money) — one live $8 purchase, webhook 200, idempotency replay.

### Step 2 — First revenue channel ⏳

| Task | Status |
|---|---|
| `/legal` landing page + PI example | ✅ [legal/index.html](../legal/index.html) |
| **Legal Stripe products on Render** | ⬜ See [LEGAL_BILLING_SETUP.md](LEGAL_BILLING_SETUP.md) |
| Targeted outreach (PI / family-law communities) | ⬜ Block until legal pricing configured (recommended) |
| First paying customer | ⬜ |

**Interim behavior:** Users from `/legal?surface=legal` see consumer Starter/Casual at checkout ($8 / $9) until `STRIPE_PRICE_LEGAL_STARTER` and `STRIPE_PRICE_LEGAL_SOLO_SUB` are set on Render.

### Step 3 — Expand

| Task | Status |
|---|---|
| Full pricing tiers from spec (e.g. Standard $20 pack) | ⬜ |
| Developer API (`/v1/scan`, `/docs`) | ⬜ |
| Broader promotion beyond beachhead outreach | ⬜ After Step 2 signal |

---

## Economics (quick reference)

| Milestone | Rough target |
|---|---|
| Cover hosting (~$10/mo) | ~2 Starter packs ($8) or ~2 legal Starter packs ($29) |
| Meaningful side income (~$200/mo) | ~7 legal Standard ($79) or ~25 consumer Standard ($20) |
| API cost per scan | ~$0.01 (Haiku); hosting dominates at low volume |

Early margins are thin at low scan volume — normal for the first weeks. Revisit pricing only after ~1,000–2,000 scans/month if margins stay thin.

---

## What we're not building (yet)

- Ads (credibility conflict — see `specs/07_monetization_notes.md`)
- Team billing, enterprise invoicing, SDKs, scan history
- All three paid surfaces in parallel
- Full legal pricing table ($79 / $199 packs) — only Legal Starter + Solo wired in code today

---

**Last updated:** June 2026 (consumer Stripe live; legal billing not configured)
