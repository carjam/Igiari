# Supabase — database & auth

Billing schema and auth/email recovery instructions for Step 1 monetization.

## Migrations

Migrations live in `migrations/`.

### Apply (no CLI required)

1. Supabase dashboard → **SQL Editor** → **New query**
2. Paste and run `migrations/20250620200000_initial_billing_schema.sql`
3. Paste and run `migrations/20250620210000_grant_billing_api_access.sql` if **Automatically expose new tables** was off at project creation
4. Confirm **Table Editor** shows `accounts` and `credit_transactions`

Re-run after editing a migration only if you roll back first (see `rollbacks/`).

### Optional CLI

`supabase link --project-ref YOUR_REF` then `supabase db push`

## Auth, email, SMTP, domain

**Full rebuild runbook:** [`docs/AUTH_AND_EMAIL_RECOVERY.md`](../docs/AUTH_AND_EMAIL_RECOVERY.md)

**Magic Link template (copy-paste):** [`email-templates/magic-link.html`](email-templates/magic-link.html)

## Frontend & backend config

**Frontend** (`site-config.js`):

```javascript
window.IGIARI_SUPABASE_URL = 'https://YOUR_REFERENCE_ID.supabase.co';
window.IGIARI_SUPABASE_ANON_KEY = 'your-publishable-key';
```

**Backend (Render):** `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_ANON_KEY` — see recovery doc.

## Rollback

Run `rollbacks/20250620200000_initial_billing_schema.down.sql` in SQL Editor (destroys billing data).
