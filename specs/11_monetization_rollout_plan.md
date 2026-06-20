# 11 — Monetization Rollout Plan

**Status:** Active — this is the execution plan for turning the live free tool into a paid product.

**Supersedes:** The "defer all monetization" guidance in `07_monetization_notes.md` for *when* to build billing. That document still applies for *what not to do* (especially ads). The full target architecture lives in `10_monetization.md`; **this file defines the order and scope of each increment** so we ship revenue capability without building all three surfaces at once.

If you are an agent picking this up cold: read `10_monetization.md` for the end-state design, then execute the steps below in order.

---

## Current state (baseline)

| Layer | Status |
|---|---|
| Core scan product | ✅ Live at https://igiari.pages.dev/ |
| Backend (`/api/scan`) | ✅ Rate limiting, caching, Haiku 4.5 |
| Accounts / billing | ❌ Not built |
| Analytics | ⏳ Step 0 (in progress) |

Phases 0–4 from `04_build_phases.md` are complete. Phase 5 (soft launch + signal collection) overlaps with Step 0 below and should be finished before or in parallel with monetization engineering — not skipped entirely.

---

## Guiding principles

1. **One revenue surface at a time.** Consumer web first; legal landing second; developer API third.
2. **Don't rebuild what works.** Extend `/api/scan`, caching, rate limiting, and the existing UI — see `10_monetization.md` § "What exists today."
3. **No ads.** Still rejected — see `07_monetization_notes.md`.
4. **Test mode before live mode.** Every Stripe and auth integration must work end-to-end in test mode before switching keys.
5. **Revenue follows outreach, not vice versa.** Code enables charging; communities (PI solos, debate/law, developers) drive first sales.

---

## Step 0 — Launch readiness (1–2 days)

**Goal:** Baseline visibility and safety before adding billing or promotion.

**Tasks:**
- Enable privacy-preserving analytics (Cloudflare Web Analytics beacon on `index.html`, or confirm Cloudflare Pages dashboard analytics is sufficient — see `docs/STEP0_LAUNCH_READINESS.md`).
- Complete `06_testing_and_launch_checklist.md` against the **live** deployment (not localhost).
- Set an Anthropic API spend cap / budget alert in the Anthropic Console (backstop below app-level rate limiting).
- Update `legal/privacy.html` when analytics is enabled.

**Acceptance criteria:**
- [ ] Analytics recording page views (beacon or dashboard confirmed).
- [ ] Live smoke test passes (example scan, true-negative, rate limit, mobile layout).
- [ ] Anthropic spend alert configured.
- [ ] Privacy policy reflects analytics if a beacon is added.

**Do not start Step 1 until Step 0 acceptance criteria are met** (or explicitly waived by the owner with documented reason).

---

## Step 1 — Monetization MVP: consumer web only (~1 week)

**Goal:** A logged-in user can buy credits and scan without building developer API or legal landing yet.

**Build order** (subset of `10_monetization.md` §6):

| # | Work item | Notes |
|---|---|---|
| 1 | Postgres + ledger tables | Supabase free tier recommended (DB + auth in one) |
| 2 | Magic-link auth + `account_type: "consumer"` | 20 trial credits on signup, no card |
| 3 | Credit-gated `/api/scan` | Debit after success only; cache hits free; anonymous path unchanged (consider tightening to 3–5 scans before signup prompt) |
| 4 | Stripe Checkout (test mode) | Start with **one pack + one subscription** (e.g. Starter $8 / Casual $9/mo) |
| 5 | Minimal account UI | Balance, buy credits, Stripe Billing Portal link |

**Explicitly defer:** `/developers`, `/v1/scan`, `/legal`, multiple pack tiers, subscription complexity beyond one plan each.

**Optional shortcut for first dollars:** Stripe Payment Link + manual credit grant while webhook idempotency is still in test — not spec-pure, acceptable for validating willingness to pay with ≤5 early customers.

**Acceptance criteria:**
- [ ] New user signs up → receives 20 trial credits.
- [ ] Successful scan debits 1 credit; failed scan and cache hit do not.
- [ ] Anonymous visitor path still works within IP rate limit.
- [ ] Test-mode Checkout grants credits via webhook; duplicate webhook does not double-grant.
- [ ] User with 0 credits sees pricing inline, not a failed scan.

---

## Step 2 — First revenue channel (~1 week after Step 1)

**Goal:** First paying customers from a deliberate beachhead, not broad promotion.

**Recommended priority:** Legal landing (`/legal`) — highest $/scan, positioning already written in `09_legal_positioning_and_pricing..md`.

| Surface | Effort | When |
|---|---|---|
| `/legal` landing + PI example | ~1 day (copy + example text; reuses Step 1 billing) | **First outreach target** |
| Consumer (debate/law student forums) | Minimal extra code | Parallel if easy |
| Developer API (`/developers`, `/v1/scan`, `/docs`) | ~2–3 days backend | Only after someone asks or consumer/legal stalls |

**Outreach (cheap, targeted):** PI/family-law solo communities, debate/law-student forums — not broad legal-tech press.

**First-month revenue target (realistic):** 5–10 paying users (~$150–400), not passive income.

---

## Step 3 — Expand after first paying users

Only after Step 2 shows at least one paying customer (or strong trial-to-paid signal):

- Remaining pack tiers and subscription plans from `10_monetization.md` §4.
- Developer API surface if requested.
- Eval/precision improvements if legal users report false positives (current eval: ~45% precision, ~89% true-negative accuracy — adequate for consumer; set expectations carefully for legal).
- Stripe live mode + soft launch to wider audiences.

---

## Document map

| File | Role |
|---|---|
| `10_monetization.md` | End-state architecture, data model, pricing, Stripe rules |
| `09_legal_positioning_and_pricing..md` | Legal beachhead copy and pricing rationale |
| `07_monetization_notes.md` | Historical deferral rationale; **ads still rejected** |
| `11_monetization_rollout_plan.md` | **This file — execution order and scope per step** |
| `docs/MONETIZATION_ROLLOUT.md` | Human-readable summary and checklist tracker |
| `docs/STEP0_LAUNCH_READINESS.md` | Step 0 task checklist |

---

## What "done" looks like for the first business experiment

Not: passive income, all three surfaces live, enterprise features.

Yes: live billing on consumer web, legal landing live, Anthropic costs covered by revenue, documented learnings about who pays and why.
