# 06 — Testing & Launch Checklist

Run through this before sharing the URL with anyone beyond the builder. This is intentionally short — the goal is catching the failure modes that would actually hurt (cost blowouts, embarrassing bugs, broken trust), not exhaustive QA.

## Functional smoke test

- [ ] Load the live URL in a fresh/incognito browser window (catches any "works on my machine because I'm logged in / have cached state" issues — though this app has no auth, this also catches stale local builds)
- [ ] Click "try an example," click scan, confirm a highlighted result appears within ~10 seconds
- [ ] Paste a piece of clean, well-reasoned text (e.g., one of the true-negative cases from `eval_set.json`) and confirm the "no fallacies found" state renders correctly, not as an error
- [ ] Paste text over 4000 characters and confirm a clear pre-submission warning appears
- [ ] Hover/click a highlighted span and confirm the explanation appears legibly
- [ ] Test on a real mobile device or browser dev tools' mobile emulation, not just resizing a desktop window

## Cost/abuse safety check

- [ ] Send 11+ rapid requests from one machine and confirm the 11th is rate-limited with a clear message, against the LIVE deployment (not just localhost)
- [ ] Confirm the API key is not visible anywhere in browser dev tools (Network tab, page source, JS bundles)
- [ ] Set a spend alert/budget cap on the Anthropic API account itself if the platform supports it, as a backstop below the application-level rate limiter

## Trust/credibility check

- [ ] Confirm the privacy disclosure sentence is visible without scrolling or clicking into a separate page
- [ ] Re-read the error and empty-state copy out loud — does it sound calm and clear, or alarming/buggy?
- [ ] Run at least 5 pieces of real-world text through it (a real news article paragraph, a real marketing email, a real social media post) — not just the curated eval set — and sanity-check the results look reasonable. The eval set passing is necessary but not sufficient; real text is messier.

## Before any wider/viral push

- [ ] Confirm analytics are recording (per Phase 5 in `04_build_phases.md`)
- [ ] Confirm you have a way to quickly take the tool offline or drop the rate limit further if costs spike unexpectedly (don't deploy something you can't quickly throttle)
- [ ] Decide who is checking spend/uptime daily for the first week, even if that's just the builder themself

## What "ready to soft-launch" means

All boxes above checked. This does NOT require: polished onboarding, multiple example cases, social sharing graphics, or a custom domain — those are all fine to add later and shouldn't block getting real signal on whether anyone wants this.
