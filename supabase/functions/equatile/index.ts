// @ts-nocheck
// Equacross online play and accounts. All state lives in the private "equatile" schema,
// reached only through this function, so racks and the bag stay hidden.
// A player is identified by their per-game token, or by their signed-in account.
// Co-op games: two teammates share seat 0's rack against the computer in seat 1.
import postgres from 'npm:postgres@3.4.5';
import { N, RACK, PTS, DIST, evaluate, searchMoves, pickMove } from './engine.js';

// Close idle connections quickly: every server instance keeps its own pool, and idle ones used to fill the database.
const sql = postgres(Deno.env.get('SUPABASE_DB_URL'), { prepare: false, max: 2, idle_timeout: 5, max_lifetime: 120, connect_timeout: 10 });
const SUPABASE_URL = Deno.env.get('SUPABASE_URL');
const SERVICE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY');
const ANON_KEY = Deno.env.get('SUPABASE_ANON_KEY');
const cors = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
};
const json = (body, status = 200) => new Response(JSON.stringify(body), { status, headers: { ...cors, 'Content-Type': 'application/json' } });
class Fail extends Error { constructor(msg, status = 400) { super(msg); this.status = status; } }

const rand = n => crypto.getRandomValues(new Uint32Array(n));
function shuffle(a) { const r = rand(a.length); for (let i = a.length - 1; i > 0; i--) { const j = r[i] % (i + 1); [a[i], a[j]] = [a[j], a[i]]; } return a; }
const CODE_CHARS = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
const makeCode = () => Array.from(rand(6), x => CODE_CHARS[x % CODE_CHARS.length]).join('');
const makeToken = () => Array.from(rand(8), x => x.toString(16).padStart(8, '0')).join('');
async function hash(t) { const b = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(t)); return Array.from(new Uint8Array(b), x => x.toString(16).padStart(2, '0')).join(''); }
const cleanName = (s, d) => (String(s || '').replace(/[\u0000-\u001f<>]/g, '').trim().slice(0, 24)) || d;
const draw = (rack, bag) => { while (rack.length < RACK && bag.length) rack.push(bag.pop()); };

async function broadcast(gameId, version) {
  if (!SERVICE_KEY) return;
  try {
    await fetch(`${SUPABASE_URL}/realtime/v1/api/broadcast`, {
      method: 'POST',
      headers: { apikey: SERVICE_KEY, Authorization: `Bearer ${SERVICE_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: [{ topic: `equatile-${gameId}`, event: 'update', payload: { version } }] }),
    });
  } catch (_) { /* clients also poll */ }
}

const teamName = tm => tm.map(t => t.name).filter(Boolean).join(' & ') || 'Your team';
function view(g, ps, seat, co = null) {
  const me = ps.find(p => p.seat === seat);
  const coop = co ? { kind: 'coop', level: g.ai_level, slot: co.slot, team: co.tm.map(t => ({ slot: t.slot, name: t.name })) } : {};
  return {
    ...coop,
    gameId: g.id, code: g.code, status: g.status, version: g.version, turn: g.turn, seat,
    board: g.board, last: g.last, log: g.log.slice(0, 60), bag: g.bag.length, scoreless: g.scoreless, outSeat: g.out_seat,
    players: [0, 1].map(s => { const p = ps.find(x => x.seat === s); return p ? { name: co ? (s === 0 ? teamName(co.tm) : 'Computer') : p.name, score: p.score, tiles: p.rack.length } : null; }),
    rack: me.rack,
  };
}

// The signed-in user, if the request carries a valid Supabase Auth access token.
async function authUser(req) {
  const m = /^Bearer\s+(\S+)$/i.exec(req.headers.get('authorization') || '');
  if (!m || m[1].split('.').length !== 3) return null;   // API keys are not user tokens
  try {
    const r = await fetch(`${SUPABASE_URL}/auth/v1/user`, { headers: { apikey: ANON_KEY || SERVICE_KEY, Authorization: `Bearer ${m[1]}` } });
    if (!r.ok) return null;
    const u = await r.json();
    return u && u.id ? u : null;
  } catch (_) { return null; }
}
const GROUP_MAX = 50, GROUP_LIMIT_PER_USER = 20;
const dayOf = d => { const n = Number(d); if (!Number.isInteger(n) || n < 1 || n > 1e6) throw new Fail('Bad day.'); return n; };
// Current streak ending on `day` (or the day before, if `day` isn't solved yet) and the best ever.
function streaks(daily, day) {
  const ok = id => daily[String(id)] && daily[String(id)].solved;
  let d = ok(day) ? day : day - 1, cur = 0; while (ok(d)) { cur++; d--; }
  const ids = Object.keys(daily).map(Number).filter(ok).sort((a, b) => a - b);
  let best = 0, run = 0; ids.forEach((id, i) => { run = i && ids[i - 1] === id - 1 ? run + 1 : 1; best = Math.max(best, run); });
  return { cur, best };
}
// Removes a member. The longest-standing member takes over a group whose owner leaves; the last one out closes it.
async function leaveGroup(tx, groupId, userId) {
  const [g] = await tx`select * from equatile.groups where id = ${groupId} for update`;
  if (!g) throw new Fail('Group not found.', 404);
  await tx`delete from equatile.group_members where group_id = ${g.id} and user_id = ${userId}`;
  const [next] = await tx`select user_id from equatile.group_members where group_id = ${g.id} order by joined_at limit 1`;
  if (!next) await tx`delete from equatile.groups where id = ${g.id}`;
  else if (g.owner_id === userId) await tx`update equatile.groups set owner_id = ${next.user_id} where id = ${g.id}`;
}
const needUser = b => { if (!b.__user) throw new Fail('Sign in first.', 401); return b.__user; };
const isUuid = x => /^[0-9a-f-]{36}$/.test(String(x));

async function load(tx, gameId, token, lock = true, user = null) {
  if (!/^[0-9a-f-]{36}$/.test(String(gameId))) throw new Fail('Game not found.', 404);
  const [g] = lock ? await tx`select * from equatile.games where id = ${gameId} for update` : await tx`select * from equatile.games where id = ${gameId}`;
  if (!g) throw new Fail('Game not found.', 404);
  const ps = await tx`select * from equatile.players where game_id = ${gameId} order by seat`;
  const h = await hash(String(token || ''));
  if (g.kind === 'coop') {
    const tm = await tx`select * from equatile.teammates where game_id = ${gameId} order by slot`;
    const mt = (token && tm.find(t => t.token_hash === h)) || (user && tm.find(t => t.user_id === user.id));
    if (!mt) throw new Fail('That link or code doesn’t belong to a player in this game.', 403);
    return { g, ps, seat: 0, co: { tm, slot: mt.slot, name: mt.name } };
  }
  const me = (token && ps.find(p => p.token_hash === h)) || (user && ps.find(p => p.user_id === user.id));
  if (!me) throw new Fail('That link or code doesn’t belong to a player in this game.', 403);
  return { g, ps, seat: me.seat, co: null };
}

function endGame(g, ps, outSeat) {
  const left = ps.map(p => p.rack.reduce((s, d) => s + PTS[d], 0));
  ps.forEach((p, i) => { p.score -= left[i]; });
  if (outSeat != null) ps[outSeat].score += left.reduce((a, b, i) => i === outSeat ? a : a + b, 0);
  g.status = 'over'; g.out_seat = outSeat;
}

async function save(tx, g, ps) {
  g.version += 1;
  await tx`update equatile.games set status = ${g.status}, board = ${tx.json(g.board)}, bag = ${tx.json(g.bag)}, turn = ${g.turn},
    scoreless = ${g.scoreless}, version = ${g.version}, log = ${tx.json(g.log)}, last = ${tx.json(g.last)}, out_seat = ${g.out_seat}, updated_at = now()
    where id = ${g.id}`;
  for (const p of ps) await tx`update equatile.players set rack = ${tx.json(p.rack)}, score = ${p.score} where game_id = ${g.id} and seat = ${p.seat}`;
}

function scorelessTurn(g, ps, seat, note, by) {
  g.log.unshift(by ? { who: seat, by, note, pts: 0 } : { who: seat, note, pts: 0 });
  g.scoreless += 1;
  if (g.scoreless >= 6) endGame(g, ps, null); else g.turn = 1 - g.turn;
}

// The computer's reply in a co-op game. Search effort is bounded by work, to stay inside the function's CPU limit.
const AI = { easy: { maxLen: 3, evals: 30000 }, medium: { maxLen: 5, evals: 80000 }, hard: { maxLen: 7, evals: 120000 } };
function computerTurn(g, ps) {
  const ai = ps[1], level = AI[g.ai_level] ? g.ai_level : 'medium', cfg = AI[level];
  const m = pickMove(searchMoves(g.board, ai.rack, cfg.maxLen, cfg.evals), level);
  if (m) {
    const res = evaluate(g.board, m.pl);
    for (const t of m.pl) { g.board[t.k] = t.d; ai.rack.splice(ai.rack.indexOf(t.d), 1); }
    ai.score += res.total; draw(ai.rack, g.bag);
    g.log.unshift({ who: 1, eqs: res.runs.map(r => r.eq.parts), pts: res.total, bingo: res.bingo });
    g.last = m.pl.map(t => t.k); g.scoreless = 0;
    if (!ai.rack.length && !g.bag.length) endGame(g, ps, 1); else g.turn = 0;
  } else if (g.bag.length >= RACK) {
    const old = ai.rack; ai.rack = []; draw(ai.rack, g.bag); g.bag.push(...old); shuffle(g.bag);
    scorelessTurn(g, ps, 1, `Swapped ${old.length} tiles`);
  } else scorelessTurn(g, ps, 1, 'Passed');
}
const afterTeam = (g, ps, co) => { if (co && g.status === 'active' && g.turn === 1) computerTurn(g, ps); };

const actions = {
  async create(b, after) {
    const bag = shuffle(DIST.flatMap((n, d) => Array(n).fill(d)));
    const r0 = [], r1 = []; draw(r0, bag); draw(r1, bag); r1.push(bag.pop()); // second player starts with 8
    const token = makeToken(), h = await hash(token);
    if (b.coop) {
      const level = AI[b.level] ? b.level : 'medium';
      for (let i = 0; i < 5; i++) {
        try {
          return await sql.begin(async tx => {
            const [g] = await tx`insert into equatile.games (code, status, kind, ai_level, board, bag) values (${makeCode()}, 'active', 'coop', ${level}, ${tx.json(Array(N * N).fill(null))}, ${tx.json(bag)}) returning *`;
            await tx`insert into equatile.players (game_id, seat, name, token_hash, rack) values (${g.id}, 0, 'Team', '', ${tx.json(r0)}), (${g.id}, 1, 'Computer', '', ${tx.json(r1)})`;
            await tx`insert into equatile.teammates (game_id, slot, name, token_hash, user_id) values (${g.id}, 0, ${cleanName(b.name, 'Player 1')}, ${h}, ${b.__user ? b.__user.id : null})`;
            const ps = await tx`select * from equatile.players where game_id = ${g.id} order by seat`;
            const tm = await tx`select * from equatile.teammates where game_id = ${g.id} order by slot`;
            return { token, ...view(g, ps, 0, { tm, slot: 0 }) };
          });
        } catch (e) { if (!String(e.message).includes('duplicate')) throw e; }
      }
      throw new Fail('Couldn’t make a game code. Try again.', 500);
    }
    for (let i = 0; i < 5; i++) {
      const code = makeCode();
      try {
        const [g] = await sql`insert into equatile.games (code, board, bag) values (${code}, ${sql.json(Array(N * N).fill(null))}, ${sql.json(bag)}) returning *`;
        await sql`insert into equatile.players (game_id, seat, name, token_hash, rack, user_id) values
          (${g.id}, 0, ${cleanName(b.name, 'Player 1')}, ${h}, ${sql.json(r0)}, ${b.__user ? b.__user.id : null}), (${g.id}, 1, '', '', ${sql.json(r1)}, null)`;
        const ps = await sql`select * from equatile.players where game_id = ${g.id} order by seat`;
        return { token, ...view(g, ps, 0) };
      } catch (e) { if (!String(e.message).includes('duplicate')) throw e; }
    }
    throw new Fail('Couldn’t make a game code. Try again.', 500);
  },
  async join(b, after) {
    const code = String(b.code || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
    return await sql.begin(async tx => {
      const [g] = await tx`select * from equatile.games where code = ${code} for update`;
      if (!g) throw new Fail('No game with that code.', 404);
      const token = makeToken(), uid = b.__user ? b.__user.id : null;
      if (g.kind === 'coop') {
        if (g.status === 'over') throw new Fail('That game is over.', 409);
        const tm0 = await tx`select * from equatile.teammates where game_id = ${g.id} order by slot`;
        if (tm0.length > 1) throw new Fail('That team already has two players.', 409);
        if (uid && tm0[0].user_id === uid) throw new Fail('That’s your own game. Send the code to your teammate.', 409);
        await tx`insert into equatile.teammates (game_id, slot, name, token_hash, user_id) values (${g.id}, 1, ${cleanName(b.name, 'Player 2')}, ${await hash(token)}, ${uid})`;
        const ps = await tx`select * from equatile.players where game_id = ${g.id} order by seat`;
        const tm = await tx`select * from equatile.teammates where game_id = ${g.id} order by slot`;
        await save(tx, g, ps);
        after.push(() => broadcast(g.id, g.version));
        return { token, ...view(g, ps, 0, { tm, slot: 1 }) };
      }
      if (g.status !== 'waiting') throw new Fail('That game already has two players.', 409);
      if (uid) { const [host] = await tx`select user_id from equatile.players where game_id = ${g.id} and seat = 0`; if (host && host.user_id === uid) throw new Fail('That’s your own game. Send the code to someone else.', 409); }
      await tx`update equatile.players set name = ${cleanName(b.name, 'Player 2')}, token_hash = ${await hash(token)}, user_id = ${uid} where game_id = ${g.id} and seat = 1`;
      g.status = 'active';
      const ps = await tx`select * from equatile.players where game_id = ${g.id} order by seat`;
      await save(tx, g, ps);
      after.push(() => broadcast(g.id, g.version));
      return { token, ...view(g, ps, 1) };
    });
  },
  // ---------- accounts ----------
  async me(b) {
    const u = needUser(b);
    const [a] = await sql`select * from equatile.accounts where user_id = ${u.id}`;
    const games = await sql`select g.id, g.code, g.status, g.turn, g.version, g.updated_at, p.seat, p.score, o.name as opp, o.score as opp_score
      from equatile.players p join equatile.games g on g.id = p.game_id
      left join equatile.players o on o.game_id = p.game_id and o.seat = 1 - p.seat
      where p.user_id = ${u.id} order by g.updated_at desc limit 50`;
    const coop = await sql`select g.id, g.code, g.status, g.turn, g.version, g.updated_at, g.ai_level, t.slot, p.score, o.score as opp_score,
        (select t2.name from equatile.teammates t2 where t2.game_id = g.id and t2.slot = 1 - t.slot) as partner
      from equatile.teammates t join equatile.games g on g.id = t.game_id
      join equatile.players p on p.game_id = g.id and p.seat = 0 join equatile.players o on o.game_id = g.id and o.seat = 1
      where t.user_id = ${u.id} order by g.updated_at desc limit 50`;
    return {
      user: { id: u.id, email: u.email || null, provider: (u.app_metadata && u.app_metadata.provider) || null },
      name: a ? a.name : '', devices: a ? a.devices : {}, daily: a ? a.daily : {},
      games: games.map(r => ({ gameId: r.id, code: r.code, status: r.status, seat: r.seat, yourTurn: r.status === 'active' && r.turn === r.seat, score: r.score, opp: r.opp || '', oppScore: r.opp_score || 0, version: r.version, updated: r.updated_at })).concat(
        coop.map(r => ({ gameId: r.id, code: r.code, status: r.status, kind: 'coop', level: r.ai_level, slot: r.slot, partner: r.partner || '', seat: 0, yourTurn: r.status === 'active' && r.turn === 0, score: r.score, opp: 'Computer', oppScore: r.opp_score || 0, version: r.version, updated: r.updated_at }))),
    };
  },
  // Stores this device's stats snapshot and merges daily results; returns the combined account data.
  async sync(b) {
    const u = needUser(b);
    const device = String(b.device || '');
    if (!/^[A-Za-z0-9-]{6,40}$/.test(device)) throw new Fail('Bad device id.');
    const stats = b.stats && typeof b.stats === 'object' ? b.stats : {};
    if (JSON.stringify(stats).length > 20000) throw new Fail('Stats too large.');
    const inDaily = b.daily && typeof b.daily === 'object' ? b.daily : {};
    return await sql.begin(async tx => {
      await tx`insert into equatile.accounts (user_id) values (${u.id}) on conflict (user_id) do nothing`;
      const [a] = await tx`select * from equatile.accounts where user_id = ${u.id} for update`;
      const daily = { ...a.daily };
      for (const [id, r] of Object.entries(inDaily).slice(0, 2000)) {
        if (!/^\d{1,6}$/.test(id) || !r || typeof r !== 'object') continue;
        const clean = { solved: !!r.solved, checks: Math.max(0, r.checks | 0), reveals: Math.max(0, r.reveals | 0), elapsed: Math.max(0, r.elapsed | 0), history: Array.isArray(r.history) ? r.history.filter(x => ['o', 'r', 'x'].includes(x)).slice(0, 60) : [] };
        const cur = daily[id];
        if (!cur || (clean.solved && !cur.solved)) daily[id] = clean;   // first result wins; a solve beats an unsolved try
      }
      const devices = { ...a.devices, [device]: { ...stats, at: Date.now() } };
      await tx`update equatile.accounts set devices = ${tx.json(devices)}, daily = ${tx.json(daily)}, updated_at = now() where user_id = ${u.id}`;
      return { name: a.name, devices, daily };
    });
  },
  // Attaches online games this device holds tokens for to the signed-in account.
  async link(b) {
    const u = needUser(b);
    let linked = 0;
    for (const x of (Array.isArray(b.games) ? b.games : []).slice(0, 50)) {
      if (!x || !isUuid(x.gameId) || !x.token) continue;
      const h = await hash(String(x.token));
      const r = await sql`update equatile.players set user_id = ${u.id} where game_id = ${x.gameId} and token_hash = ${h} and (user_id is null or user_id = ${u.id}) returning seat`;
      const r2 = await sql`update equatile.teammates set user_id = ${u.id} where game_id = ${x.gameId} and token_hash = ${h} and (user_id is null or user_id = ${u.id}) returning slot`;
      linked += r.length + r2.length;
    }
    return { linked };
  },
  async setname(b) {
    const u = needUser(b), name = cleanName(b.name, '');
    await sql`insert into equatile.accounts (user_id, name) values (${u.id}, ${name}) on conflict (user_id) do update set name = ${name}, updated_at = now()`;
    return { name };
  },
  // Deletes the account and its saved data. Online games stay playable on devices that still hold their tokens.
  async deleteAccount(b) {
    const u = needUser(b);
    await sql`update equatile.players set user_id = null where user_id = ${u.id}`;
    await sql`update equatile.teammates set user_id = null where user_id = ${u.id}`;
    await sql`delete from equatile.accounts where user_id = ${u.id}`;
    for (const { group_id } of await sql`select group_id from equatile.group_members where user_id = ${u.id}`) await sql.begin(tx => leaveGroup(tx, group_id, u.id));
    const r = await fetch(`${SUPABASE_URL}/auth/v1/admin/users/${u.id}`, { method: 'DELETE', headers: { apikey: SERVICE_KEY, Authorization: `Bearer ${SERVICE_KEY}` } });
    if (!r.ok) throw new Fail('Couldn’t delete the sign-in. Try again, or email support@equacross.com.', 502);
    return { deleted: true };
  },
  // ---------- daily puzzle groups ----------
  async groupCreate(b) {
    const u = needUser(b), name = cleanName(b.name, '');
    if (!name) throw new Fail('Give the group a name.');
    const [{ n }] = await sql`select count(*)::int as n from equatile.group_members where user_id = ${u.id}`;
    if (n >= GROUP_LIMIT_PER_USER) throw new Fail(`You can be in up to ${GROUP_LIMIT_PER_USER} groups.`, 409);
    for (let i = 0; i < 5; i++) {
      try {
        return await sql.begin(async tx => {
          const [g] = await tx`insert into equatile.groups (code, name, owner_id) values (${makeCode()}, ${name}, ${u.id}) returning *`;
          await tx`insert into equatile.group_members (group_id, user_id) values (${g.id}, ${u.id})`;
          return { group: { id: g.id, code: g.code, name: g.name, owner: true, members: 1 } };
        });
      } catch (e) { if (!String(e.message).includes('duplicate')) throw e; }
    }
    throw new Fail('Couldn’t make a group code. Try again.', 500);
  },
  async groupJoin(b) {
    const u = needUser(b), code = String(b.code || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
    return await sql.begin(async tx => {
      const [g] = await tx`select * from equatile.groups where code = ${code} for update`;
      if (!g) throw new Fail('No group with that code.', 404);
      const [{ n }] = await tx`select count(*)::int as n from equatile.group_members where group_id = ${g.id}`;
      const [mine] = await tx`select 1 from equatile.group_members where group_id = ${g.id} and user_id = ${u.id}`;
      if (!mine) {
        if (n >= GROUP_MAX) throw new Fail(`That group is full (${GROUP_MAX} people).`, 409);
        const [{ m }] = await tx`select count(*)::int as m from equatile.group_members where user_id = ${u.id}`;
        if (m >= GROUP_LIMIT_PER_USER) throw new Fail(`You can be in up to ${GROUP_LIMIT_PER_USER} groups.`, 409);
        await tx`insert into equatile.group_members (group_id, user_id) values (${g.id}, ${u.id})`;
      }
      return { group: { id: g.id, code: g.code, name: g.name, owner: g.owner_id === u.id, members: mine ? n : n + 1 } };
    });
  },
  async groupLeave(b) {
    const u = needUser(b);
    if (!isUuid(b.groupId)) throw new Fail('Group not found.', 404);
    await sql.begin(tx => leaveGroup(tx, b.groupId, u.id));
    return { left: true };
  },
  async groupRemove(b) {
    const u = needUser(b);
    if (!isUuid(b.groupId) || !isUuid(b.userId)) throw new Fail('Not found.', 404);
    const [g] = await sql`select * from equatile.groups where id = ${b.groupId}`;
    if (!g) throw new Fail('Group not found.', 404);
    if (g.owner_id !== u.id) throw new Fail('Only the person who runs the group can remove people.', 403);
    if (b.userId === u.id) throw new Fail('Use Leave group to leave it yourself.');
    await sql`delete from equatile.group_members where group_id = ${g.id} and user_id = ${b.userId}`;
    return { removed: true };
  },
  // Your groups, with how many members have solved the given day's puzzle.
  async groupList(b) {
    const u = needUser(b), day = dayOf(b.day);
    const rows = await sql`select g.id, g.code, g.name, g.owner_id,
        (select count(*)::int from equatile.group_members m where m.group_id = g.id) as members,
        (select count(*)::int from equatile.group_members m join equatile.accounts a on a.user_id = m.user_id
           where m.group_id = g.id and (a.daily -> ${String(day)} ->> 'solved') = 'true') as solved
      from equatile.groups g join equatile.group_members me on me.group_id = g.id and me.user_id = ${u.id}
      order by me.joined_at`;
    return { groups: rows.map(r => ({ id: r.id, code: r.code, name: r.name, owner: r.owner_id === u.id, members: r.members, solved: r.solved })) };
  },
  // One group's members with their result for the day and their streaks.
  // Times and squares stay hidden until the person asking has solved that day's puzzle.
  async groupView(b) {
    const u = needUser(b), day = dayOf(b.day);
    if (!isUuid(b.groupId)) throw new Fail('Group not found.', 404);
    const [g] = await sql`select * from equatile.groups where id = ${b.groupId}`;
    if (!g) throw new Fail('Group not found.', 404);
    const ms = await sql`select m.user_id, m.joined_at, coalesce(a.name, '') as name, coalesce(a.daily, '{}'::jsonb) as daily
      from equatile.group_members m left join equatile.accounts a on a.user_id = m.user_id where m.group_id = ${g.id} order by m.joined_at`;
    const me = ms.find(m => m.user_id === u.id);
    if (!me) throw new Fail('You’re not in that group.', 403);
    const iSolved = !!(me.daily[String(day)] && me.daily[String(day)].solved);
    let anon = 0;
    const members = ms.map(m => {
      const r = m.daily[String(day)], st = streaks(m.daily, day);
      return {
        userId: m.user_id, name: m.name || `Player ${++anon}`, you: m.user_id === u.id, owner: m.user_id === g.owner_id,
        today: r && r.solved ? (iSolved ? { solved: true, checks: r.checks | 0, reveals: r.reveals | 0, elapsed: r.elapsed | 0, history: Array.isArray(r.history) ? r.history.slice(0, 60) : [] } : { solved: true }) : { solved: false },
        streak: st.cur, best: st.best,
      };
    });
    return { group: { id: g.id, code: g.code, name: g.name, owner: g.owner_id === u.id }, day, youSolved: iSolved, members };
  },
  // ---------- games ----------
  async state(b, after) {
    const { g, ps, seat, co } = await load(sql, b.gameId, b.token, false, b.__user);
    return view(g, ps, seat, co);
  },
  async play(b, after) {
    return await sql.begin(async tx => {
      const { g, ps, seat, co } = await load(tx, b.gameId, b.token, true, b.__user);
      if (g.status !== 'active') throw new Fail(g.status === 'waiting' ? 'Waiting for the other player to join.' : 'This game is over.', 409);
      if (g.turn !== seat) throw new Fail('It’s not your turn.', 409);
      const me = ps[seat];
      const raw = Array.isArray(b.placements) ? b.placements : [];
      if (!raw.length || raw.length > me.rack.length) throw new Fail('Place at least one tile.');
      const pl = raw.map(t => ({ k: t.k | 0, d: t.d | 0 }));
      if (pl.some(t => t.k < 0 || t.k >= N * N || t.d < 0 || t.d > 9) || new Set(pl.map(t => t.k)).size !== pl.length) throw new Fail('That play isn’t valid.');
      const rack = me.rack.slice();
      for (const t of pl) { const i = rack.indexOf(t.d); if (i < 0) throw new Fail('Those tiles aren’t all in your rack.'); rack.splice(i, 1); }
      const res = evaluate(g.board, pl);
      if (!res.ok) throw new Fail(res.msg || 'Every line has to be a true equation.');
      for (const t of pl) g.board[t.k] = t.d;
      me.rack = rack; me.score += res.total; draw(me.rack, g.bag);
      g.log.unshift({ who: seat, ...(co ? { by: co.name } : {}), eqs: res.runs.map(r => r.eq.parts), pts: res.total, bingo: res.bingo });
      g.last = pl.map(t => t.k); g.scoreless = 0;
      if (!me.rack.length && !g.bag.length) endGame(g, ps, seat); else g.turn = 1 - seat;
      afterTeam(g, ps, co);
      await save(tx, g, ps);
      after.push(() => broadcast(g.id, g.version));
      return { scored: res.total, ...view(g, ps, seat, co) };
    });
  },
  async swap(b, after) {
    return await sql.begin(async tx => {
      const { g, ps, seat, co } = await load(tx, b.gameId, b.token, true, b.__user);
      if (g.status !== 'active' || g.turn !== seat) throw new Fail('It’s not your turn.', 409);
      const me = ps[seat], digits = (Array.isArray(b.digits) ? b.digits : []).map(d => d | 0);
      if (!digits.length) throw new Fail('Pick tiles to swap.');
      if (g.bag.length < digits.length) throw new Fail(`Only ${g.bag.length} tiles left in the bag.`);
      const rack = me.rack.slice();
      for (const d of digits) { const i = rack.indexOf(d); if (i < 0) throw new Fail('Those tiles aren’t all in your rack.'); rack.splice(i, 1); }
      me.rack = rack; draw(me.rack, g.bag); g.bag.push(...digits); shuffle(g.bag);
      scorelessTurn(g, ps, seat, `Swapped ${digits.length} tile${digits.length > 1 ? 's' : ''}`, co && co.name);
      afterTeam(g, ps, co);
      await save(tx, g, ps);
      after.push(() => broadcast(g.id, g.version));
      return view(g, ps, seat, co);
    });
  },
  async pass(b, after) {
    return await sql.begin(async tx => {
      const { g, ps, seat, co } = await load(tx, b.gameId, b.token, true, b.__user);
      if (g.status !== 'active' || g.turn !== seat) throw new Fail('It’s not your turn.', 409);
      scorelessTurn(g, ps, seat, 'Passed', co && co.name);
      afterTeam(g, ps, co);
      await save(tx, g, ps);
      after.push(() => broadcast(g.id, g.version));
      return view(g, ps, seat, co);
    });
  },
  async resign(b, after) {
    return await sql.begin(async tx => {
      const { g, ps, seat, co } = await load(tx, b.gameId, b.token, true, b.__user);
      if (g.status === 'over') throw new Fail('This game is over.', 409);
      g.log.unshift({ who: seat, ...(co ? { by: co.name } : {}), note: co ? 'Gave up' : 'Resigned', pts: 0 });
      g.status = 'over'; g.out_seat = null;
      ps[seat].score = Math.min(ps[seat].score, ps[1 - seat].score - 1);
      await save(tx, g, ps);
      after.push(() => broadcast(g.id, g.version));
      return view(g, ps, seat, co);
    });
  },
};

Deno.serve(async req => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: cors });
  if (req.method !== 'POST') return json({ error: 'Use POST.' }, 405);
  let body;
  try { body = await req.json(); } catch { return json({ error: 'Bad request.' }, 400); }
  const fn = actions[body?.action];
  if (!fn) return json({ error: 'Unknown action.' }, 400);
  body.__user = await authUser(req);
  const after = [];
  try { const out = await fn(body, after); for (const f of after) await f(); return json(out); }
  catch (e) {
    if (e instanceof Fail) return json({ error: e.message }, e.status);
    console.error(e);
    return json({ error: 'Something went wrong on the server.' }, 500);
  }
});
