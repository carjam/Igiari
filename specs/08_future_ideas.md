# 08 — Future Ideas (Explicitly Out of Scope Now)

This is a parking lot. Nothing here should be built during the phases in `04_build_phases.md`. Its only purpose is to capture good ideas so they aren't lost or — worse — built prematurely by an agent that notices them mid-task and decides to "just quickly add" them.

## Product extensions
- Browser extension version (scan-in-place on any webpage) — the original motivating idea, deliberately deferred because it's a much larger engineering effort (DOM injection, multi-site compatibility, extension store review) and this web tool exists specifically to test demand before taking that on.
- URL fetching (paste a link instead of text) — adds scraping/legal complexity (paywalls, robots.txt, copyright concerns around storing/displaying fetched third-party content).
- File upload support (PDF, audio transcripts, docx).
- Multi-language support.
- Browser bookmarklet as a lighter-weight middle step between the web tool and a full extension — worth considering before building the full extension, not before building the web tool.
- "Debate mode" — paste both sides of an exchange and get a structured breakdown of fallacies per speaker.
- Audio/video input with timestamped findings (this was the original framing in the project that produced the underlying taxonomy and eval set — revisit once text-based demand is confirmed).

## Engagement/retention features
- Saved scan history (requires accounts)
- A public gallery/leaderboard of notable scanned examples (requires moderation, consent/privacy thinking around publishing user-submitted text)
- "Fallacy of the day" or similar recurring content
- Social sharing card generation (auto-generated image of a flagged finding, designed for sharing) — plausible high-leverage virality feature, but needs design work and isn't required for the demand test itself

## Technical improvements (not needed at MVP scale)
- Persistent rate-limit storage (Redis) surviving server restarts and multi-instance deployment
- A real database once any form of accounts/history is needed
- Streaming responses (show findings as they're detected rather than waiting for the full response) — nice UX improvement, added complexity, skip until the core loop is validated
- Caching layer for repeated/viral inputs (mentioned as a nice-to-have in `03_architecture.md` already — listed here too as a reminder it's not required)

## Business model ideas (see `07_monetization_notes.md` for the considered menu)
- B2B API/dataset licensing
- Embeddable widget for other websites/newsletters ("Scanned for fallacies by [tool]" badge) — interesting distribution mechanism, worth real consideration once there's a working v1 to embed
- Partnership with an existing reading/research/media-literacy tool rather than building distribution from scratch

## A note on why this list exists

If you're an agent and you think of a good idea while building the MVP, the correct action is: write it here, then keep going on the current phase. Do not implement it. The entire point of this spec is to keep the MVP small enough to actually finish and ship, so that the harder, more interesting ideas in this document have real usage data behind them when they're eventually evaluated.
