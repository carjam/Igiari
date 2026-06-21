# Stripe Go-Live Checklist

**Purpose:** Prepare real-money billing without flipping production until you choose to.  
**Current state:** Sandbox (`sk_test_...`) on Render — keep it until the final step below.

Related: [STRIPE_SETUP.md](STRIPE_SETUP.md) (sandbox) · [INTEGRATIONS.md](INTEGRATIONS.md)

---

## Phase A — Prepare in Stripe (no Render changes)

Do these in Stripe **live** mode (exit sandbox). Nothing here charges customers until Phase C.

### A1. Account readiness

- [ ] Stripe account fully activated (identity, bank account verified)
- [ ] Payouts enabled (or know expected delay)
- [ ] [Customer portal](https://dashboard.stripe.com/settings/billing/portal) enabled for **live**

### A2. Live products — consumer

Create in [Product catalog](https://dashboard.stripe.com/products) (**live**, not sandbox):

| Product | Type | Price | Save as |
|---------|------|-------|---------|
| Igiari Starter | One-time | $8 | `STRIPE_PRICE_STARTER_PACK` (live `price_...`) |
| Igiari Casual | Recurring monthly | $9 | `STRIPE_PRICE_CASUAL_SUB` (live `price_...`) |

### A3. Live products — legal (for `/legal` outreach)

| Product | Type | Price | Save as |
|---------|------|-------|---------|
| Objection Legal Starter | One-time | $29 | `STRIPE_PRICE_LEGAL_STARTER` |
| Objection Legal Solo | Recurring monthly | $39 | `STRIPE_PRICE_LEGAL_SOLO_SUB` |

Store live price IDs in a password manager — **do not** put them on Render yet.

### A4. Live webhook

1. [Developers → Webhooks / Event destinations](https://dashboard.stripe.com/webhooks) (**live**)
2. URL: `https://igiari-backend.onrender.com/api/webhooks/stripe`
3. Events: `checkout.session.completed`, `invoice.paid`, `invoice.payment_failed`, `customer.subscription.deleted`
4. Save **live** signing secret (`whsec_...`) — not on Render yet

---

## Phase B — Code ready (done in repo)

- [x] Consumer + legal product catalogs in `backend/stripe_billing.py`
- [x] Legal signup tagging (`?surface=legal`, `X-Igiari-Surface: legal`)
- [x] Interim consumer pricing fallback until legal price env vars are set
- [x] Webhook idempotency verified in sandbox
- [x] `/legal` landing page

**Optional before go-live:** Add legal price env vars in **sandbox** on Render and test a $29 legal Starter purchase + replay.

---

## Phase C — Flip Render to live (only when ready)

**Warning:** After this, Checkout charges real cards. Use a small self-test first.

Update **igiari-backend → Environment** (mark secrets as Secret):

| Variable | Change to |
|----------|-----------|
| `STRIPE_SECRET_KEY` | `sk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | Live `whsec_...` |
| `STRIPE_PRICE_STARTER_PACK` | Live consumer Starter `price_...` |
| `STRIPE_PRICE_CASUAL_SUB` | Live consumer Casual `price_...` |
| `STRIPE_PRICE_LEGAL_STARTER` | Live legal Starter `price_...` (when outreach starts) |
| `STRIPE_PRICE_LEGAL_SOLO_SUB` | Live legal Solo `price_...` (when outreach starts) |

Keep `SITE_URL=https://igiari.us`. Save → wait for redeploy.

---

## Phase D — Verify live (real money)

1. Sign in on https://igiari.us
2. Buy **Starter** with your real card (or smallest pack)
3. Confirm credits increase
4. Stripe **live** dashboard → webhook **200**
5. Resend webhook → balance unchanged (idempotency)
6. Optional refund test purchase in Stripe Dashboard

---

## Phase E — Outreach (Step 2)

Only after Phase D:

- [ ] `/legal` pricing matches live legal products (env vars set)
- [ ] First targeted outreach (PI / family-law communities)
- [ ] Support email ready for billing questions (`legal/terms.html` contact)

---

## Rollback

If something breaks after Phase C:

1. Revert Render `STRIPE_*` to **sandbox** values → redeploy (real charges stop)
2. Or disable Checkout by clearing `STRIPE_SECRET_KEY` temporarily (payments off; scans still work for existing credits)

---

**Last updated:** June 2026
