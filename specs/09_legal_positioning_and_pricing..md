# Igiari! for Legal — Positioning & Pricing

## The one-sentence pitch

**"Before you send it, check whether the argument actually holds up."**

A reasoning-quality check for demand letters, declarations, and correspondence — not a drafting tool, not a citation checker, not a case-management platform. The thing none of those check.

## Why this gap is real (not assumed)

The legal AI market is saturated with tools that draft, summarize, and assemble — EvenUp, AI Demand Pro, ProPlaintiff, NexLaw, CoCounsel, Clio. Every one of them explicitly leaves the actual argumentative reasoning to attorney judgment: drafting tools tighten prose and assemble facts, but framing a weakness as supported causation rather than an admission — the actual *argument* — is left as manual, non-negotiable attorney work, by every vendor's own admission. That's not an oversight. It's outside what a generative drafting tool is built to evaluate, because generation and evaluation are different tasks. Igiari does the second one.

## Lead beachhead: Personal Injury solos

**Why PI leads**: the pain is dollar-denominated and already named in the market's own language — a weak causation argument or an unaddressed pre-existing-condition framing is something an adjuster is specifically trained to find and exploit, and it directly affects the settlement number. That makes the pitch concrete: *catch the reasoning gap before the adjuster does.*

**The moment this gets used**: a solo or small PI firm's paralegal/associate drafts a demand letter (possibly using one of the AI drafting tools above) → before it goes to the client or out the door, run it through Igiari → it flags, e.g., a weak causal link between the accident and a later symptom, or a damages claim that doesn't logically follow from the stated facts → attorney fixes it before an adjuster ever sees the gap. Same flow in reverse: an adjuster's denial letter comes in → scan it for the actual reasoning supporting the denial → respond directly to the weak logic, not just the outcome.

## Secondary beachhead: Family law solos

Same product, same pitch, riding alongside PI rather than requiring separate positioning: custody declarations, response letters to opposing counsel, settlement correspondence in a divorce — all argumentative prose, all high-emotion, all places where a shaky inference ("the children are obviously better off with X because Y") is worth catching before it's read by a judge or opposing counsel. Use as the second example on the landing page, not a separate campaign.

## What this product explicitly is NOT, and should say so directly

- Not a legal research tool (no case law database, no Shepard's-style citation validation — if asked, say so plainly rather than overclaiming)
- Not a drafting tool (it doesn't write the letter — it reviews one that already exists)
- Not a replacement for attorney judgment or a substitute for malpractice-grade review — frame as a second pair of eyes, not an authority
- Not exclusive to legal — same core product as the consumer/debate version; legal gets its own landing page and pricing tier, not a forked product

## Positioning language to use (and avoid)

**Use**: "reasoning check," "argument review," "catch the gap before they do," "a second pair of eyes on the logic." Plain, concrete, outcome-tied.

**Avoid**: "AI-powered legal assistant" (sounds like every drafting tool above — actively hurts differentiation), "logical fallacy detector" as the lead phrase in legal marketing specifically (correct and precise for a technical/academic audience, but "fallacy" reads as undergraduate-philosophy jargon to a practicing attorney — lead with the outcome, use "fallacy" as the explanatory detail once they're already interested, not as the hook).

**Trust signals this audience needs, stated plainly, same honest approach as the consumer product**: data handling (don't store client text beyond abuse-prevention needs, same as the existing privacy copy), no claim of being a substitute for legal judgment, clear about what it doesn't do (see above) — this audience has been trained by their own bar associations to be skeptical of AI overclaiming, and a tool that's upfront about its limits will read as more credible, not less.

---

## Implementation status (June 2026)

| Item | Status |
|------|--------|
| `/legal` landing + copy | ✅ Live |
| Legal surface tagging (`?surface=legal`) | ✅ Code deployed |
| Legal Stripe on Render ($29 / $39) | ⬜ **Not configured** |
| Checkout from legal funnel today | Interim consumer Starter ($8) / Casual ($9/mo) |

Enable legal checkout: [docs/LEGAL_BILLING_SETUP.md](../docs/LEGAL_BILLING_SETUP.md).

---

## Pricing

### Why legal pricing sits well above the consumer/debate tier

This is value-based, same principle as the original consumer pricing, applied to a buyer with a much higher stakes-per-scan ratio. A PI solo who catches one weak causation argument before a $30,000 settlement negotiation has gotten value far in excess of a $0.50-1/scan price — and the comparison set (LegesGPT at $19.99/mo, NexLaw's flat-rate solo pricing, both explicitly positioned *below* the $225+/seat enterprise platforms) confirms solos will pay real money for a narrow, well-targeted tool, just not enterprise-platform money.

### Packs

| Pack | Price | Scans | Price/scan |
|---|---|---|---|
| Starter | $29 | 25 | $1.16 |
| Standard | $79 | 100 | $0.79 |
| Practice | $199 | 300 | $0.66 |

### Subscription

| Plan | Price/mo | Scans included | Price/scan |
|---|---|---|---|
| Solo | $39/mo | 50 | $0.78 |
| Practice | $99/mo | 200 | $0.49 |

All of the above sit at roughly 92–95% gross margin over true cost (API + Stripe fees + amortized hosting, at a blended ~1,000 scans/month assumption across the legal customer base) — meaningfully higher margin than the consumer/debate tier, which is appropriate: legal buyers are paying for outcome-relevant stakes, not raw compute, and the price should reflect that rather than tracking the same cost-multiple as a hobbyist tool.

### Free trial

Same mechanism as the rest of the product: **5 free scans, no card required.** For this audience specifically, frame the trial copy around a real use case on the landing page itself ("run your last demand letter through it, free") rather than a generic "try it" button — concreteness matters more to this buyer than to the consumer/debate audience.

### Why not a flat per-seat subscription like the enterprise platforms

Per-seat pricing (Harvey, CoCounsel, GC AI) makes sense when the platform is the attorney's daily driver across every task. Igiari is a narrow, occasional-but-high-stakes check — usage-based packs and a lighter subscription tier match how this tool actually gets used (a handful of times per active case, not constantly), and undercutting the enterprise per-seat model on structure, not just price, reinforces the "narrow tool, not a platform" positioning.

---

## Landing page / outreach notes

- Build a dedicated `/legal` (or `/for-legal`) landing page reusing the existing product, not a separate app — same backend, same credit system, just legal-specific copy and the PI/family-law example scans.
- Use a real (anonymized/synthetic, not an actual client's) demand letter excerpt as the "try an example" default on this page, the same pattern as the original consumer tool's example button — but make the example a realistic PI scenario (a weak causation claim) rather than the debate/political example used elsewhere.
- Outreach channels worth testing first, cheaply, before any paid acquisition: PI- and family-law-focused solo practitioner communities (state bar solo/small-firm sections, relevant subreddits, PI-specific Facebook groups — these exist and are active per the "fragmented, solo-dominated" market description found earlier), not broad legal-tech press, which skews toward the enterprise platforms this product deliberately isn't competing with.
