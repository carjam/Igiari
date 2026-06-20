# 03 — Architecture

This document makes concrete decisions rather than presenting options, so a building agent doesn't stall on choices. If you have a strong reason to deviate, document the reason in `08_future_ideas.md` or a `DECISIONS.md` you create, but default to what's written here.

## Stack decision

- **Frontend**: static HTML/CSS/vanilla JS. No framework (no React/Vue/etc). Reasoning: this is a single page with one form and one results view — a framework adds build tooling, dependency management, and deployment complexity with no real benefit at this scope. Keep it framework-free so it can be hosted anywhere static files are served.
- **Backend**: a thin Python server using FastAPI (or Flask if the building agent is more comfortable there — FastAPI preferred for built-in request validation). Reasoning: Python keeps the Anthropic SDK usage simple and matches the skill/eval tooling already built in Python.
- **Hosting**:
  - Frontend: any static host (Cloudflare Pages, Netlify, GitHub Pages, or Vercel static). Pick whichever the deploying agent/human already has an account for. No strong preference.
  - Backend: a small always-on or serverless host that supports Python — Render, Fly.io, or a single small VM. Needs to support environment variables (for the API key) and outbound HTTPS to api.anthropic.com.
- **No database for v1.** Rate limiting can be done in-memory or via a simple file/Redis if available — see "Rate limiting" below. Do not stand up Postgres/etc for this phase; there is no user data model yet.

## Why the API key MUST live server-side, never client-side

This is a hard requirement, not a preference. If the Anthropic API key were embedded in frontend JS, anyone could open browser dev tools, extract it, and use it to run unlimited requests on the builder's account/budget. The backend exists specifically to hold the key and proxy requests — this is the backend's entire job in v1. Do not skip building a backend "to save time" by calling the API directly from the browser.

## Model choice

Use **Claude Haiku 4.5** (`claude-haiku-4-5-20251001`) for this tool, not Sonnet or Opus. Reasoning: this is a cost-sensitive, high-volume, free consumer tool — Haiku-tier pricing is necessary for the unit economics to make sense at zero/low price points. If accuracy testing against the eval set (see below) shows Haiku's quality is unacceptably low on the existing 30-case eval set, escalate to Sonnet only for the specific cases that fail, and note the tradeoff in `DECISIONS.md` — don't silently upgrade the whole pipeline to a more expensive model without checking the eval set first.

Verify the current correct model string against `/mnt/skills/public/product-self-knowledge/SKILL.md` or by checking Anthropic's docs before hardcoding it, since model identifiers can change.

## Input length cap

Cap pasted text at **4,000 characters** (~700-800 words) for v1. Reasoning: long enough for an email, an article excerpt, or several paragraphs of transcript; short enough to keep both latency and per-request cost predictable and bounded. Enforce this in the frontend (disable submit / show a counter) AND in the backend (reject oversized requests) — never trust client-side validation alone.

## Rate limiting (cost control — required, not optional)

Implement IP-based rate limiting on the backend: a sensible starting point is **10 scans per IP per hour**. Use a simple in-memory token bucket (a Python dict keyed by IP, reset on server restart, is fine for v1 — this does not need to survive restarts or scale across multiple server instances yet). If the chosen host makes Redis trivially available, use that instead for slightly more robustness, but don't add Redis as a new dependency just for this.

This is specifically to prevent a worst-case scenario where the tool goes viral or is hit by a bot and runs up an unbounded API bill overnight. Build this in Phase 1, not as a later hardening pass.

## Caching (cost control, nice-to-have, not blocking)

If time allows: cache results by a hash of the input text (e.g., SHA-256 of the trimmed/normalized input) so identical repeated submissions (e.g., the same viral example text submitted by many visitors) don't re-trigger an API call. An in-memory dict with a max size/eviction policy (or simple TTL) is sufficient for v1. This is a SHOULD, not a MUST — don't block launch on it.

## How the backend uses the existing skill content

The backend does NOT need to "use the skill" in the sense of Claude Skills/agentic tool use — there's no agent loop here, just a single API call per scan. Instead:

1. Load `fallacy_reference/fallacies.json` at server startup (or build time) into memory.
2. Construct a system prompt for the API call that includes: a condensed version of the taxonomy (name + definition + pattern for all 136 fallacies, or a curated subset — see note below), the calibration guidance from the existing `SKILL.md` (don't manufacture findings, true negatives are valid, distinguish real fallacies from merely weak arguments), and the exact output JSON schema from `05_api_contract.md`.
3. Send the user's pasted text as the user-turn content.
4. Parse the model's JSON response and return it to the frontend.

**Token budget note**: including all 136 fallacies' full definitions in every request adds meaningful input tokens to every single call. Two options, pick one and document the choice:
- (a) Include the full taxonomy every time — simpler, more consistent detection, higher per-call cost.
- (b) Curate it down to the ~40–50 most common/highest-value fallacies for a first version (the ones most likely to appear in everyday text — see the Informal categories in the taxonomy, since the existing eval set skews almost entirely Informal already) — cheaper, slightly less comprehensive.
Default to (a) for v1 unless cost testing in Phase 2 shows it's a problem, since correctness matters more than cost at this stage and the absolute token count (136 short entries) is not large by modern context-window standards.

## Validating output quality

After the backend is built, run a manual or scripted check against the existing eval set (`eval_set.json` from the prior project) before considering Phase 2 done. Reuse `grade_eval.py`'s matching logic if practical, adapted to call the new backend's API instead of reading a static predictions file. This is the single most important quality gate in this whole build — don't skip it.
