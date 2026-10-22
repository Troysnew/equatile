# Equatile

A Scrabble-style board game with number tiles. Every line of touching tiles must read as a true equation: `972671` reads as `97 − 26 = 71`.

## What's here

- `index.html`: the whole game in one page (vs computer, pass and play, daily and random puzzles, online play, workbench). Published with GitHub Pages.
- `supabase/functions/equatile/`: the server function for online play. It deals tiles, keeps racks and the bag hidden, and checks every move.
  - `engine.js` is generated from the rules code in `index.html`, so the page and the server always score the same way.
- `supabase/migrations/`: the database tables for online games, in a private `equatile` schema.

## Online play

The page talks to the `equatile` function on Supabase. One player starts a game and shares a 6-character code or an invite link (`#join-CODE`); the other joins with it. No accounts yet.
