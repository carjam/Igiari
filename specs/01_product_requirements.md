# 01 — Product Requirements

## User story

> As a visitor with no account, I want to paste a piece of text (an email, an ad, an article excerpt, a chat transcript) into a web page and immediately see which parts of it use flawed reasoning, what the flaw is called, and why — so I can decide whether to trust it.

## Functional requirements (MUST have for v1)

| # | Requirement | Notes |
|---|---|---|
| F1 | A text input area where the user pastes or types text | Plain `<textarea>`, no rich text needed |
| F2 | A "Scan" button that submits the text for analysis | Disabled while a request is in flight |
| F3 | A findings list showing each flagged span (the exact quote), the fallacy name, category, and explanation | As of 2026-07, this is the only rendering of results — the full pasted text is not echoed back inline, since the user already has it |
| F4 | Each finding also shows a confidence level and, when applicable, what would strengthen the reasoning | Part of the same findings-list card as F3, not a separate hover/click interaction |
| F5 | A visible, enforced input length cap | See `03_architecture.md` for the exact number and why |
| F6 | A loading state while the request is processing | Should not feel broken on a 5–10 second wait |
| F7 | A clear empty/error state if the model finds nothing, or if the request fails | "No fallacies found" is a valid, expected result — must not look like an error |
| F8 | A way to try it instantly with zero setup, e.g. a "try an example" button that pre-fills a known-good sample | Removes the blank-page problem — see `02_design_direction.md` |
| F9 | Basic abuse/rate limiting | See `03_architecture.md` — this is a cost-control requirement, not optional polish |

## Functional requirements (SHOULD have, do if time allows, do not block launch on these)

| # | Requirement | Notes |
|---|---|---|
| S1 | A "copy results as text" or "share result" button | Low effort, helps virality (people screenshot/share findings) |
| S2 | A confidence indicator per flagged span (high/medium/low) | Already part of the skill's output schema — just surface it |
| S3 | Simple analytics (page views, scans run, scan-to-share rate) | Needed to evaluate whether this experiment "worked" — see `06_testing_and_launch_checklist.md` |

## Explicitly OUT of scope for v1 (do not build, even if easy)

- User accounts / login
- Payment of any kind
- Saving/history of past scans
- File upload (PDF, docx, audio) — text paste only
- URL fetching (paste text, not a link)
- Browser extension
- Mobile native app
- Any language other than English
- Editing/correcting the highlighted text
- Admin dashboard or moderation tooling beyond basic rate limiting
- A “fallacy of the day” or other recurring content (engagement features) — out of scope, revisit only if v1 gets traction

## Non-functional requirements

- **Cost ceiling**: must be operable for under ~$20/month at low/moderate traffic (a few hundred scans/day). This shapes model choice and caching decisions in `03_architecture.md`.
- **No dark patterns**: don't manufacture findings to seem more impressive than the text warrants. This product's entire value proposition is trustworthiness — a tool that over-flags or fabricates results to seem more "useful" undermines its own premise. The backend prompt must preserve the calibration guidance from the existing skill (false positives are costly, not every weak argument is a named fallacy, true negatives are valid and expected outputs).
- **Privacy**: pasted text is sent to the Anthropic API for processing. State this plainly on the page (one sentence is enough — see `02_design_direction.md` for copy guidance). Do not log/store submitted text beyond what's needed for basic rate-limiting/abuse prevention, and say so.

## Acceptance criteria for this document

This document is "satisfied" once `04_build_phases.md`'s tasks, when complete, produce a tool that satisfies every row in the MUST table above. Each phase in `04_build_phases.md` references back to specific F-numbers here.
