-- Equatile online play. Kept in its own schema so it never touches other apps' data.
-- Not exposed to the public API: only the server function (database owner) reads or writes it.
create schema if not exists equatile;
revoke all on schema equatile from public, anon, authenticated;

create table equatile.games (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  status text not null default 'waiting' check (status in ('waiting', 'active', 'over')),
  board jsonb not null,
  bag jsonb not null,
  turn smallint not null default 0,
  scoreless smallint not null default 0,
  version integer not null default 0,
  log jsonb not null default '[]'::jsonb,
  last jsonb not null default '[]'::jsonb,
  out_seat smallint,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table equatile.players (
  game_id uuid not null references equatile.games (id) on delete cascade,
  seat smallint not null check (seat in (0, 1)),
  name text not null default '',
  token_hash text not null default '',
  rack jsonb not null default '[]'::jsonb,
  score integer not null default 0,
  primary key (game_id, seat)
);

alter table equatile.games enable row level security;
alter table equatile.players enable row level security;
revoke all on all tables in schema equatile from public, anon, authenticated;
create index games_updated_idx on equatile.games (updated_at);
