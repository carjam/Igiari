# Render Deployment Configuration

**Live API:** https://igiari-backend.onrender.com  
**Dashboard:** https://dashboard.render.com/ → service **igiari-backend**

Integration details (Supabase env, Anthropic): **[docs/INTEGRATIONS.md](../docs/INTEGRATIONS.md)**

---

## Option 1: Using render.yaml (Recommended)

`render.yaml` at repo root — Render auto-detects it on deploy.

---

## Option 2: Manual Configuration

### Service Type
Web Service

### Python Version
**CRITICAL:** **3.11.9** (Settings → Environment). Not 3.13+ (maturin/Rust build errors).

### Build Command
```bash
pip install -r requirements.txt
```

### Start Command
```bash
uvicorn server:app --host 0.0.0.0 --port $PORT
```

### Environment Variables

| Variable | Source |
|----------|--------|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com/settings/keys |
| `SUPABASE_URL` | `https://yvkrihgjcoyqytwoisgw.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase → Settings → API → Secret key |
| `SUPABASE_ANON_KEY` | Supabase → Settings → API → Publishable key |
| `PYTHON_VERSION` | `3.11.9` (optional if `runtime.txt` is used) |

### Root Directory
`backend`

### Region
Closest to users (e.g., Oregon for US West)

### Instance Type
Free (or Starter $7/month for better performance)

### Auto-Deploy
Yes (deploys on git push to connected branch)

---

## Troubleshooting

**Maturin / Rust errors:** Set Python 3.11.9 in dashboard; see `backend/runtime.txt` and `--only-binary=:all:` in `render.yaml`.

**Balance unavailable after sign-in:** Missing `SUPABASE_*` env vars on Render — see [INTEGRATIONS.md](../docs/INTEGRATIONS.md).

**Cold starts:** Free tier sleeps after inactivity (~30s wake).
