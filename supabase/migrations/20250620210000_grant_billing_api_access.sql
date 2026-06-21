-- Grant Data API access to billing tables.
-- Required when project has "Automatically expose new tables" disabled (recommended).
-- Run in SQL Editor if account balance shows "Balance unavailable" after sign-in.

grant select, insert, update, delete on public.accounts to service_role;
grant select, insert on public.credit_transactions to service_role;

-- RLS policy "Users read own account" uses the authenticated role.
grant select on public.accounts to authenticated;

notify pgrst, 'reload schema';
