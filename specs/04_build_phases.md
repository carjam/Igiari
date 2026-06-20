# 04 — Build Phases

Execute these phases in order. Each phase lists its dependencies, tasks, and acceptance criteria. **Do not start a phase until the previous phase's acceptance criteria are met.** If you are an autonomous agent working without a human checking in after every phase, still stop and self-verify against the acceptance criteria before moving on — don't chain phases together speculatively.

---

## Phase 0 — Setup

**Depends on**: nothing.

**Tasks**:
- Create the repo structure shown in `00_master_spec.md`.
- Copy `fallacies.json` and `fallacy_taxonomy.md` from `../source-materials/references/` into `backend/fallacy_reference/`. If these files aren't available, stop and ask the human for them rather than recreating the taxonomy from scratch — it already exists and recreating it risks inconsistency with the eval set.
- Copy `eval_set.json` from `../source-materials/eval/` into `backend/fallacy_reference/eval_set.json` — needed in Phase 2.
- Set up a `.env.example` in `backend/` with a placeholder `ANTHROPIC_API_KEY=` line. Never commit a real key.
- Initialize git, add a `.gitignore` that excludes `.env`, `__pycache__`, `node_modules` (if any).

**Acceptance criteria**: Repo structure exists, taxonomy files are in place, `.env` is gitignored.

---

## Phase 1 — Backend skeleton + API contract

**Depends on**: Phase 0.

**Tasks**:
- Read `05_api_contract.md` for the exact request/response schema before writing code.
- Build a minimal FastAPI (or Flask) server with one POST endpoint matching the contract in `05_api_contract.md`.
- Wire up the Anthropic API call per the model/prompt approach in `03_architecture.md`. Use the official Anthropic Python SDK, not raw HTTP requests, unless there's a specific reason not to.
- Implement input length validation (reject >4000 chars with a clear error response — see `03_architecture.md`).
- Implement IP-based rate limiting (see `03_architecture.md`) — this must exist before any public deployment happens, even a soft-launch one.
- Return parsed JSON matching the contract; handle the case where the model's output isn't valid JSON gracefully (retry once, then return a clear error rather than crashing).

**Acceptance criteria**:
- Can `curl` the endpoint locally with sample text and get back a well-formed JSON response matching `05_api_contract.md`.
- Submitting >4000 characters returns a clear 4xx error, not a 500 or a silent truncation.
- Making 11 requests from the same IP within the rate-limit window returns a clear rate-limit error on the 11th.
- The API key is read from an environment variable, never hardcoded, and is absent from any logs.

---

## Phase 2 — Quality validation against the eval set

**Depends on**: Phase 1.

**Tasks**:
- Using the running backend from Phase 1, send each `transcript` field from `eval_set.json` to the new endpoint.
- Compare results against `ground_truth` using the same matching logic as `grade_eval.py` (canonical-name + alias matching, not exact span matching).
- Compute precision/recall/F1 on positive cases and accuracy on true-negative cases, same as the original grading script's output format.

**Acceptance criteria**:
- A precision and recall number exists and has been looked at by a human or reported clearly, not skipped.
- If recall is very low (missing most fallacies) or precision is very low (flagging things constantly, including on true-negative cases), **stop and fix the prompt before proceeding to Phase 3.** Building a frontend on top of a backend that doesn't work is wasted effort — this gate exists to prevent that.
- There is no fixed numeric bar required to "pass" (this is a demand-test MVP, not a production system) — but a backend that gets most true-negative cases wrong (frequently hallucinating fallacies in clean text) is a launch-blocking quality bar, since it directly violates the "no dark patterns / don't manufacture findings" requirement in `01_product_requirements.md`.

---

## Phase 3 — Frontend build

**Depends on**: Phase 2 passing its acceptance criteria.

**Tasks**:
- Read `02_design_direction.md` fully before writing any CSS.
- Build `index.html` / `styles.css` / `app.js` per the requirements in `01_product_requirements.md` (F1–F9) and the design direction in `02_design_direction.md`.
- Implement the paste box, scan button, loading state, results rendering with inline highlights, hover/click reveal of explanations, empty/no-fallacies state, and error state.
- Implement the "try an example" pre-fill button (F8) using one of the example transcripts from `eval_set.json` that has a clear, well-known fallacy (e.g., `eval_002`'s straw man example is a good candidate — it's short and the fallacy is easy to see once pointed out).
- Implement the client-side character counter/cap matching the backend's 4000-character limit, so users get instant feedback rather than waiting for a server rejection.
- Add the one-sentence privacy disclosure per `02_design_direction.md`.

**Acceptance criteria**:
- A human can open the page, click "try an example," click "scan," and see highlighted results within ~10 seconds, with no console errors.
- Pasting >4000 characters shows a clear in-page warning before submission, not just a backend error after the fact.
- The empty/no-fallacies state and the error state are visually distinguishable from each other (verify by triggering both manually — e.g., scan a clean sentence for the former, kill the backend server temporarily for the latter).
- Layout doesn't break at common mobile widths (test at ~375px wide at minimum) even though this is primarily a desktop-use tool.

---

## Phase 4 — Integration + deployment

**Depends on**: Phase 3.

**Tasks**:
- Connect frontend to the deployed backend (not localhost) — update the API base URL.
- Deploy backend to the chosen host (see `03_architecture.md`) with the real API key set as an environment variable on the host, never in source.
- Deploy frontend to the chosen static host.
- Verify CORS is configured correctly so the deployed frontend can call the deployed backend (a same-origin-only backend will silently fail from a different-domain frontend — this is a common integration snag, check for it explicitly).
- Do a final end-to-end smoke test on the live public URL, not just localhost.

**Acceptance criteria**:
- The live public URL works end-to-end for a stranger with no setup: paste text (or click "try an example"), scan, see results.
- Rate limiting is confirmed working against the LIVE deployment, not just the local dev server (host environments sometimes behave differently — e.g., requests may appear to come from a load balancer IP rather than the real client IP; verify the rate limiter is keying on the correct address in the deployed environment).
- Run through the full `06_testing_and_launch_checklist.md` before sharing the URL publicly.

---

## Phase 5 — Soft launch + signal collection

**Depends on**: Phase 4.

**Tasks**:
- Add minimal analytics per `01_product_requirements.md` S3 (even a free tier of Plausible/Simple Analytics/Cloudflare Web Analytics is enough — avoid heavy tools like full Google Analytics for a single-page tool).
- Share the URL in a small, low-stakes way first (a few friends, a niche forum/community relevant to critical thinking or media literacy) before any broad/viral push — this is a deliberate choice to catch bugs and cost issues at small scale before they happen at large scale.
- Watch API spend daily for the first week. If costs are tracking higher than expected, revisit the rate limit and the model choice in `03_architecture.md` before any wider promotion.

**Acceptance criteria**: this phase doesn't have a hard "done" — it's the start of the demand-testing process itself, which is the actual goal of this entire project per `00_master_spec.md`. Treat Phase 5 as ongoing rather than a task to complete and check off.
