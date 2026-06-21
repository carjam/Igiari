-- Rollback for 20250620200000_initial_billing_schema.sql
-- Run manually in SQL Editor only if you need to undo the initial billing schema.

drop policy if exists "Users read own account" on public.accounts;

drop table if exists public.credit_transactions;
drop table if exists public.accounts;
