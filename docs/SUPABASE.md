# Supabase — database & auth

Postgres, magic-link auth, and credit ledger for Step 1 monetization.

| | |
|---|---|
| **Project dashboard** | https://supabase.com/dashboard/project/yvkrihgjcoyqytwoisgw |
| **Project URL** | https://yvkrihgjcoyqytwoisgw.supabase.co |
| **SQL Editor** | […/sql](https://supabase.com/dashboard/project/yvkrihgjcoyqytwoisgw/sql) |
| **API keys** | […/settings/api-keys](https://supabase.com/dashboard/project/yvkrihgjcoyqytwoisgw/settings/api-keys) |
| **Auth / SMTP / templates** | […/auth](https://supabase.com/dashboard/project/yvkrihgjcoyqytwoisgw/auth/providers) |

All integrations (Render env, Resend, URLs): **[INTEGRATIONS.md](INTEGRATIONS.md)** · Full rebuild: **[AUTH_AND_EMAIL_RECOVERY.md](AUTH_AND_EMAIL_RECOVERY.md)**

---

## Migrations

Files in `migrations/`. Apply in **SQL Editor** (no CLI required):

1. `20250620200000_initial_billing_schema.sql` — tables + RLS  
2. `20250620210000_grant_billing_api_access.sql` — Data API grants (required if “Automatically expose new tables” was off)

Confirm **Table Editor** shows `accounts` and `credit_transactions`.

**Rollback:** `rollbacks/20250620200000_initial_billing_schema.down.sql` (destroys billing data).

**New project settings:** Data API On · auto-expose new tables Off · automatic RLS On.

---

## Auth & email

| Setting | Value |
|---------|--------|
| Site URL | `https://igiari.us` |
| Redirect URLs | `https://igiari.us/**` |
| SMTP | Resend → `smtp.resend.com:587`, sender `noreply@igiari.us` |
| Magic Link template | [`email-templates/magic-link.html`](email-templates/magic-link.html) |

---

## App configuration

**Frontend** (`site-config.js`):

```javascript
window.IGIARI_SUPABASE_URL = 'https://yvkrihgjcoyqytwoisgw.supabase.co';
window.IGIARI_SUPABASE_ANON_KEY = 'sb_publishable_...'; // publishable key only
```

**Backend** (Render → `igiari-backend` → Environment):

| Variable | Key type |
|----------|----------|
| `SUPABASE_URL` | Project URL (above) |
| `SUPABASE_SERVICE_ROLE_KEY` | Secret key — server only |
| `SUPABASE_ANON_KEY` | Publishable key — JWT verification |

See `backend/.env.example` for local dev.
