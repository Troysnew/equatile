-- Equacross accounts. Sign-in is handled by Supabase Auth; this stores what an account carries
-- between devices. Like the rest of the schema, only the server function reads or writes it.
create table equatile.accounts (
  user_id uuid primary key references auth.users (id) on delete cascade,
  name text not null default '',
  devices jsonb not null default '{}'::jsonb,   -- per-device stats snapshots, combined on read
  daily jsonb not null default '{}'::jsonb,     -- daily puzzle results by puzzle number
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
alter table equatile.accounts enable row level security;
revoke all on equatile.accounts from public, anon, authenticated;

-- An online seat can belong to an account, so the game follows the player to any device.
alter table equatile.players add column user_id uuid references auth.users (id) on delete set null;
create index players_user_idx on equatile.players (user_id) where user_id is not null;
