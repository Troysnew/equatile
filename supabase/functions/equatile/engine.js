// @ts-nocheck
// Generated from the game page so client and server share identical rules.
const N = 13, MID = 6, CENTER = MID * N + MID, RACK = 7;
const PTS = [3, 1, 1, 1, 2, 2, 2, 3, 3, 3];
const DIST = [7, 12, 11, 10, 9, 8, 8, 7, 7, 7];
const OPBONUS = 5, BINGO = 20, REVEAL_SECS = 30, HINT_RATE = { easy: 0.5, medium: 0.75, hard: 1 }, HINT_DISCOUNTED = 3;
const LEVELS = {
  easy:   { label: 'Easy',   maxLen: 3, budget: 700,  holes: 5 },
  medium: { label: 'Medium', maxLen: 5, budget: 1300, holes: 8 },
  hard:   { label: 'Hard',   maxLen: 7, budget: 2500, holes: 11 },
};
const PREM = Array(N * N).fill(null);
(() => {
  const Q = { '3E': [[0,0],[0,6]], '2E': [[1,1],[2,2],[3,3]], '3T': [[1,5],[5,5]], '2T': [[0,3],[2,6],[4,1]] };
  for (const t in Q) for (const [r, c] of Q[t]) for (const [a, b] of [[r,c],[c,r]])
    for (const [x, y] of [[a,b],[N-1-a,b],[a,N-1-b],[N-1-a,N-1-b]]) PREM[x*N+y] = t;
})();

/* ---------- equations ---------- */
const eqCache = new Map();
function findEqs(s) {
  if (eqCache.has(s)) return eqCache.get(s);
  const n = s.length, out = [];
  const ok = x => x.length === 1 || x[0] !== '0';
  if (n >= 3) for (let i = 1; i <= n - 2; i++) for (let j = i + 1; j <= n - 1; j++) {
    const a = s.slice(0, i), b = s.slice(i, j), c = s.slice(j);
    if (!ok(a) || !ok(b) || !ok(c)) continue;
    const A = +a, B = +b, C = +c;
    const L = (op, bonus) => out.push({ parts: [a, op, b, '=', c], bonus });
    const R = (op, bonus) => out.push({ parts: [a, '=', b, op, c], bonus });
    // A op B = C   (no multiplying by 0 or dividing 0; adding or subtracting 0 is fine)
    if (A + B === C) L('+', false);
    if (A - B === C) L('−', false);
    if (A !== 0 && B !== 0 && A * B === C) L('×', true);
    if (A !== 0 && B !== 0 && A === B * C) L('÷', true);
    // A = B op C
    if (A === B + C) R('+', false);
    if (A === B - C) R('−', false);
    if (B !== 0 && C !== 0 && A === B * C) R('×', true);
    if (B !== 0 && C !== 0 && B === A * C) R('÷', true);
  }
  if (eqCache.size > 200000) eqCache.clear();
  eqCache.set(s, out);
  return out;
}
const bestEq = eqs => eqs.find(e => e.bonus) || eqs[0];

/* ---------- board logic ---------- */
function get(board, ov, r, c) {
  if (r < 0 || r >= N || c < 0 || c >= N) return null;
  const k = r * N + c;
  if (ov && ov.has(k)) return ov.get(k);
  return board[k];
}
function lineRun(board, ov, r, c, dr, dc) {
  while (get(board, ov, r - dr, c - dc) != null) { r -= dr; c -= dc; }
  const cells = []; let s = '';
  for (;;) { const d = get(board, ov, r, c); if (d == null) break; cells.push(r * N + c); s += d; r += dr; c += dc; }
  return { cells, s, dir: dr ? 'v' : 'h' };
}
function hasNeighbor(board, k) {
  const r = Math.floor(k / N), c = k % N;
  return get(board, null, r-1, c) != null || get(board, null, r+1, c) != null || get(board, null, r, c-1) != null || get(board, null, r, c+1) != null;
}
function evaluate(board, pl, fast, empty) {
  const fail = msg => ({ ok: false, msg, runs: [], total: 0 });
  if (!pl.length) return fail('');
  if (empty === undefined) empty = board.every(x => x == null);
  const ov = new Map();
  for (const p of pl) { if (board[p.k] != null) return fail('That square is taken.'); ov.set(p.k, p.d); }
  const rs = new Set(pl.map(p => Math.floor(p.k / N))), cs = new Set(pl.map(p => p.k % N));
  if (rs.size > 1 && cs.size > 1) return fail('Put all your tiles in one row or one column.');
  let dir = null;
  if (pl.length > 1) {
    dir = rs.size === 1 ? 'h' : 'v';
    const ks = pl.map(p => p.k).sort((a, b) => a - b), step = dir === 'h' ? 1 : N;
    for (let k = ks[0]; k <= ks[ks.length - 1]; k += step) if (board[k] == null && !ov.has(k)) return fail('Leave no gaps between your tiles.');
  }
  if (empty) { if (!ov.has(CENTER)) return fail('The first play has to cover the star.'); }
  else if (!pl.some(p => hasNeighbor(board, p.k))) return fail('Connect to the tiles already on the board.');
  const seen = new Set(), runs = [];
  const add = run => { if (run.cells.length < 2) return; const key = run.dir + run.cells[0]; if (seen.has(key)) return; seen.add(key); runs.push(run); };
  const r0 = Math.floor(pl[0].k / N), c0 = pl[0].k % N;
  if (dir) add(lineRun(board, ov, r0, c0, dir === 'v' ? 1 : 0, dir === 'h' ? 1 : 0));
  for (const p of pl) {
    const r = Math.floor(p.k / N), c = p.k % N;
    if (dir !== 'h') add(lineRun(board, ov, r, c, 0, 1));
    if (dir !== 'v') add(lineRun(board, ov, r, c, 1, 0));
  }
  if (!runs.length) return fail(empty ? 'The first play needs at least 3 tiles in a line.' : 'Make a line of at least 3 tiles.');
  let ok = true, total = 0;
  for (const run of runs) {
    if (run.cells.length < 3) { run.err = 'Two tiles side by side can’t make an equation.'; ok = false; if (fast) return fail(''); continue; }
    const eqs = findEqs(run.s);
    if (!eqs.length) { run.err = 'These digits don’t split into a true equation.'; ok = false; if (fast) return fail(''); continue; }
    run.eq = bestEq(eqs);
    let sum = 0, mult = 1;
    for (const k of run.cells) {
      const isNew = ov.has(k), d = isNew ? ov.get(k) : board[k];
      let t = PTS[d];
      if (isNew) { const p = PREM[k]; if (p === '2T') t *= 2; else if (p === '3T') t *= 3; else if (p === '2E') mult *= 2; else if (p === '3E') mult *= 3; }
      sum += t;
    }
    run.score = sum * mult + (run.eq.bonus ? OPBONUS : 0);
    total += run.score;
  }
  const bingo = ok && pl.length >= RACK;
  if (bingo) total += BINGO;
  return { ok, msg: ok ? '' : 'Every line has to be a true equation.', runs, total: ok ? total : 0, bingo };
}

/* ---------- computer moves (same search as the game page, bounded by work instead of time) ---------- */
function uniquePerms(rack, L) {
  const out = [], used = Array(rack.length).fill(false), cur = [];
  (function rec() {
    if (cur.length === L) { out.push(cur.slice()); return; }
    const tried = new Set();
    for (let i = 0; i < rack.length; i++) {
      if (used[i] || tried.has(rack[i])) continue;
      tried.add(rack[i]); used[i] = true; cur.push(i); rec(); cur.pop(); used[i] = false;
    }
  })();
  return out;
}
function searchMoves(board, rack, maxLen, evalLimit, rng = Math.random) {
  const empty = board.every(x => x == null);
  maxLen = Math.min(rack.length, maxLen);
  const segs = [];
  for (const [dr, dc] of [[0, 1], [1, 0]]) for (let line = 0; line < N; line++) for (let st = 0; st < N; st++) {
    let r = dr ? st : line, c = dr ? line : st;
    if (board[r * N + c] != null) continue;
    const cells = [];
    while (r < N && c < N && cells.length < maxLen) {
      const k = r * N + c;
      if (board[k] == null) {
        cells.push(k);
        const L = cells.length;
        if (!(dr && L === 1)) {
          const conn = empty ? (L >= 3 && cells.includes(CENTER)) : cells.some(x => hasNeighbor(board, x));
          if (conn) segs.push(cells.slice());
        }
      }
      r += dr; c += dc;
    }
  }
  for (let i = segs.length - 1; i > 0; i--) { const j = rng() * (i + 1) | 0; [segs[i], segs[j]] = [segs[j], segs[i]]; }
  const perms = {}, moves = [];
  let n = 0;
  outer: for (const seg of segs) {
    const P = perms[seg.length] || (perms[seg.length] = uniquePerms(rack, seg.length));
    for (const perm of P) {
      const pl = seg.map((k, i) => ({ k, d: rack[perm[i]] }));
      const res = evaluate(board, pl, true, empty);
      if (res.ok) moves.push({ pl, total: res.total });
      if (++n >= evalLimit) break outer;
    }
  }
  return moves;
}
function pickMove(moves, level, rng = Math.random) {
  if (!moves.length) return null;
  moves.sort((a, b) => a.total - b.total);
  const n = moves.length;
  if (level === 'hard') return moves[n - 1];
  const [lo, hi] = level === 'easy' ? [0, Math.max(1, Math.ceil(n * 0.5))] : [Math.floor(n * 0.55), Math.max(Math.floor(n * 0.55) + 1, Math.ceil(n * 0.85))];
  return moves[Math.min(n - 1, lo + (rng() * (hi - lo) | 0))];
}

export { N, MID, CENTER, RACK, PTS, DIST, OPBONUS, BINGO, PREM, LEVELS, findEqs, evaluate, get, lineRun, searchMoves, pickMove };
