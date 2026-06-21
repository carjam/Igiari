# Igiari! — Monetization Build Spec (current)

This is the single, current spec for adding payment to the live Igiari! fallacy scanner. It supersedes any older monetization drafts in this repo — this file is authoritative for **what** to build (architecture, pricing, data model).

**How to build it:** Do **not** implement everything here at once. Follow the phased rollout in `11_monetization_rollout_plan.md` — consumer billing MVP first, legal landing second, developer API third. Step 0 (launch readiness) must complete before Step 1.

## What exists today (June 2026)

Live fallacy scanner at **https://igiari.us** (Cloudflare Pages) with backend on Render. Claude Haiku 4.5, IP rate limiting, response caching.

**Step 1 shipped (test mode):** Supabase auth, credit ledger, sign-in required to scan, Stripe Checkout (Starter + Casual), webhooks with idempotent credit grants, buy UI + Billing Portal. **Next:** Step 2 legal landing, then Stripe live mode when ready to charge real money.

**Do not rebuild the scan pipeline — extend it.**

## What we're building now

Three paid surfaces sharing one backend and one credit ledger:

1. **Consumer web tool** (existing site, gets accounts + billing added) — for debate coaches, law students, individual writers who use the browser UI directly.
2. **Developer API** (new surface at `/developers`) — for writers/journalists/toolmakers integrating fallacy detection into their own agentic pipelines (Claude Code workflows, editorial tools, custom agents).
3. **Legal** (new surface at `/legal`) — for solo/small-firm personal injury and family law practitioners reviewing demand letters, declarations, and correspondence for reasoning quality. Same product and backend as (1), distinct landing page, copy, and pricing tier — see Section 4 for why legal pricing sits well above consumer pricing, and `LEGAL_POSITIONING_AND_PRICING.md` for the full positioning rationale.

All three are metered by a shared credit balance per account. All three get a free trial before any payment is required.

## Explicitly out of scope right now

Team/multi-seat billing, annual subscription discounts, non-USD pricing, a marketing site redesign, enterprise sales/invoicing, SDKs/client libraries, an interactive API playground, self-serve refunds, scan history/dashboards, multiple API keys per account, usage webhooks. If a good idea outside this list comes up while building, note it in a `FUTURE_IDEAS.md` and keep moving — don't build it now.

---

## 1. Data model

New tables (first time this project needs a real database — use Postgres):

```
accounts
  id (uuid), email, account_type ("consumer"|"developer"|"legal"),
  credit_balance (int), free_trial_granted (bool),
  stripe_customer_id (nullable), subscription_status ("none"|"active"|"canceled"),
  created_at

api_keys
  id (uuid), account_id (fk), key_hash, key_prefix,
  created_at, revoked_at (nullable)

credit_transactions
  id (uuid), account_id (fk), delta (int),
  reason ("trial_grant"|"pack_purchase"|"subscription_renewal"|"scan_usage"|"refund"|"admin_adjustment"),
  stripe_event_id (nullable, used for webhook idempotency),
  created_at
```

`credit_balance` is a cache of `SUM(delta)` from `credit_transactions` — always write a transaction row, never just mutate the balance directly. This is what lets you reconstruct disputes and safely handle duplicate Stripe webhooks.

**Debit timing**: debit credit only *after* a scan succeeds, never before calling the Claude API. A failed/errored scan must not cost the user a credit. A cache hit (identical input already seen) must not cost a credit either.

**Auth**: magic-link email login via a managed provider (Clerk or Supabase Auth — don't hand-roll this). Same auth system across all three surfaces; `account_type` just records which front door they signed up through. API keys (developer surface only): generate randomly, store only the hash, show the full key once at creation, display only a short prefix afterward — same UX as Anthropic's own Console key creation.

---

## 2. Endpoints

**Existing (modify):** `/api/scan` — add credit-balance check before calling Claude, debit-after-success, keep existing anonymous/IP-rate-limited path for non-logged-in visitors untouched (small free taste, e.g. 3-5 scans, no account needed).

**New:**
```
POST /v1/scan                          (API-key authenticated, developer surface)
Authorization: Bearer igk_live_xxxx
{ "text": "..." }

→ 200 { "input_length": int, "findings": [...], "credits_remaining": int }
→ 402 INSUFFICIENT_CREDIT   (balance is 0 — message points to purchase page)
→ 401 INVALID_API_KEY
→ 429 RATE_LIMITED          (per-account limit, e.g. 60/hour, independent of credit balance)
```

`findings` schema matches the existing validated scan response shape — reuse it, don't invent a new one.

```
POST /api/webhooks/stripe              (Stripe webhook receiver)
```
Verify Stripe's signature on every payload before trusting it. Handle: `checkout.session.completed` (grant credits / activate subscription), `invoice.paid` (renewal — grant next period's credits), `invoice.payment_failed` (flag account, stop future grants until resolved), `customer.subscription.deleted` (mark canceled, let already-granted current-period credits remain usable).

**Idempotency is required**: before processing any webhook event, check whether a `credit_transactions` row already exists with that event's `stripe_event_id`. If yes, return success without granting credit again — Stripe redelivers events, and a naive handler will double-grant.

---

## 3. Stripe setup

Use **Stripe Checkout** (hosted payment page) — not a custom payment form, not raw card handling. Two modes: `mode: "payment"` for one-time packs, `mode: "subscription"` for the consumer monthly plan. Use Stripe's hosted **Billing Portal** for subscription management/cancellation — don't build that UI yourself.

Build and fully test in **Stripe test mode** (test card `4242 4242 4242 4242`) before switching to live keys. Refunds: handle manually via Stripe Dashboard for now; if you issue one, manually add a matching negative `credit_transactions` row (`reason: "refund"`) to keep the ledger honest.

---

## 4. Pricing (current numbers — treat as decisions)

### Cost basis

- Claude Haiku 4.5 API cost: **~$0.01/scan** (≈8,000 input tokens + ≈400 output tokens, at $1/$5 per MTok — reverify these rates against current Anthropic pricing before launch, they can change).
- Stripe fees: 2.9% + $0.30/transaction, amortized into pack pricing below.
- **Fixed monthly hosting cost: target $8–15/month** — pick a cheap always-on backend compute tier (~$7/mo, avoids cold-start delays that a free/sleeping tier would add) plus free-tier Postgres and free-tier auth (Clerk/Supabase free tiers cover early volume). Don't default to pricier tiers without a reason; it directly hurts margin at low volume (see below).

### Why margin looks different at low volume vs. high volume

Hosting cost is fixed per month, not per scan — its per-scan share shrinks as volume grows. Concretely, true cost per scan (API + hosting):

| Monthly scan volume | True cost/scan | Note |
|---|---|---|
| ~100/mo | $0.09–0.16 | Hosting cost can rival or exceed the API cost. Developer-tier pricing (below) may be at/below true cost here. |
| ~1,000/mo | $0.018–0.025 | Consumer margins healthy; developer margins thin but positive. |
| ~5,000/mo | $0.012–0.013 | Matches the steady-state numbers below closely. |
| 20,000+/mo | ~$0.010–0.011 | Hosting cost per scan is negligible; full margin below applies. |

**Expect thin or even slightly negative true margin in the first weeks**, especially on developer packs, while volume is low. This is normal — don't panic-reprice off early numbers. Revisit pricing only if margins are still thin once past ~1,000–2,000 scans/month.

### Free trial (all surfaces)

**5 free scans on signup, no card required.** Real cost exposure: ~$0.05/signup; ~$50 worst case at 1,000 zero-converting signups — small, and already bounded by the existing Anthropic Console spend cap.

### Consumer pricing (debate coaches, law students, writers — web UI)

Offer both; let the buyer pick (bursty tournament-prep users want a pack, steady users want a subscription):

| Type | Option | Price | Scans |
|---|---|---|---|
| One-time pack | Starter | $8 | 50 |
| One-time pack | Standard | $20 | 100 |
| One-time pack | Bulk | $45 | 250 |
| Subscription | Casual | $9/mo | 60 included |
| Subscription | Regular | $15/mo | 150 included |

No rollover of unused subscription scans for now (use-it-or-lose-it per billing period).

### Developer/API pricing (agentic-tool integration)

Prepaid packs only for now, no subscription tier yet — usage patterns for a brand-new integration are unpredictable:

| Pack | Price | Scans |
|---|---|---|
| Dev Starter | $20 | 250 |
| Dev Growth | $75 | 1,000 |
| Dev Scale | $300 | 5,000 |

Priced lower per-scan than consumer tiers deliberately — this buyer can see your underlying API cost and is implicitly comparing against building it themselves. The taxonomy, calibration tuning, and maintained eval set are what's actually being sold; price to reflect that value-add, not as an opaque markup.

### Legal pricing (PI and family law solos/small firms)

Priced well above the consumer and developer tiers — not because the underlying cost is higher, but because this buyer's stakes-per-scan are much higher (a caught reasoning gap can affect a real settlement number or court filing), and the comparison set (LegesGPT at $19.99/mo, NexLaw's flat-rate solo pricing) confirms solos pay real money for a narrow tool well below the $225–1,000+/seat enterprise legal-AI platforms (Harvey, CoCounsel, GC AI):

| Type | Option | Price | Scans |
|---|---|---|---|
| One-time pack | Starter | $29 | 25 |
| One-time pack | Standard | $79 | 100 |
| One-time pack | Practice | $199 | 300 |
| Subscription | Solo | $39/mo | 50 included |
| Subscription | Practice | $99/mo | 200 included |

These sit at roughly 92–95% gross margin over true cost (vs. 80–91% for consumer/developer tiers) — appropriate, since this price reflects outcome stakes, not a cost multiple. Lead beachhead is PI (the pain — a weak causation argument an adjuster will exploit — is already named in the market's own language); family law rides alongside as a secondary example using the identical product and pricing, not a fork. Full positioning rationale, landing-page notes, and language to use/avoid: see `LEGAL_POSITIONING_AND_PRICING.md`.

### Rate limiting still applies to paid accounts

Independent of credit balance — e.g. 60 scans/hour even for paid accounts — to prevent a compromised key or runaway script from draining a balance unexpectedly fast.

---

## 5. UX notes

**Consumer flow**: anonymous visitors keep their small no-account taste of the tool (unchanged). Hitting that limit prompts account creation → 5 free trial credits granted automatically on signup. Hitting 0 credits shows pricing inline (pack + subscription side by side, no forced default) instead of attempting a failed scan. Minimal account dashboard: balance, subscription status, link to Stripe's Billing Portal. Keep existing product voice — plain, dry, no countdown timers or fake urgency badges; this audience will trust the tool more for restraint here, not less.

**Developer flow**: distinct `/developers` page with a real copy-pasteable request/response example and pricing in API terms (not consumer subscription language). Sign up → key generated and shown once → 5 free trial credits, no card required. A single static `/docs` page covering auth, the request/response shape, every error code, and rate limits is sufficient — no interactive API explorer needed yet.

**Legal flow**: distinct `/legal` page, reusing the existing scan UI and credit system — not a forked product. Lead copy: "check whether the argument actually holds up," not "AI-powered legal assistant" (that phrasing reads as indistinguishable from the drafting/case-management tools this audience already has, and actively hurts differentiation) and not "logical fallacy detector" as the primary hook (correct but reads as academic jargon to a practicing attorney — use "fallacy" as supporting detail once they're already engaged, not as the headline). Default "try an example" on this page should be a realistic PI demand-letter excerpt with a weak causation claim (anonymized/synthetic, never a real client's text), not the debate/political example used on the consumer page. State plainly what the tool doesn't do (no case law database, no citation validation, not a substitute for attorney judgment) — this audience is primed by bar-association guidance to distrust AI overclaiming, and explicit limits read as more credible, not less.

---

## 6. Build order

1. Database + account model
2. Auth (all surfaces) + trial credit grant on signup
3. Credit-gated scanning (debit-after-success, cache exception, anonymous path untouched)
4. Stripe integration, fully tested in test mode for every tier, including a duplicate-webhook idempotency check
5. Consumer billing UI (pricing page, dashboard, Stripe Billing Portal link)
6. Developer API surface (`/v1/scan`, key management, `/docs`)
7. Legal landing page (`/legal`) — reuses the existing scan UI and Stripe/credit plumbing from steps 3–5; this step is primarily copy, a legal-specific pricing display, and the PI/family-law example scan, not new backend mechanics
8. Switch Stripe to live mode, re-verify the Anthropic Console spend cap is still sized appropriately for paid traffic, soft-launch directly to PI/family-law solo communities, debate/law communities, and developer-tool communities before any broad push

Each step should work end-to-end in test mode before moving to the next. Don't parallelize steps 2–4; the API surface in step 6 and the legal page in step 7 can both be built alongside step 5 once step 4 is solid.
