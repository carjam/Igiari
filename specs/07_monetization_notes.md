# 07 — Monetization Notes

> **Update (June 2026):** Monetization is now in active rollout. The deferral rationale below applied to the original demand-test MVP (Phases 0–4). Execution order and scoped increments are in `11_monetization_rollout_plan.md`; full target design in `10_monetization.md`. **The ads rejection below still stands.**

## Why the original MVP phase had zero monetization built in

This MVP exists to answer one question cheaply: **do people actually use this?** Adding payment, accounts, or even ads at this stage adds engineering surface area (billing integration, legal terms, ad-network setup) that only pays off if the answer to that question is yes. Building monetization before demand is confirmed is solving a problem you don't know you have yet.

Ads specifically were considered and rejected for this product even at a later stage, not just deferred — see the reasoning below, kept here so it isn't relitigated mid-build.

## Why ads are a poor fit for this specific product (not deferred — actually rejected)

This tool's entire value proposition is "I help you see through manipulative persuasion." An ad-supported version creates a structural credibility problem: the tool's business model would depend on the same attention-and-persuasion economy its core feature scrutinizes. This matters even without any actual conflict of interest, because the audience this product attracts (people who care about argument quality) will reasonably distrust a tool whose incentives even *appear* compromised. Additionally, the economics are weak at this traffic scale — low pageviews-per-session and an ad-blocker-prone audience make ad revenue unlikely to materially exceed API costs.

**Do not add ads to this product even if asked to "monetize it quickly" later — flag this document instead and revisit the discussion explicitly, rather than defaulting to ads as the obvious next step.**

## What signal to watch for instead, during Phase 5

These are the things worth tracking that would inform a real monetization decision later:

- **Usage volume and repeat usage**: are the same people coming back to scan multiple things, or is it one-and-done curiosity?
- **Share/virality behavior**: are people sharing specific results (screenshots, links) without being asked to?
- **Unprompted requests for more**: do users ask for things like "can I scan a whole article via URL," "can I save my results," "can I run this on my newsletter before I send it" — these are organic signals about which paid tier might actually land, much more reliable than guessing upfront.
- **Who shows up**: individual casual users vs. people clearly testing it for a work use case (e.g., someone pasting in obviously professional content — a draft press release, a competitor's ad copy) are different future customers with different monetization paths (consumer freemium vs. B2B).

## If/when demand is confirmed, the menu to revisit (not to build now)

This was already discussed and doesn't need to be re-derived — the options on the table when this becomes relevant are:
1. Freemium usage caps (free tier + paid unlimited/higher-limit tier)
2. One-time/lifetime unlock purchase
3. Free tool as a funnel into a B2B offering (API access, bulk/dataset licensing) for media, ed-tech, debate-prep, or sales-call-QA use cases
4. Donations/pay-what-you-want if the free tool builds enough goodwill/audience on its own

None of these should be implemented speculatively. Revisit this document with real usage data in hand before picking one.
