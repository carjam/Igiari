# 02 — Design Direction

## Read `/mnt/skills/public/frontend-design/SKILL.md` if available before starting UI work

This document gives this-specific-project answers to that skill's framework, so the building agent isn't starting from a blank slate. If the skill isn't available in your environment, follow this document directly — it's self-contained.

## Ground the design in the actual subject

The subject is **rhetoric and argumentation** — not "AI" or "productivity software." Avoid the generic AI-tool look (rounded cards, purple-to-blue gradients, a chat bubble icon, Inter font, "Powered by AI" badges). This is not a chatbot. It should feel more like a tool a debate coach, an editor, or a fact-checker would have on their desk — precise, slightly skeptical, unflashy.

Reference material worth drawing from for visual/verbal vocabulary: copyediting marks (strikethrough, marginalia, redline annotations), courtroom exhibit tabs, the red-pen-on-an-essay feeling, dictionary/encyclopedia cross-reference numbering. The product is fundamentally an annotator — lean into that, the way a track-changes view or a heavily annotated PDF looks, rather than a generic "AI insight" panel.

## Suggested token system (a starting point — refine, don't default further toward generic)

**Color** — avoid both the cream/terracotta AI-default and the black/acid-green AI-default named in the frontend-design skill. Suggested direction: a paper-like off-white background, ink-black text, and ONE precise accent used only for flagged spans — a deliberate, slightly desaturated red (like a copyeditor's pen, not an alarm/error red). Something like:
- Background: `#FAF8F3` (warm paper, not stark white)
- Text: `#1A1A18` (soft black, not pure #000)
- Accent (flag highlight underline): `#A8332B` (muted brick red — "red pen," not "danger")
- Secondary accent (UI chrome, buttons): `#2B3A42` (dark slate, not blue)
- Muted/borders: `#D8D2C4`

**Type** — a serif for body text (this is fundamentally a reading/annotation tool, serif reads as "considered," and most pasted content — articles, emails — is prose) paired with a clean monospace or grotesk for UI labels/metadata (fallacy names, confidence levels) to create a clear visual distinction between "the user's text" and "the tool's annotations." Avoid Inter as the body face — it is the single most common AI-tool default. Consider something like a slab or text serif (e.g., a Georgia/Source Serif/Lora-class face) for the pasted text, and a tighter grotesk or mono for labels.

**Layout concept**: A single centered column, like a printed page. The paste box sits where the page "begins." After scanning, the same column re-renders with inline annotations — the text doesn't move to a different panel, it transforms in place, the way redline/track-changes works. Avoid a generic two-panel "input left, output right" SaaS layout; the in-place transformation is more honest to what's happening and removes a layout decision (no separate scroll regions to sync).

**Signature element**: The annotation itself should be the one memorable, considered design element — not a separate badge or icon system. Suggested treatment: flagged spans get a wavy or dashed underline (echoing a copyeditor's mark) in the accent color; hovering reveals a small marginal note (like a margin comment in a printed/annotated document) showing the fallacy name and one-line explanation, rather than a generic floating tooltip card. If a margin-note treatment is too complex for v1, a simple tooltip is an acceptable fallback — but keep the underline-as-redline-mark treatment regardless, since it's cheap and does a lot of the visual work.

## Specific UI moments to get right

- **Empty/start state**: Don't show a blank textarea with placeholder text like "Paste your text here..." and nothing else — that's the generic default. Instead, lead with one real example already loaded as a clickable suggestion (e.g., a short sample sentence containing an actual fallacy) so a first-time visitor can see the product work with one click, with zero typing. This satisfies requirement F8 in `01_product_requirements.md`.
- **Loading state**: avoid a generic spinner. Consider a brief, dry, in-voice loading message ("Reading closely…" / "Checking the reasoning…") — matches the copyediting metaphor, costs nothing extra to build.
- **No-fallacies-found state**: this must NOT look like an error or a dead end. Phrase it as a real, positive finding: e.g., "No fallacies found — this reasoning holds up." Visually distinct from the error state (different color, not just different text).
- **Error state** (API failure, rate limit hit): plain language, tells the user what happened and what to do, never blames the user, never apologizes excessively. E.g., "That didn't go through — try again in a moment" rather than a raw error code.

## Copy voice

Plain, direct, slightly dry — like the tool itself has good epistemic hygiene. Avoid hype language ("Supercharge your reading!", "AI-powered insights!"). Avoid moralizing or scolding tone toward whatever text the user pastes — the tool's job is to describe reasoning patterns accurately, not to shame the user or the text's author.

One line of plain-language privacy disclosure is required somewhere visible (footer is fine): state that pasted text is sent to a third-party AI model for analysis and is not stored beyond basic abuse prevention. Don't bury this in a separate privacy policy page for v1 — one honest sentence on the main page is sufficient at this scale, and is more trustworthy than a wall of legal text for a free anonymous tool.

## Explicit anti-patterns to avoid (per frontend-design skill calibration notes)

Do not default to: cream background + serif display + terracotta accent; OR near-black background + single acid-green/vermilion accent; OR broadsheet hairline-rule newspaper layout — unless the reasoning above happens to lead there deliberately (the paper/ink direction above is adjacent to the broadsheet default; lean into hairline rules and dense-text-column structure deliberately if that's the direction taken, but make sure the *annotation/redline* signature element — not the broadsheet styling itself — is what makes this feel distinct, since broadsheet-as-default is explicitly called out as overused).
