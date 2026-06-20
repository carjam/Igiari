# Igiari Launch Checklist Tracker
**Based on:** `specs/06_testing_and_launch_checklist.md`  
**Step 0 rollout:** [`STEP0_LAUNCH_READINESS.md`](STEP0_LAUNCH_READINESS.md)  
**Last Updated:** 2026-06-20

---

## Functional Smoke Test

### Can Test Locally Now
- [x] ~~Load URL in fresh browser~~ → **✅ Tested locally at http://localhost:8080**
- [ ] Click "try example" → scan → see results ⏳ **Blocked by rate limit**
- [ ] Paste true-negative text → verify "no fallacies found" state ⏳ **Blocked by rate limit**
- [x] Paste >4000 chars → see pre-submission warning → **✅ Character counter present, turns red/warning**
- [ ] Hover highlighted span → see explanation ⏳ **Blocked by rate limit**
- [ ] Test on mobile device/emulation → **⏳ Can test UI only, no API calls**

### Must Test After Deployment
- [ ] Load LIVE URL (not localhost) in incognito
- [ ] Full flow on production
- [ ] Real mobile device test

---

## Cost/Abuse Safety Check

### Tested Locally ✅
- [x] **11+ requests → 11th rate-limited** → **✅ PASS** (triggered correctly in testing)
- [x] **API key not in browser** → **✅ PASS** (backend-only, never exposed)
  - Verified: Key in `.env`, loaded by server
  - Verified: `.claude/settings.json` blocks agent access
  - Verified: Frontend only sends text, never handles key

### Must Test After Deployment
- [ ] Rate limiting works on LIVE deployment (IP detection behind load balancer)
- [ ] API key not in Network tab of deployed frontend
- [ ] Set Anthropic API spend alert/budget cap

---

## Trust/Credibility Check

### Tested Locally ✅
- [x] **Privacy disclosure visible** → **✅ PASS** (footer, no scroll needed on desktop)
  - Text: "Pasted text is sent to Anthropic's API for analysis. We don't store your text beyond basic rate limiting."
  - Location: `frontend/index.html:63-66`
- [x] **Error copy sounds calm/clear** → **✅ PASS**
  - Rate limit: "You've exceeded the rate limit of 10 scans per hour. Please try again later."
  - Empty text: "Please provide some text to analyze."
  - Too long: "Text exceeds the 4,000 character limit. Please shorten your input."
- [x] **Empty-state copy positive** → **✅ PASS**
  - Text: "No fallacies found — this reasoning holds up."
  - Framed as success, not error

### Must Test After Rate Limit Resets
- [ ] Run 5+ real-world texts (news, marketing, social media)
- [ ] Sanity-check results look reasonable (not just eval set)

---

## Before Wider/Viral Push

### Phase 5 Requirements
- [ ] Analytics recording (Plausible/Simple Analytics/Cloudflare)
- [ ] Way to quickly take offline or reduce rate limit
- [ ] Daily spend/uptime monitoring plan for first week

---

## Blockers to "Ready to Soft-Launch"

### 🔴 Critical (Must Complete)
1. **Rate limit reset** (~35 minutes from now)
   - Needed to test full scan flow
   - Needed to run Phase 2 quality validation

2. **Phase 2 Quality Validation**
   - Run: `python backend/run_eval.py`
   - Check: Precision/recall/F1
   - Gate: True-negative accuracy > 60%

3. **Phase 3.5 Response Caching (NEW - REQUIRED)**
   - **Status:** Upgraded from SHOULD to MUST
   - **When:** After Phase 2 passes, before Phase 4 deployment
   - **Why:** Cost control for viral/repeated requests
   - **Implementation:**
     - SHA-256 hash of trimmed input as cache key
     - In-memory dict storing API responses
     - Optional: LRU eviction (max 1000 entries)
     - Optional: TTL (24 hours)
   - **Test:** Verify cache hit on identical text (no API call)
   - **Documented in:** `DECISIONS.md`

4. **Phase 4 Deployment**
   - Choose backend hosting (Render/Fly.io/VM)
   - Choose frontend hosting (Cloudflare Pages/Netlify/Vercel)
   - Deploy both
   - Configure production API_URL
   - Test end-to-end on LIVE URLs

5. **Phase 5 Analytics Setup**
   - Add analytics script (Plausible/Simple Analytics)
   - Test events are recording
   - Set up dashboard

### 🟡 Important (Should Complete)
- **Real-world text testing** (5+ examples)
- **Anthropic API budget alert** (if platform supports)
- **Mobile device testing** (real device, not just emulation)

### 🟢 Nice to Have
- Custom domain
- Social sharing graphics
- Multiple example cases
- Polished onboarding

---

## Testing Windows

### Now → Rate Limit Reset (+35 min)
**Can test:**
- ✅ UI/UX elements (buttons, layout, styling)
- ✅ Character counter behavior
- ✅ "Try an Example" button
- ✅ Error state display (currently visible)
- ✅ Mobile responsive CSS (resize browser)
- ✅ Privacy disclosure presence

**Cannot test:**
- ❌ Full scan flow
- ❌ Results rendering
- ❌ Hover tooltips
- ❌ No-fallacies state
- ❌ API responses

### After Rate Limit Reset
**Can test:**
- ✅ Full scan flow (example → scan → results)
- ✅ Results with highlights + tooltips
- ✅ No-fallacies-found state (true negatives)
- ✅ Phase 2 quality validation (30 eval cases)
- ✅ Real-world text testing

### After Phase 4 Deployment
**Must test:**
- ✅ Everything above on LIVE URLs
- ✅ Rate limiting on production (IP detection)
- ✅ CORS configuration
- ✅ Mobile on real devices
- ✅ Incognito/fresh browser
- ✅ API key security in Network tab

---

## Phase 2 Quality Gate Details

**Script:** `backend/run_eval.py`  
**Input:** 30 cases from `backend/fallacy_reference/eval_set.json`  
**Output:** `backend/eval_results.json`

**Metrics computed:**
- Precision (positive cases)
- Recall (positive cases)
- F1 score
- True-negative accuracy

**Pass criteria (from spec):**
- No fixed threshold for precision/recall (MVP tolerance)
- True-negative accuracy MUST be > 60%
- Results MUST be reviewed by human

**Failure modes to watch:**
- Low recall → missing most fallacies
- Low precision → flagging constantly
- Low TN accuracy → **LAUNCH BLOCKER** (hallucinating fallacies in clean text)

---

## Current Status: Phase 3 Complete ✅

**What works RIGHT NOW:**
- ✅ Backend API (tested, functional)
- ✅ Frontend UI (loaded, interactive)
- ✅ Rate limiting (tested, working)
- ✅ Error handling (tested with 429 error)
- ✅ All F1-F9 requirements met
- ✅ Design spec compliance
- ✅ API contract compliance

**What's blocking launch:**
1. Rate limit (35 min)
2. Phase 2 validation (pending #1)
3. Phase 4 deployment (pending #2)
4. Phase 5 analytics (pending #3)

**Estimated time to soft-launch:**
- Rate limit: +35 min
- Phase 2 validation: +15 min (running the script)
- Deployment decisions: +30 min (choose hosting)
- Deployment execution: +1-2 hours (deploy, configure, test)
- Analytics setup: +30 min
- **Total: ~3-4 hours from rate limit reset**

---

## Next Actions

**Immediate (when rate limit resets):**
1. Test full scan flow manually
2. Run `python backend/run_eval.py`
3. Review eval results
4. Test 5+ real-world texts

**If Phase 2 passes:**
5. Choose hosting providers (backend + frontend)
6. Deploy backend, set environment variables
7. Deploy frontend, update API_URL
8. End-to-end smoke test on production
9. Add analytics
10. Soft launch to small audience

**If Phase 2 fails (TN accuracy < 60%):**
- Fix prompt calibration
- Re-run eval
- Don't proceed to deployment until fixed

---

**Checklist Owner:** User (carjam)  
**Review Frequency:** After each phase completion  
**Next Review:** After rate limit reset + Phase 2 validation
