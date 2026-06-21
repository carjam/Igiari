# Supabase — database migrations

Billing schema for Step 1 monetization. Migrations live in `migrations/`.

## Apply migrations (no CLI required)

1. Open Supabase dashboard → **SQL Editor** → **New query**
2. Paste the contents of `migrations/20250620200000_initial_billing_schema.sql`
3. Click **Run**
4. Confirm **Table Editor** shows `accounts` and `credit_transactions`

Re-run after editing a migration only if you roll back first (see `rollbacks/`).

## Optional: Supabase CLI

If you install the CLI later: `supabase link --project-ref YOUR_REF` then `supabase db push`.

## Frontend config

Add to `site-config.js` at the repo root (publishable key only):

```javascript
window.IGIARI_SUPABASE_URL = 'https://YOUR_REFERENCE_ID.supabase.co';
window.IGIARI_SUPABASE_ANON_KEY = 'your-publishable-key';
```

## Backend env (Render)

| Variable | Value |
|----------|--------|
| `SUPABASE_URL` | `https://YOUR_REFERENCE_ID.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Secret key from API Keys |
| `SUPABASE_ANON_KEY` | Publishable key (optional; for future use) |

## Auth redirect URLs

Supabase dashboard → **Authentication** → **URL Configuration**:

- **Site URL:** `https://igiari.pages.dev`
- **Redirect URLs:** `https://igiari.pages.dev/**`

## Rollback

Run `rollbacks/20250620200000_initial_billing_schema.down.sql` in SQL Editor (destroys billing data).
