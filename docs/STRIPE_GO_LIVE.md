# Stripe Go-Live Checklist

**Purpose:** Track Stripe live rollout for Igiari production billing.

Related: [STRIPE_SETUP.md](STRIPE_SETUP.md) (sandbox / local dev) · [LEGAL_BILLING_SETUP.md](LEGAL_BILLING_SETUP.md) · [INTEGRATIONS.md](INTEGRATIONS.md)

---

## Current production state (June 2026)

| Item | Status |
|------|--------|
| Render `STRIPE_SECRET_KEY` | ✅ Live (`sk_live_...`) |
| Render consumer price IDs | ✅ Live Starter + Casual |
| Render live webhook secret | ✅ Live `whsec_...` |
| Consumer checkout | ✅ Real charges on https://igiari.us |
| Legal price env vars on Render | ⬜ **Not set** — legal funnel uses interim consumer pricing |
| Legal live products in Stripe | ⬜ Optional until [LEGAL_BILLING_SETUP.md](LEGAL_BILLING_SETUP.md) |

**Sandbox** remains available for local development — production no longer uses test keys.

---

## Phase A — Prepare in Stripe (live dashboard) ✅

Completed in Stripe **live** mode (not sandbox).

### A1. Account readiness ✅

- [x] Stripe account activated
- [x] [Customer portal](https://dashboard.stripe.com/settings/billing/portal) enabled (live) — cancel, payment methods, invoices

### A2. Live products — consumer ✅

| Product | Type | Price | Render env var |
|---------|------|-------|----------------|
| Igiari Starter | One-time | $8 | `STRIPE_PRICE_STARTER_PACK` |
| Igiari Casual | Recurring monthly | $9 | `STRIPE_PRICE_CASUAL_SUB` |

### A3. Live products — legal ⬜

Not required for consumer go-live. Do before `/legal` outreach at target pricing:

| Product | Type | Price | Render env var |
|---------|------|-------|----------------|
| Objection Legal Starter | One-time | $29 | `STRIPE_PRICE_LEGAL_STARTER` |
| Objection Legal Solo | Recurring monthly | $39 | `STRIPE_PRICE_LEGAL_SOLO_SUB` |

See [LEGAL_BILLING_SETUP.md](LEGAL_BILLING_SETUP.md).

### A4. Live webhook ✅

- [x] URL: `https://igiari-backend.onrender.com/api/webhooks/stripe`
- [x] Events: `checkout.session.completed`, `invoice.paid`, `invoice.payment_failed`, `customer.subscription.deleted`
- [x] Live signing secret saved and on Render

**Note:** Stripe’s UI may use an event-first flow (select events → webhook destination). Choose **snapshot** payload if offered — the backend expects classic `event.data.object` webhooks.

---

## Phase B — Code ready ✅

- [x] Consumer + legal product catalogs in `backend/stripe_billing.py`
- [x] Legal signup tagging (`?surface=legal`, `X-Igiari-Surface: legal`)
- [x] Interim consumer pricing fallback when legal env vars unset
- [x] Webhook idempotency verified (sandbox)
- [x] `/legal` landing page

---

## Phase C — Flip Render to live ✅

Consumer billing on Render uses live keys and live consumer price IDs.

| Variable | Production |
|----------|------------|
| `STRIPE_SECRET_KEY` | `sk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Live `whsec_...` |
| `STRIPE_PRICE_STARTER_PACK` | Live Starter `price_...` |
| `STRIPE_PRICE_CASUAL_SUB` | Live Casual `price_...` |
| `STRIPE_PRICE_LEGAL_STARTER` | ⬜ Not set |
| `STRIPE_PRICE_LEGAL_SOLO_SUB` | ⬜ Not set |
| `SITE_URL` | `https://igiari.us` |

---

## Phase D — Verify live (real money)

Run once after Phase C (or re-run after any Stripe env change):

1. Sign in on https://igiari.us (new account → **5** trial scans)
2. Buy **Starter** ($8) with a real card
3. Confirm credits increase by **50**
4. Stripe **live** → Webhooks → delivery **200**
5. Resend `checkout.session.completed` → balance unchanged (idempotency)
6. Optional: refund test purchase in Stripe Dashboard

For **Casual** ($9/mo): subscribe → **60** credits on `invoice.paid`; test Billing Portal cancel.

---

## Phase E — Outreach (Step 2)

Before PI/family-law outreach at **legal** prices:

- [ ] Complete [LEGAL_BILLING_SETUP.md](LEGAL_BILLING_SETUP.md)
- [ ] Confirm `/legal?surface=legal` checkout shows Legal Starter / Legal Solo (not interim consumer packs)
- [ ] First targeted outreach
- [ ] Support email ready (`legal/terms.html` contact)

Consumer-only outreach (main site, debate forums) can proceed now — live Starter/Casual are active.

---

## Rollback

If something breaks:

1. Revert Render `STRIPE_*` to **sandbox** values → redeploy (real charges stop)
2. Or clear `STRIPE_SECRET_KEY` temporarily (payments off; existing credits still work)

---

**Last updated:** June 2026
