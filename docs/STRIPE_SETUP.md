# Stripe Setup

Stripe configuration for Igiari billing. Code: `backend/stripe_billing.py`.

---

## Production (live) — current

**https://igiari.us** uses **Stripe live mode** on Render:

| Product | Price | Render env var |
|---------|-------|----------------|
| Igiari Starter | $8 one-time (50 scans) | `STRIPE_PRICE_STARTER_PACK` |
| Igiari Casual | $9/mo (60 scans/mo) | `STRIPE_PRICE_CASUAL_SUB` |

Also on Render: `STRIPE_SECRET_KEY` (`sk_live_...`), `STRIPE_WEBHOOK_SECRET` (live `whsec_...`), `SITE_URL=https://igiari.us`.

**Legal billing is not configured** — see [LEGAL_BILLING_SETUP.md](LEGAL_BILLING_SETUP.md).

Go-live checklist and history: [STRIPE_GO_LIVE.md](STRIPE_GO_LIVE.md).

**Live dashboard:** https://dashboard.stripe.com/dashboard

---

## Sandbox (local dev & testing)

Use Stripe **test mode** for local `.env` and sandbox purchases. Do not point production Render at test keys.

**Test dashboard:** https://dashboard.stripe.com/test/dashboard

### 1. API keys

1. [Developers → API keys](https://dashboard.stripe.com/test/apikeys) → copy **Secret key** (`sk_test_...`)
2. Local `backend/.env` → `STRIPE_SECRET_KEY`

### 2. Products and prices

Create in [Product catalog](https://dashboard.stripe.com/test/products) (test mode):

| Product | Type | Price | Env var |
|---------|------|-------|---------|
| Igiari Starter | One-time | $8.00 USD | `STRIPE_PRICE_STARTER_PACK` = `price_...` |
| Igiari Casual | Recurring monthly | $9.00 USD | `STRIPE_PRICE_CASUAL_SUB` = `price_...` |

Optional legal sandbox products: `STRIPE_PRICE_LEGAL_STARTER`, `STRIPE_PRICE_LEGAL_SOLO_SUB` — see [LEGAL_BILLING_SETUP.md](LEGAL_BILLING_SETUP.md).

Copy each **Price ID** (`price_...`), not the Product ID.

### 3. Webhook (local)

**Production endpoint (live):** `https://igiari-backend.onrender.com/api/webhooks/stripe`

For local dev with Stripe CLI:

```bash
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

Use the CLI’s `whsec_...` in local `.env`.

Events: `checkout.session.completed`, `invoice.paid`, `invoice.payment_failed`, `customer.subscription.deleted`.

### 4. Billing Portal

[Settings → Billing → Customer portal](https://dashboard.stripe.com/settings/billing/portal) — enable in **live** for production; test mode for sandbox experiments.

### 5. Test card (sandbox only)

| Field | Value |
|-------|--------|
| Number | `4242 4242 4242 4242` |
| Expiry | Any future date |
| CVC | Any 3 digits |

**Verify in sandbox:**

1. Sign in → use **5** trial credits (or fresh account)
2. Buy Starter → balance +50
3. Resend `checkout.session.completed` → credits do **not** double

---

## Render environment (reference)

| Variable | Production | Local dev |
|----------|------------|-----------|
| `STRIPE_SECRET_KEY` | `sk_live_...` | `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | Live `whsec_...` | CLI or test `whsec_...` |
| `STRIPE_PRICE_STARTER_PACK` | Live `price_...` | Test `price_...` |
| `STRIPE_PRICE_CASUAL_SUB` | Live `price_...` | Test `price_...` |
| `STRIPE_PRICE_LEGAL_STARTER` | ⬜ Not set | Optional test `price_...` |
| `STRIPE_PRICE_LEGAL_SOLO_SUB` | ⬜ Not set | Optional test `price_...` |
| `SITE_URL` | `https://igiari.us` | `http://localhost:8080` |

See also [INTEGRATIONS.md](INTEGRATIONS.md) · [DEPLOY_RENDER.md](DEPLOY_RENDER.md).

---

**Last updated:** June 2026
