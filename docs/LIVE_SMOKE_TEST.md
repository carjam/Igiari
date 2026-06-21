# Live Smoke Test — Production

**Run date:** 2026-06-21  
**Target:** https://igiari.us · https://igiari-backend.onrender.com  
**Method:** Automated script + manual notes

---

## Automated (14/14 pass)

| Check | Result |
|-------|--------|
| Frontend `https://igiari.us/` HTTP 200 | ✅ |
| Header: Objection! + tagline | ✅ |
| Cloudflare Web Analytics beacon | ✅ |
| No API key in HTML or public JS | ✅ |
| Auth + pricing UI present | ✅ |
| Backend health `GET /` | ✅ |
| `GET /api/billing/products` (2 products) | ✅ |
| `POST /api/scan` without auth → 401 `NOT_SIGNED_IN` | ✅ |
| `legal/privacy.html`, `legal/terms.html` load | ✅ |

---

## Manual checklist

| Item | Result | Notes |
|------|--------|-------|
| Sign in → Try Example → Scan → results ~10s | ✅ Owner verified (Stripe test session) | |
| Sandbox Checkout → credits grant (+50 Starter) | ✅ | 19 → 69 |
| Webhook replay idempotency | ✅ | Resend `checkout.session.completed` → still 69 |
| True negative → "No fallacies found" | ⏳ | Run when convenient |
| >4000 chars → warning | ✅ | Counter in UI |
| Hover highlight → explanation | ⏳ | Requires scan with findings |
| Mobile ~375px layout | ⏳ | Visual check recommended |
| 11th scan IP rate limit | **N/A** | Prod requires auth + credits; anonymous IP limit disabled |
| Privacy footer visible (desktop) | ✅ | |
| Calm error copy | ✅ | Sign-in / insufficient credit messages reviewed in code |

---

## Sign-off

Step 0 live smoke test: **complete** for launch purposes. Remaining manual rows are low-risk UI polish.

**Next:** Step 2 — `/legal` landing + outreach.
