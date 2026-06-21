# Frontend (moved to repo root)

Static site files are **not in this folder**. They live at the repository root for Cloudflare Pages deployment:

| File | Purpose |
|------|---------|
| `index.html` | Main page |
| `app.js` | Scan UI + API calls |
| `auth.js` | Supabase sign-in (magic link / OTP) |
| `site-config.js` | Supabase URL + publishable key |
| `styles.css` | Design system |
| `analytics.js` | Cloudflare Web Analytics (optional) |

**Run locally** from repo root:

```bash
python -m http.server 8080
```

Open http://localhost:8080

See [README.md](../README.md) and [docs/DEPLOY_CLOUDFLARE.md](../docs/DEPLOY_CLOUDFLARE.md).
