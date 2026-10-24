-- Daily puzzle groups: friends share a code and see each other's daily results and streaks.
-- Members are accounts; results come from equatile.accounts.daily. Server function access only.
create table equatile.groups (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name text not null,
  owner_id uuid not null references auth.users (id) on delete cascade,
  created_at timestamptz not null default now()
);
create table equatile.group_members (
  group_id uuid not null references equatile.groups (id) on delete cascade,
  user_id uuid not null references auth.users (id) on delete cascade,
  joined_at timestamptz not null default now(),
  primary key (group_id, user_id)
);
create index group_members_user_idx on equatile.group_members (user_id);
create index groups_owner_idx on equatile.groups (owner_id);
alter table equatile.groups enable row level security;
alter table equatile.group_members enable row level security;
revoke all on equatile.groups, equatile.group_members from public, anon, authenticated;
