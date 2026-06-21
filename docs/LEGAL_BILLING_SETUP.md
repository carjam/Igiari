# Legal Billing Setup

Enable **legal-tier checkout** ($29 Starter / $39 Solo) for users who sign up through `/legal?surface=legal`. Until this is done, the legal funnel falls back to **consumer** Starter ($8) and Casual ($9/mo) with an interim-pricing note in the UI.

**Consumer billing is already live** on Render. This doc is only for legal products.

Related: [STRIPE_GO_LIVE.md](STRIPE_GO_LIVE.md) · [specs/09_legal_positioning_and_pricing..md](../specs/09_legal_positioning_and_pricing..md)

---

## What the code expects

| Product key | Display | Price | Credits | Render env var |
|-------------|---------|-------|---------|----------------|
| `legal_starter` | Legal Starter | $29 one-time | 25 | `STRIPE_PRICE_LEGAL_STARTER` |
| `legal_solo_sub` | Legal Solo | $39/mo | 50/mo | `STRIPE_PRICE_LEGAL_SOLO_SUB` |

Defined in `backend/stripe_billing.py`. The `/legal` landing page lists additional tiers ($79, $199, etc.) — those are **not implemented** in checkout yet.

When both env vars are set, `GET /api/billing/products?surface=legal` returns legal products and `interim_consumer_pricing: false`.

---

## Step 1 — Create products in Stripe (live)

In Stripe **live** mode ([Product catalog](https://dashboard.stripe.com/products), confirm `pk_live_...` on [API keys](https://dashboard.stripe.com/apikeys)):

**Objection Legal Starter**
- One time · **$29.00 USD**
- Copy **Price ID** (`price_...`)

**Objection Legal Solo**
- Recurring · **Monthly** · **$39.00 USD**
- Copy **Price ID** (`price_...`)

Store IDs in a password manager — do not commit to git.

**Optional:** Create the same products in Stripe **test** mode first to run a $29 sandbox purchase before touching live.

---

## Step 2 — Add env vars on Render

**igiari-backend** → **Environment** → add (mark as Secret):

| Variable | Value |
|----------|-------|
| `STRIPE_PRICE_LEGAL_STARTER` | Live Legal Starter `price_...` |
| `STRIPE_PRICE_LEGAL_SOLO_SUB` | Live Legal Solo `price_...` |

Save → wait for redeploy. Consumer Stripe vars stay unchanged.

Also add to local `backend/.env` if testing legal checkout locally (use test price IDs with test keys).

---

## Step 3 — Verify

1. Open https://igiari.us/legal/ → **Open the scanner** (sets `?surface=legal`)
2. Sign in (or use account tagged legal)
3. Pricing panel should show **Legal Starter $29** and **Legal Solo $39/mo** — **not** the interim consumer note
4. Complete a test purchase (live or sandbox depending on keys)
5. Credits: +25 (Starter) or +50 on first invoice (Solo)
6. Stripe webhook **200**; resend event → balance unchanged

`GET /api/account/me` with header `X-Igiari-Surface: legal` should return `"legal_billing_ready": true`.

---

## Outreach checklist

Only after Step 3:

- [ ] `/legal` pricing table matches checkout ($29 / $39 — not $8 / $9)
- [ ] First outreach to PI / family-law communities
- [ ] Monitor webhook failures in Stripe live dashboard

---

**Last updated:** June 2026
