-- Initial billing schema (Step 1: consumer accounts + credit ledger)
-- Spec: specs/10_monetization.md §1
-- api_keys table deferred until developer API (Step 3)

create table public.accounts (
  id uuid primary key references auth.users (id) on delete cascade,
  email text not null,
  account_type text not null default 'consumer'
    check (account_type in ('consumer', 'developer', 'legal')),
  credit_balance integer not null default 0
    check (credit_balance >= 0),
  free_trial_granted boolean not null default false,
  stripe_customer_id text,
  subscription_status text not null default 'none'
    check (subscription_status in ('none', 'active', 'canceled')),
  created_at timestamptz not null default now()
);

create unique index accounts_email_idx on public.accounts (email);

create table public.credit_transactions (
  id uuid primary key default gen_random_uuid(),
  account_id uuid not null references public.accounts (id) on delete cascade,
  delta integer not null,
  reason text not null check (reason in (
    'trial_grant',
    'pack_purchase',
    'subscription_renewal',
    'scan_usage',
    'refund',
    'admin_adjustment'
  )),
  stripe_event_id text,
  created_at timestamptz not null default now()
);

create index credit_transactions_account_id_idx
  on public.credit_transactions (account_id);

create unique index credit_transactions_stripe_event_id_idx
  on public.credit_transactions (stripe_event_id)
  where stripe_event_id is not null;

comment on table public.accounts is
  'One row per signed-up user. credit_balance is a cache; ledger is source of truth.';

comment on table public.credit_transactions is
  'Append-only credit ledger. Always insert a row; never adjust balance without one.';

alter table public.accounts enable row level security;
alter table public.credit_transactions enable row level security;

-- Frontend may read own account (balance, subscription_status). Writes via backend service role.
create policy "Users read own account"
  on public.accounts
  for select
  using (auth.uid() = id);

-- credit_transactions: no client policies; backend uses service role key.
