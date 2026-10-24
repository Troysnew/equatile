-- Co-op online games: two people share one rack (seat 0) against the computer (seat 1).
-- Each teammate has their own key or account, stored in equatile.teammates.
alter table equatile.games add column kind text not null default 'duel' check (kind in ('duel', 'coop'));
alter table equatile.games add column ai_level text check (ai_level in ('easy', 'medium', 'hard'));
create table equatile.teammates (
  game_id uuid not null references equatile.games (id) on delete cascade,
  slot smallint not null check (slot in (0, 1)),
  name text not null default '',
  token_hash text not null default '',
  user_id uuid references auth.users (id) on delete set null,
  primary key (game_id, slot)
);
create index teammates_user_idx on equatile.teammates (user_id) where user_id is not null;
alter table equatile.teammates enable row level security;
revoke all on equatile.teammates from public, anon, authenticated;
