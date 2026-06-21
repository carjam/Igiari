# Stripe Setup (Step 1 — test mode)

Consumer billing: **Starter pack** ($8 / 50 scans) and **Casual subscription** ($9/mo / 60 scans). Code lives in `backend/stripe_billing.py`.

**Dashboard:** https://dashboard.stripe.com/test/dashboard

---

## 1. API keys

1. [Developers → API keys](https://dashboard.stripe.com/test/apikeys) → copy **Secret key** (`sk_test_...`)
2. Render → **igiari-backend** → Environment → add `STRIPE_SECRET_KEY`

---

## 2. Products and prices

Create in [Product catalog](https://dashboard.stripe.com/test/products) (test mode):

| Product | Type | Price | Env var |
|---------|------|-------|---------|
| Igiari Starter | One-time | $8.00 USD | `STRIPE_PRICE_STARTER_PACK` = `price_...` |
| Igiari Casual | Recurring monthly | $9.00 USD | `STRIPE_PRICE_CASUAL_SUB` = `price_...` |

Copy each **Price ID** (starts with `price_`), not the Product ID.

---

## 3. Webhook

**Production endpoint:** `https://igiari-backend.onrender.com/api/webhooks/stripe`

1. [Developers → Webhooks](https://dashboard.stripe.com/test/webhooks) → Add endpoint
2. Events to send:
   - `checkout.session.completed`
   - `invoice.paid`
   - `invoice.payment_failed`
   - `customer.subscription.deleted`
3. Copy **Signing secret** (`whsec_...`) → Render env `STRIPE_WEBHOOK_SECRET`

**Local testing** (Stripe CLI):

```bash
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

Use the CLI’s `whsec_...` in local `.env`.

---

## 4. Billing Portal

1. [Settings → Billing → Customer portal](https://dashboard.stripe.com/test/settings/billing/portal)
2. Enable portal; allow subscription cancel
3. No code change — `/api/billing/portal` uses default portal config

---

## 5. Render environment

| Variable | Example |
|----------|---------|
| `STRIPE_SECRET_KEY` | `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` |
| `STRIPE_PRICE_STARTER_PACK` | `price_...` |
| `STRIPE_PRICE_CASUAL_SUB` | `price_...` |
| `SITE_URL` | `https://igiari.us` |

Redeploy after saving. Frontend reads products from `GET /api/billing/products` — no Stripe keys in the browser.

---

## 6. Test card

| Field | Value |
|-------|--------|
| Number | `4242 4242 4242 4242` |
| Expiry | Any future date |
| CVC | Any 3 digits |

**Verify:**

1. Sign in → use trial credits until 0 (or test with a fresh account)
2. Pricing panel appears → buy Starter → return to site → balance +50
3. Stripe Dashboard → Webhooks → resend `checkout.session.completed` → credits do **not** double (verified: balance unchanged on replay).

---

## 7. Go live

Do **not** flip Render to live keys until you have completed the checklist in [STRIPE_GO_LIVE.md](STRIPE_GO_LIVE.md) (create live products + webhook first, then Phase C env swap).

See also [INTEGRATIONS.md](INTEGRATIONS.md).
