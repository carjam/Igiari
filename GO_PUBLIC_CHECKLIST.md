# Go Public Checklist

This checklist guides you through making the repository public and shutting down paid services.

## ✅ Phase 1: Documentation (COMPLETE)

- [x] Add MIT LICENSE
- [x] Update README with portfolio context
- [x] Create ARCHITECTURE.md for technical highlights
- [x] Create DEPLOYMENT_STATUS.md with restart instructions
- [x] Add archived notices to deployment docs
- [x] Improve .gitignore for better security

## 🔒 Phase 2: Security Verification (DO THIS)

Before making the repo public, verify no secrets are exposed:

### Check for secrets in committed files:
```bash
# Search for potential secrets (should find nothing concerning)
git grep -i "sk_live"
git grep -i "sk_test"
git grep -i "whsec_"
git grep -E "ANTHROPIC_API_KEY.*=.*sk-ant"
git grep -E "SUPABASE_SERVICE_ROLE_KEY.*=.*eyJ"

# Verify .env is gitignored (should return nothing)
git ls-files | grep "^\.env$"
```

### Expected safe findings:
- ✅ `site-config.js` with Supabase ANON key - **This is safe** (public by design)
- ✅ References to example keys like `sk_test_...` in docs - **This is safe** (placeholder examples)
- ✅ Production URLs (igiari.us, etc.) - **This is safe** (not secrets, just infrastructure)

### Verify environment variables are secure:
- ✅ All sensitive keys are in `.env` (which is gitignored)
- ✅ `backend/.env.example` contains only placeholder values
- ✅ `render.yaml` marks all secrets as `sync: false`

## 💰 Phase 3: Shut Down Paid Services

### Cloudflare Pages
**Cost:** Varies (currently paying)

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to **Workers & Pages** → **igiari** project
3. **Option A (Pause):** Settings → Deployments → Pause deployments
4. **Option B (Delete):** Settings → Delete project
5. **Domain:** Optionally remove custom domain `igiari.us` or let it remain parked

**Result:** Stops Cloudflare charges. Frontend no longer accessible at igiari.us.

### Anthropic API
**Cost:** Pay-per-use (stops when backend is down)

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. **Option A (Set spend limit):** Settings → Limits → Set to $0
3. **Option B (Delete key):** Settings → API Keys → Delete key

**Result:** Prevents any accidental API charges. Backend won't work without key.

### Render (Backend)
**Cost:** Free tier (but keep it available for portfolio if desired)

**If you want to shut it down completely:**
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Select **igiari-backend** service
3. **Option A (Suspend):** Settings → Suspend service (can resume later)
4. **Option B (Delete):** Settings → Delete service

**If you want to keep free tier:**
- Leave it running - it will auto-sleep after 15min of inactivity
- Cold starts take ~30s but shows "it works" for portfolio viewers
- No cost on free tier

**Recommendation:** Keep it on free tier for portfolio demo (with rate limiting).

### Supabase
**Cost:** Free tier (auto-pauses weekly)

**Action:** No action needed. Free tier is fine.

- Already pauses weekly due to inactivity
- Keeps your schema and data intact
- Wakes up on first request

### Resend
**Cost:** Free tier (100 emails/day)

**Action:** No action needed. Free tier is fine.

- Only sends emails when someone signs in
- Well within free tier limits

### Stripe
**Cost:** Free (only charges on transactions)

**Action:** No action needed.

- No cost unless processing payments
- Keep account to showcase integration
- Can disable webhook if desired (prevents errors in Stripe logs)

**Optional - Disable webhook:**
1. Go to [Stripe Webhooks](https://dashboard.stripe.com/webhooks)
2. Find webhook pointing to `igiari-backend.onrender.com`
3. Click **...** → Disable

## 🌐 Phase 4: Make Repository Public

### Before making public, commit all changes:

```bash
git status
git add LICENSE ARCHITECTURE.md DEPLOYMENT_STATUS.md GO_PUBLIC_CHECKLIST.md
git add README.md .gitignore docs/
git commit -m "docs: prepare repository for public release

- Add MIT LICENSE
- Add ARCHITECTURE.md for technical overview
- Add DEPLOYMENT_STATUS.md with restart instructions
- Update README with portfolio context
- Add archived notices to deployment docs
- Improve .gitignore for better secret protection"
git push origin master
```

### Make the repository public:

**Via GitHub Web:**
1. Go to https://github.com/carjam/Igiari
2. Click **Settings** tab
3. Scroll to **Danger Zone**
4. Click **Change visibility**
5. Select **Make public**
6. Type repository name to confirm
7. Click **I understand, make this repository public**

**Via GitHub CLI (if installed):**
```bash
gh repo edit carjam/Igiari --visibility public
```

### Verify it's public:
- Visit https://github.com/carjam/Igiari in incognito/private window
- Should be viewable without login

## 🎨 Phase 5: Add to Portfolio

### Update your GitHub profile README

If you have a profile README (https://github.com/carjam/carjam), add Igiari:

```markdown
## 🚀 Featured Projects

### [Igiari - Logical Fallacy Scanner](https://github.com/carjam/Igiari)
Production-ready SaaS with LLM integration, Stripe billing, and authentication.

**Tech:** FastAPI · Anthropic Claude · Stripe · Supabase · PostgreSQL · Pytest
```

### Pin the repository

1. Go to https://github.com/carjam
2. Click **Customize your pins**
3. Select **Igiari**
4. Arrange as desired

### Add topics/tags to repository

On GitHub repo page:
- Click ⚙️ next to **About**
- Add topics: `fastapi`, `stripe`, `anthropic`, `llm`, `saas`, `python`, `postgresql`, `supabase`, `portfolio`
- Add description: "Production-ready SaaS for detecting logical fallacies using Claude AI"
- Add website: (leave blank or add your portfolio URL)

### Create social preview image (optional)

1. Create 1280x640px image with:
   - Project name "Igiari"
   - Tech stack logos
   - Screenshot of UI
2. Upload to: GitHub repo → Settings → Social preview → Upload image

## 📸 Phase 6: Create Portfolio Assets (Optional)

### Take screenshots for portfolio:

1. **Homepage/Scanner** - Clean UI showing the fallacy scanner
2. **Results** - Example of detected fallacies with explanations
3. **Auth Flow** - Sign-in interface (demonstrates auth implementation)
4. **Stripe Checkout** - Payment flow (demonstrates monetization)
5. **Architecture Diagram** - Consider creating a visual architecture diagram

### Record a demo video:

- 30-60 second walkthrough
- Show: paste text → detect fallacies → see results
- Host on YouTube or similar
- Embed in portfolio site

## ✅ Final Verification

Before announcing:

- [ ] Repository is public and viewable
- [ ] README looks good on GitHub (check formatting)
- [ ] ARCHITECTURE.md is accessible and well-formatted
- [ ] No secrets exposed (double-check)
- [ ] LICENSE file is present
- [ ] Repository topics/tags are added
- [ ] At least one commit after going public (to trigger GitHub's social preview generation)

## 🎉 Done!

Your SaaS portfolio project is now public and ready to impress recruiters!

**Next steps:**
- Share on LinkedIn with your network
- Add to your resume under "Projects"
- Reference in cover letters when applying to relevant positions
- Keep iterating based on feedback

---

**Note:** You can always restart services later if you want to show a live demo during interviews. See [DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md) for instructions.
