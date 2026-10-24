"""Builds the static pages of equacross.com from one shared layout.

Run from the repo root:  python3 tools/build_site.py
The game itself lives in play/index.html and is not touched by this script.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://equacross.com"
EMAIL = "support@equacross.com"
UPDATED = "October 24, 2026"

NAV = [("how-to-play/", "How to play", "how"), ("support/", "Support", "support")]


def logo(pre, h=34):
    """The approved wordmark, with a light-on-dark version for dark mode."""
    w = round(h * 3.948)
    return (f'<img class="logo-light" src="{pre}assets/brand/logo-wordmark.svg" alt="Equacross" width="{w}" height="{h}">'
            f'<img class="logo-dark" src="{pre}assets/brand/logo-wordmark-on-dark.svg" alt="Equacross" width="{w}" height="{h}">')


ICONS = {
    "trophy": '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M14 8h20v8a10 10 0 0 1-20 0z" fill="var(--coral)"/><path d="M14 11H8.5a4.5 4.5 0 0 0 5.7 6.6M34 11h5.5a4.5 4.5 0 0 1-5.7 6.6" fill="none" stroke="var(--coral)" stroke-width="3.2" stroke-linecap="round"/><rect x="21.5" y="25" width="5" height="8" rx="1.5" fill="var(--coral)"/><rect x="15" y="33" width="18" height="6" rx="2.5" fill="var(--coral)"/></svg>',
    "brain": '<svg viewBox="0 0 48 48" aria-hidden="true"><path d="M23 9.5a6 6 0 0 0-11 2.2 6 6 0 0 0-4.6 9.6 6 6 0 0 0 2.3 9.6A6 6 0 0 0 20 36.5a4.6 4.6 0 0 0 3 2z" fill="#7FA66C"/><path d="M25 9.5a6 6 0 0 1 11 2.2 6 6 0 0 1 4.6 9.6 6 6 0 0 1-2.3 9.6A6 6 0 0 1 28 36.5a4.6 4.6 0 0 1-3 2z" fill="#7FA66C"/><path d="M16 17c2 0 3.5 1.4 3.5 3.4M13.5 26c2.2-.3 4 .9 4.6 2.8M32 17c-2 0-3.5 1.4-3.5 3.4M34.5 26c-2.2-.3-4 .9-4.6 2.8" fill="none" stroke="#E2EBD6" stroke-width="2.4" stroke-linecap="round"/></svg>',
    "calendar": '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="7" y="10" width="34" height="30" rx="6" fill="var(--coral)"/><rect x="7" y="10" width="34" height="9" rx="4" fill="#A93127"/><rect x="14" y="6" width="4" height="9" rx="2" fill="var(--forest-ink)"/><rect x="30" y="6" width="4" height="9" rx="2" fill="var(--forest-ink)"/><g fill="#FFF8E8"><rect x="13" y="23" width="6" height="5" rx="1.2"/><rect x="21" y="23" width="6" height="5" rx="1.2"/><rect x="29" y="23" width="6" height="5" rx="1.2"/><rect x="13" y="31" width="6" height="5" rx="1.2"/><rect x="21" y="31" width="6" height="5" rx="1.2"/></g></svg>',
    "device": '<svg viewBox="0 0 48 48" aria-hidden="true"><rect x="13" y="5" width="22" height="38" rx="5" fill="#7FA66C"/><rect x="16.5" y="10" width="15" height="24" rx="2" fill="#E2EBD6"/><circle cx="24" cy="38.5" r="1.8" fill="#E2EBD6"/><path d="M19.5 18.5h8.5l-2.6-2.6M28.5 25.5H20l2.6 2.6" fill="none" stroke="#193B2C" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    "people": '<svg viewBox="0 0 48 48" aria-hidden="true"><circle cx="24" cy="15" r="6.5" fill="#6FA0C9"/><path d="M12 38c0-7 5.4-12 12-12s12 5 12 12z" fill="#6FA0C9"/><circle cx="11.5" cy="19" r="4.6" fill="var(--blue)"/><path d="M3 37c0-5.2 3.8-9 8.5-9 2 0 3.8.6 5.2 1.7A15 15 0 0 0 11 37z" fill="var(--blue)"/><circle cx="36.5" cy="19" r="4.6" fill="var(--blue)"/><path d="M45 37c0-5.2-3.8-9-8.5-9-2 0-3.8.6-5.2 1.7A15 15 0 0 1 37 37z" fill="var(--blue)"/></svg>',
}


SPARK = ('<svg class="spark" viewBox="-14 -48 70 42" aria-hidden="true"><g stroke="var(--coral)" stroke-width="10" stroke-linecap="round" fill="none">'
         '<line x1="0" y1="-19" x2="-8" y2="-34"/><line x1="17" y1="-21" x2="19" y2="-42"/><line x1="33" y1="-14" x2="49" y2="-27"/></g></svg>')


def page(path, key, title, desc, body, base=None):
    """path: output file relative to ROOT. base: prefix for relative links."""
    depth = path.count("/")
    pre = base if base is not None else "../" * depth
    nav = "".join(
        f'<a class="{"hide-sm" if k == "how" else ""}" href="{pre}{href}"{" aria-current=\"page\"" if k == key else ""}>{label}</a>'
        for href, label, k in NAV)
    canon = SITE + "/" + (path[:-len("index.html")] if path.endswith("index.html") else path)
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Equacross">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#FBF9F3" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0E1C15" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{pre}favicon.ico" sizes="48x48">
<link rel="icon" href="{pre}assets/brand/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{pre}assets/brand/apple-touch-icon.png">
<link rel="manifest" href="{pre}site.webmanifest">
<link rel="preload" href="{pre}assets/fonts/nunito-sans-latin-900-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{pre}assets/fonts/nunito-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{pre}assets/site.css">
</head>
<body data-page="{key}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap">
    <a class="brand" href="{pre if pre else './'}" aria-label="Equacross home"><img class="brand-mark" src="{pre}assets/brand/nav-mark.svg" alt="" width="34" height="34">{logo(pre, 34)}</a>
    <nav class="nav" aria-label="Main">{nav}<a class="btn primary" href="{pre}play/">Play</a></nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-foot">
  <div class="wrap">
    <div style="display:flex;flex-direction:column;gap:8px">
      <a class="brand" href="{pre if pre else './'}" aria-label="Equacross home">{logo(pre, 30)}</a>
      <p class="fine">Every line is an equation.</p>
    </div>
    <nav class="foot-links" aria-label="Footer">
      <a href="{pre}play/">Play</a><a href="{pre}how-to-play/">How to play</a><a href="{pre}support/">Support</a><a href="{pre}privacy/">Privacy</a><a href="{pre}terms/">Terms</a>
    </nav>
    <p class="fine" style="flex-basis:100%">© 2026 Equacross. Questions? <a href="mailto:{EMAIL}">{EMAIL}</a></p>
  </div>
</footer>
<script src="{pre}assets/site.js" defer></script>
</body>
</html>
"""
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("wrote", path)


def tiles(s, new=()):
    pts = [3, 1, 1, 1, 2, 2, 2, 3, 3, 3]
    out = []
    for i, ch in enumerate(s):
        if ch == "_":
            out.append('<span class="t gap" aria-hidden="true"></span>')
        else:
            out.append(f'<span class="t{" new" if i in new else ""}">{ch}<small>{pts[int(ch)]}</small></span>')
    return f'<div class="tiles" aria-label="Tiles {" ".join(c if c != "_" else "empty" for c in s)}">{"".join(out)}</div>'


def eq(s):
    return " ".join(f'<span class="op">{p}</span>' if p in "+−×÷=" else p for p in s.split(" "))


# ---------------------------------------------------------------- home
HOME = f"""
<section class="hero">
  <div class="wrap">
    <div class="hero-copy">
      <span class="eyebrow">A word game for numbers</span>
      <h1>Every line is<br>an equation<span class="op">.</span></h1>
      <p class="lede">Place digit tiles like Scrabble. Equacross finds the math hiding in every line you build, and scores it.</p>
      <div class="cta-row">
        <a class="btn primary big" href="play/">Play in your browser</a>
        <span class="soon">iPhone app coming soon</span>
      </div>
    </div>
    <figure class="hero-art" aria-label="Three Equacross number tiles, 9, 7 and 2, on a game board">
      <div class="hero-board" aria-hidden="true">{"".join(f'<i class="c{c}"></i>' for c in "lmbclmlmlmlmlmlbmlmlcmlml")}</div>
      <span class="ht ht1" aria-hidden="true">9</span><span class="ht ht2" aria-hidden="true">7</span><span class="ht ht3" aria-hidden="true">2</span>{SPARK}
    </figure>
  </div>
</section>

<section class="features" aria-label="Why Equacross">
  <div class="wrap feature-row">
    <div class="feature">{ICONS["trophy"]}<h3>Fun strategy</h3><p>Plan ahead for bigger scores.</p></div>
    <div class="feature">{ICONS["brain"]}<h3>Quick to learn</h3><p>Simple rules, deep gameplay.</p></div>
    <div class="feature">{ICONS["calendar"]}<h3>Daily puzzle</h3><p>A new challenge every day.</p></div>
    <div class="feature">{ICONS["people"]}<h3>Play with friends</h3><p>Challenge anyone, anywhere.</p></div>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div class="copy">
      <span class="eyebrow">How it works</span>
      <h2>You place digits. Equacross finds the math.</h2>
      <p>There are no symbol tiles. Put digits next to each other, and the game reads the line as an equation: it works out where the operator and the equals sign go.</p>
      <p>Extend a line and it’s read again, so the same tiles can become part of a bigger equation.</p>
    </div>
    <div class="demo" id="demo" aria-live="polite">
      <span class="eyebrow">How a line reads</span>
      <div class="tiles" aria-label="Tiles 9, 7, 2, 6, 7, 1">
        <span class="t">9<small>3</small></span><span class="t">7<small>3</small></span><span class="t">2<small>1</small></span><span class="t new">6<small>2</small></span><span class="t new">7<small>3</small></span><span class="t new">1<small>1</small></span>
      </div>
      <div class="demo-eq"><span>97</span><span class="op">−</span><span>26</span><span class="op">=</span><span>71</span><span class="v">✓ true</span></div>
      <p class="demo-note">Add 6, 7 and 1 to 972, and the same digits become part of a bigger equation: 97 − 26 = 71.</p>
      <div class="demo-steps" role="group" aria-label="Demo steps">
        <button type="button" aria-label="Step 1: the empty square" aria-current="false"></button>
        <button type="button" aria-label="Step 2: drop a 7" aria-current="false"></button>
        <button type="button" aria-label="Step 3: add 6, 7, 1" aria-current="true"></button>
      </div>
    </div>
  </div>
</section>

<section class="section" id="modes">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Ways to play</span>
      <h2>One board, four ways to play</h2>
      <p>Play a quick round against the computer, sit down with a friend, or settle into the daily puzzle.</p>
    </div>
    <div class="modes">
      <article class="mode">
        <span class="mode-icon mi-trophy">{ICONS["trophy"]}</span>
        <div class="mode-body">
        <span class="tag">Solo</span>
        <h3>Vs the computer</h3>
        <p>Three levels, from short safe plays to an opponent that hunts for the highest-scoring move every turn.</p>
        <div class="pills"><span class="pill">Easy</span><span class="pill">Medium</span><span class="pill">Hard</span></div>
        </div>
      </article>
      <article class="mode">
        <span class="mode-icon mi-people">{ICONS["people"]}</span>
        <div class="mode-body">
        <span class="tag">Online</span>
        <h3>Vs a friend, anywhere</h3>
        <p>Start a game and send a six-character code. Take turns at your own pace. Each player sees only their own tiles, and the server checks every move.</p>
        <div class="pills"><span class="pill">Invite by code</span><span class="pill">No account needed</span></div>
        </div>
      </article>
      <article class="mode">
        <span class="mode-icon mi-device">{ICONS["device"]}</span>
        <div class="mode-body">
        <span class="tag">Same device</span>
        <h3>Pass and play</h3>
        <p>Share one phone or tablet. Your rack stays hidden until you hand it over.</p>
        </div>
      </article>
      <article class="mode">
        <span class="mode-icon mi-calendar">{ICONS["calendar"]}</span>
        <div class="mode-body">
        <span class="tag">Daily</span>
        <h3>The daily puzzle</h3>
        <p>A partly built board, a handful of tiles, and one goal: make every line true. Everyone gets the same puzzle each day.</p>
        <div class="pills"><span class="pill">New at midnight</span><span class="pill">Random puzzles too</span></div>
        </div>
      </article>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div class="copy">
      <span class="eyebrow">Daily puzzle</span>
      <h2>Share the solve, not the answer</h2>
      <p>Fill the outlined squares so every line across and down is true. When you solve it, you get a result to share: a red square for each wrong check, yellow for each tile you revealed, green for the solve.</p>
      <p>Any arrangement that works counts, even if it isn’t the one the puzzle started with.</p>
    </div>
    <div class="result" aria-label="Example shared result">
      <span class="ex-tag">Example result</span>
      <span>Equacross Daily #1</span>
      <span class="sq" aria-hidden="true">🟥🟨🟩</span>
      <span class="meta">Solved in 3:41 · 2 checks · 1 reveal</span>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap split">
    <div class="bench" aria-label="Workbench example">
      <span class="eyebrow">Workbench</span>
      <div class="screen"><span class="t dark">9</span><span class="t dark">7</span><span class="sym">−</span><span class="t dark">2</span><span class="t mine">6</span><span class="sym">=</span><span class="t mine">7</span><span class="t mine">1</span></div>
      <span class="num">97 − 26 = 71</span>
      <span class="check">✓ Uses all 3 base tiles, in order. Fits on the board going across.</span>
    </div>
    <div class="copy">
      <span class="eyebrow">Workbench</span>
      <h2>Work it out before you commit</h2>
      <p>Tap a line of tiles on the board, then open the Workbench. It’s a calculator built from your tiles: try operators, check the math, and see if the play fits on the board and what it would score.</p>
      <p>When it works, one tap puts the tiles on the board.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Scoring</span>
      <h2>Harder math, bigger scores</h2>
      <p>Every tile in a line counts, including the ones already on the board, so building on long equations pays off.</p>
    </div>
    <div class="scoring">
      <div class="score-card"><h3>Tile points</h3><p>1, 2 and 3 score 1 point. 4, 5 and 6 score 2. 7, 8, 9 and 0 score 3.</p></div>
      <div class="score-card"><h3>Premium squares</h3><p>Double and triple a tile, or double and triple the whole equation.</p></div>
      <div class="score-card"><h3>Bonuses</h3><p>+5 for an equation with × or ÷. +20 for using all 7 tiles in one play.</p></div>
    </div>
    <p style="margin-top:28px"><a href="how-to-play/">Read the full rules</a></p>
  </div>
</section>

<section class="cta-band">
  <div class="wrap">
    <h2>Find the equation in 972671.</h2>
    <a class="btn" href="play/">Play now</a>
  </div>
</section>
"""
page("index.html", "home", "Equacross: every line is an equation",
     "Equacross is a Scrabble-style game with number tiles. Build lines of digits, and the game finds the equation in each one. Play the computer, a friend, or the daily puzzle.",
     HOME, base="")

# ---------------------------------------------------------------- how to play
HOW = f"""
<section class="doc-hero"><div class="wrap">
  <span class="eyebrow">Rules</span>
  <h1>How to play</h1>
  <p>Everything you need to play Equacross, from your first move to the daily puzzle.</p>
  <p class="cta-row"><a class="btn primary" href="../play/#tutorial">Play the 1-minute tutorial</a></p>
</div></section>
<div class="wrap doc">
  <nav class="toc" aria-label="On this page"><strong>On this page</strong>
    <a href="#basics">The basics</a><a href="#reading">How lines are read</a><a href="#rules">Equation rules</a><a href="#placing">Placing tiles</a>
    <a href="#scoring">Scoring</a><a href="#turns">Other turn options</a><a href="#ending">Ending the game</a><a href="#workbench">Workbench</a>
    <a href="#online">Online games</a><a href="#puzzles">Puzzles</a>
  </nav>
  <article class="prose">
    <h2 id="basics">The basics</h2>
    <p>Each player draws 7 number tiles. On your turn, place one or more tiles in a single row or column, touching the tiles already on the board. Every line of touching tiles, across and down, has to read as a true equation.</p>
    <p>You never place symbols. You only place digits, and the game works out where the operator and the equals sign go.</p>

    <h2 id="reading">How lines are read</h2>
    <div class="example">
      {tiles("9_2")}
      <p>A 9 and a 2 sit on the board with an empty square between them.</p>
    </div>
    <div class="example">
      {tiles("972", new=(1,))}
      <span class="eqline">{eq("9 − 7 = 2")}</span>
      <p>Drop a 7 in the gap, and the line reads as 9 − 7 = 2.</p>
    </div>
    <div class="example">
      {tiles("972671", new=(3, 4, 5))}
      <span class="eqline">{eq("97 − 26 = 71")}</span>
      <p>Add 6, 7 and 1, and the whole line is read again. Digits next to each other join into bigger numbers, so it now reads as 97 − 26 = 71.</p>
    </div>

    <h2 id="rules">Equation rules</h2>
    <ul>
      <li>Every equation has exactly one operator and one equals sign. Operators are <span class="num">+ − × ÷</span>.</li>
      <li>The equals sign can come last or first. <span class="num">972</span> reads as <span class="num">9 − 7 = 2</span>, and <span class="num">297</span> reads as <span class="num">2 = 9 − 7</span>.</li>
      <li>Lines are read left to right and top to bottom.</li>
      <li>Multiplying by 0 and dividing 0 don’t count. Adding or subtracting 0 is fine: <span class="num">7 + 0 = 7</span> works, and so does <span class="num">7 − 7 = 0</span>.</li>
      <li>Division has to come out even, and results can’t be negative.</li>
      <li>Numbers with more than one digit can’t start with 0.</li>
      <li>Two tiles side by side can never be an equation, so every line of touching tiles needs at least 3.</li>
    </ul>

    <h2 id="placing">Placing tiles</h2>
    <ul>
      <li>All the tiles you place in a turn go in one row or one column, with no gaps between them. Tiles already on the board can sit between yours.</li>
      <li>The first play of the game covers the star in the middle and uses at least 3 tiles.</li>
      <li>After that, every play has to touch a tile that’s already on the board.</li>
      <li>The second player starts with 8 tiles instead of 7, to make up for going second. After their first play, racks refill to 7.</li>
    </ul>

    <h2 id="scoring">Scoring</h2>
    <p>Each line you make is scored separately, and the scores are added together. A line scores the points of every tile in it, including tiles that were already on the board.</p>
    <div class="table-wrap"><table>
      <thead><tr><th>Digits</th><th>Points each</th></tr></thead>
      <tbody><tr><td class="num">1, 2, 3</td><td class="num">1</td></tr><tr><td class="num">4, 5, 6</td><td class="num">2</td></tr><tr><td class="num">7, 8, 9, 0</td><td class="num">3</td></tr></tbody>
    </table></div>
    <div class="table-wrap"><table>
      <thead><tr><th>Square</th><th>What it does</th></tr></thead>
      <tbody>
        <tr><td><span class="sw" style="background:#cde0ef">2T</span></td><td>Doubles the points of the tile placed on it.</td></tr>
        <tr><td><span class="sw" style="background:#8db3d6">3T</span></td><td>Triples the points of the tile placed on it.</td></tr>
        <tr><td><span class="sw" style="background:#f3d1c8">2E</span></td><td>Doubles the whole equation.</td></tr>
        <tr><td><span class="sw" style="background:#e2907e">3E</span></td><td>Triples the whole equation.</td></tr>
      </tbody>
    </table></div>
    <ul>
      <li>Premium squares only count on the turn a tile is placed on them.</li>
      <li>Tile multipliers apply first, then equation multipliers.</li>
      <li>An equation that uses × or ÷ earns <span class="num">+5</span>, added after multipliers.</li>
      <li>Using all 7 tiles in one play earns <span class="num">+20</span>.</li>
    </ul>
    <p class="note">Example: you place a 7 between a 9 and a 2, and your 7 is on a 2E square. The line 9 − 7 = 2 scores (3 + 3 + 1) × 2 = 14 points.</p>

    <h2 id="turns">Other turn options</h2>
    <ul>
      <li><strong>Swap:</strong> trade any of your tiles for new ones from the bag. It uses your turn and scores nothing.</li>
      <li><strong>Pass:</strong> skip your turn.</li>
      <li><strong>Show a move:</strong> the game places a move for you, but it costs points: 50% of that move’s score against the Easy computer, 75% against Medium, and 100% against Hard or another person. From your 4th hint in a game, every hint costs 100%. You get one hint per turn. Hints aren’t available in online games.</li>
    </ul>

    <h2 id="ending">Ending the game</h2>
    <ul>
      <li>The game ends when the bag is empty and a player uses their last tile, or after 6 scoreless turns in a row.</li>
      <li>The points on any tiles left in your rack are subtracted from your score. A player who uses their last tile also collects the other player’s leftover points.</li>
    </ul>

    <h2 id="workbench">Workbench</h2>
    <p>Tap a tile on the board, or drag across a line of tiles, to pick a base. Then open the Workbench. It shows your base tiles and your own tiles, plus calculator keys.</p>
    <ul>
      <li>Tap tiles and symbols to build an equation. The Workbench does the math as you go.</li>
      <li>It checks that you used every base tile in order, with your tiles only before or after them, and that the play fits on the board.</li>
      <li>When everything checks out, it shows the score and can place the tiles for you. You still press Play to score them.</li>
      <li>With no base selected, it works as scratch math.</li>
    </ul>

    <h2 id="online">Online games</h2>
    <ul>
      <li>Choose <strong>New game</strong>, then <strong>Online</strong>, then <strong>Start a game</strong>. You get a 6-character code and a link to send.</li>
      <li>Your friend chooses <strong>Join a game</strong> and enters the code, or opens your link.</li>
      <li>Take turns whenever you like. The board updates when the other player moves.</li>
      <li>Your game is saved on the device you started or joined it on. Open <strong>My games</strong> there to switch to it. You can have several online games going at once.</li>
    </ul>

    <h2 id="puzzles">Puzzles</h2>
    <ul>
      <li>A puzzle gives you a partly built board with outlined empty squares, and exactly the tiles needed to fill them.</li>
      <li>Fill every outlined square so every line is true, then press <strong>Check</strong>. Lines that don’t work turn red.</li>
      <li>Any arrangement that works counts.</li>
      <li><strong>Reveal a tile</strong> places one correct tile for you and adds 30 seconds to your time.</li>
      <li>The daily puzzle is the same for everyone and changes at midnight your time. Random puzzles come in Easy (5 tiles), Medium (8) and Hard (11).</li>
    </ul>
    <p><a class="btn primary" href="../play/">Play Equacross</a></p>
  </article>
</div>
"""
page("how-to-play/index.html", "how", "How to play Equacross",
     "The full rules of Equacross: how lines of digits are read as equations, placing tiles, scoring, online games and the daily puzzle.", HOW)

# ---------------------------------------------------------------- support
SUPPORT = f"""
<section class="doc-hero"><div class="wrap">
  <span class="eyebrow">Support</span>
  <h1>Get help</h1>
  <p>Answers to common questions, and how to reach us.</p>
</div></section>
<div class="wrap doc">
  <div class="contact-card" style="align-self:start">
    <h2 style="font-size:1.4rem">Contact us</h2>
    <p>For help, bug reports, feedback or feature ideas, email:</p>
    <span class="mail">{EMAIL}</span>
    <div class="copy-row"><a class="btn primary" href="mailto:{EMAIL}?subject=Equacross%20support">Send an email</a><button class="btn" type="button" data-copy="{EMAIL}">Copy address</button></div>
    <p class="fine">If you’re reporting a problem with an online game, include the 6-character game code.</p>
  </div>
  <div class="prose">
    <h2 id="faq">Common questions</h2>
    <div class="faq">
      <details><summary>Why won’t the game accept my play?</summary><div>
        <p>Every line of touching tiles, across and down, has to read as a true equation, including lines your tiles create sideways. The panel next to the board shows which line failed and why.</p>
        <p>Common causes: two tiles side by side with nothing else in the line, a number that starts with 0, or multiplying by 0 or dividing 0, which don’t count. See <a href="../how-to-play/#rules">the equation rules</a>.</p>
      </div></details>
      <details><summary>How do I play online with a friend?</summary><div>
        <p>Choose New game, then Online, then Start a game. Send your friend the 6-character code or the link. They choose Join a game and enter the code, or just open the link.</p>
      </div></details>
      <details><summary>Where are my games? Can I play more than one at a time?</summary><div>
        <p>Yes. Every game you start is saved on that device: games against the computer, pass and play, puzzles and online games. Tap <strong>My games</strong> to see them all and switch between them. Online games that are waiting on you say “Your turn.”</p>
        <p>Games are saved in the browser you played them in. Clearing your browser’s data for this site, or using a private window, removes them from that device.</p>
      </div></details>
      <details><summary>When does the daily puzzle change?</summary><div>
        <p>At midnight in your own time zone. Everyone gets the same puzzle on the same date.</p>
      </div></details>
      <details><summary>Why did my score go down?</summary><div>
        <p>Using Show a move costs points, and at the end of the game the points on any tiles left in your rack are subtracted. See <a href="../how-to-play/#turns">turn options</a> and <a href="../how-to-play/#ending">ending the game</a>.</p>
      </div></details>
      <details><summary>Does Equacross cost anything?</summary><div>
        <p>Playing in your browser is free. Details for the iPhone app will be listed on the App Store when it’s released.</p>
      </div></details>
      <details><summary>How do I delete my data?</summary><div>
        <p>Games against the computer, pass and play, and puzzles are stored only on your device. Clearing your browser’s data for this site removes them.</p>
        <p>For online games, email <a href="mailto:{EMAIL}">{EMAIL}</a> with the game code and we’ll delete that game from our server. See the <a href="../privacy/">privacy policy</a> for details.</p>
      </div></details>
    </div>
  </div>
</div>
"""
page("support/index.html", "support", "Equacross support",
     "Get help with Equacross: common questions about rules, online games and the daily puzzle, and how to contact us.", SUPPORT)

# ---------------------------------------------------------------- privacy
PRIVACY = f"""
<section class="doc-hero"><div class="wrap">
  <span class="eyebrow">Legal</span>
  <h1>Privacy policy</h1>
  <p class="updated">Last updated {UPDATED}</p>
</div></section>
<div class="wrap doc">
  <nav class="toc" aria-label="On this page"><strong>On this page</strong>
    <a href="#summary">Summary</a><a href="#device">On your device</a><a href="#accounts">Accounts</a><a href="#online">Online games</a><a href="#providers">Service providers</a>
    <a href="#use">How we use data</a><a href="#retention">How long we keep it</a><a href="#children">Children</a><a href="#choices">Your choices</a><a href="#changes">Changes</a><a href="#contact">Contact</a>
  </nav>
  <article class="prose">
    <p>This policy explains what information Equacross (“Equacross,” “we,” “us”) collects when you use the Equacross website at equacross.com and the Equacross apps, and how it’s used.</p>

    <h2 id="summary">Summary</h2>
    <ul>
      <li>Accounts are optional. You can play every mode without one.</li>
      <li>There are no ads and no analytics or tracking.</li>
      <li>Games against the computer, pass and play, and puzzles stay on your device.</li>
      <li>Online games store the name you enter and the game itself on our server so both players can play.</li>
      <li>We don’t sell your information or share it for advertising.</li>
    </ul>

    <h2 id="device">Information stored on your device</h2>
    <p>Equacross saves your current game, your daily puzzle results and your settings in your browser’s or device’s local storage, so you can pick up where you left off. This information stays on your device and isn’t sent to us, except for online games as described below.</p>

    <h2 id="accounts">Accounts (optional)</h2>
    <p>You can sign in with Apple, Google or your email address to keep your stats, daily puzzle results and online games on every device. If you sign in, we store:</p>
    <ul>
      <li>Your email address and the sign-in method you used. If you use Sign in with Apple and choose to hide your email, we receive a private relay address from Apple instead.</li>
      <li>An account ID created by our sign-in service.</li>
      <li>The name you choose to show other players, if you set one.</li>
      <li>Your game stats (such as wins, best move and longest equation) from each device you use, and your daily puzzle results.</li>
      <li>Which online games your account is playing.</li>
      <li>The groups you start or join, and each group’s name and invite code.</li>
    </ul>
    <p>We use this only to run your account and sync your games. We don’t send you marketing email. Sign-in emails contain a one-time code or link.</p>
    <p><strong>Groups.</strong> If you join a group, its other members can see the name you chose, whether you’ve solved each daily puzzle, your daily puzzle streaks, and, once they’ve solved that day’s puzzle themselves, your time, checks, reveals and result squares for it. They don’t see your email address. The person who runs a group can remove members, and you can leave a group at any time.</p>
    <p>You can delete your account at any time from the Account screen in the game. That deletes your sign-in, the stats and results stored with it, and your group memberships. Games saved on your device stay there, and online games keep working on devices that already have them.</p>

    <h2 id="online">Online games</h2>
    <p>When you start or join an online game, we store on our server:</p>
    <ul>
      <li>The name you enter, up to 24 characters. You don’t have to use your real name.</li>
      <li>The game: the board, each player’s tiles, scores, the list of moves, and the 6-character game code.</li>
      <li>A scrambled (hashed) version of a random player key. The key itself is created on our server and saved on your device so you can rejoin your game. We keep only the scrambled version, which can’t be turned back into the key.</li>
    </ul>
    <p>The other player in your game can see the name you entered, the board, the scores and the moves. They can’t see your tiles.</p>
    <p>In a team game against the computer, you and your teammate share one set of tiles, so each of you sees the team’s tiles and the tiles the other is trying on the board before playing them. Neither of you sees the computer’s tiles.</p>

    <h2 id="providers">Service providers</h2>
    <p>Like any website, the services that deliver Equacross receive standard technical information, such as your IP address, browser type and the time of each request, and may keep it in their logs. We use:</p>
    <ul>
      <li><strong>Supabase</strong>, which hosts our server and database for online games and runs account sign-in.</li>
      <li><strong>Apple</strong> and <strong>Google</strong>, if you choose to sign in with them.</li>
      <li><strong>GitHub Pages</strong>, which hosts this website.</li>
      <li><strong>jsDelivr</strong>, which delivers a code library used for live online game updates.</li>
    </ul>
    <p>These providers process information under their own privacy policies. We don’t use them to track you.</p>

    <h2 id="use">How we use information</h2>
    <ul>
      <li>To run online games: dealing tiles, checking moves, keeping scores, and telling each player when it’s their turn.</li>
      <li>To sign you in and keep your stats, results and games in sync across your devices.</li>
      <li>To keep games fair, for example by rejecting moves from someone who isn’t in the game.</li>
      <li>To fix problems and keep the service working.</li>
      <li>To answer you when you contact us.</li>
    </ul>
    <p>We may also disclose information if the law requires it.</p>

    <h2 id="retention">How long we keep it</h2>
    <p>We keep account data until you delete your account. We keep online game records so players can return to their games. We may delete old or inactive games at any time. If you email us, we keep your message and our reply for as long as we need them to help you.</p>

    <h2 id="children">Children</h2>
    <p>Equacross is a general audience game. We don’t ask for anyone’s age, and the only personal information online play asks for is a name, which can be a nickname. Accounts are optional and need only an email address or an Apple or Google sign-in. We don’t knowingly collect personal information from children under 13. If you’re a parent or guardian and think your child has given us personal information, email us and we’ll delete it.</p>

    <h2 id="choices">Your choices</h2>
    <ul>
      <li>You can play every mode except online without sending us any information, and you never need an account.</li>
      <li>You can delete your account and its data from the Account screen in the game.</li>
      <li>You can remove everything stored on your device by clearing your browser’s or device’s data for Equacross.</li>
      <li>You can ask us to delete an online game by emailing us with its game code.</li>
    </ul>

    <h2 id="changes">Changes to this policy</h2>
    <p>If we change how Equacross handles information, we’ll update this page and the date at the top.</p>

    <h2 id="contact">Contact</h2>
    <p>Questions about privacy? Email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
  </article>
</div>
"""
page("privacy/index.html", "privacy", "Equacross privacy policy",
     "How Equacross handles information: optional accounts, no ads or tracking. Offline games stay on your device; online games store your chosen name and the game.", PRIVACY)

# ---------------------------------------------------------------- terms
TERMS = f"""
<section class="doc-hero"><div class="wrap">
  <span class="eyebrow">Legal</span>
  <h1>Terms of use</h1>
  <p class="updated">Last updated {UPDATED}</p>
</div></section>
<div class="wrap doc">
  <nav class="toc" aria-label="On this page"><strong>On this page</strong>
    <a href="#using">Using Equacross</a><a href="#conduct">Fair play</a><a href="#ip">Ownership</a><a href="#apple">App Store</a><a href="#warranty">No warranty</a><a href="#liability">Liability</a><a href="#changes">Changes</a><a href="#law">Governing law</a><a href="#contact">Contact</a>
  </nav>
  <article class="prose">
    <p>These terms apply to the Equacross website at equacross.com and the Equacross apps. By using Equacross, you agree to them.</p>

    <h2 id="using">Using Equacross</h2>
    <p>You may use Equacross for your own personal, non-commercial entertainment. We may change, pause or stop any part of Equacross, including online play, at any time.</p>

    <h2 id="conduct">Fair play</h2>
    <ul>
      <li>Don’t use names that are offensive, hateful, or that impersonate someone else.</li>
      <li>Don’t try to cheat, interfere with other players’ games, or access games you aren’t part of.</li>
      <li>Don’t try to disrupt, overload or break the service.</li>
    </ul>
    <p>We may delete games or block access when these terms are broken.</p>

    <h2 id="ip">Ownership</h2>
    <p>The Equacross name, game design, artwork and software belong to Equacross. These terms don’t give you any ownership of them.</p>

    <h2 id="apple">Apps from the App Store</h2>
    <p>If you got Equacross from Apple’s App Store, Apple’s Licensed Application End User License Agreement also applies. If it conflicts with these terms, Apple’s agreement controls for the app.</p>

    <h2 id="warranty">No warranty</h2>
    <p>Equacross is provided “as is” and “as available,” without warranties of any kind, to the extent the law allows. We don’t promise that it will always be available or free of errors, or that saved games will never be lost.</p>

    <h2 id="liability">Limitation of liability</h2>
    <p>To the extent the law allows, Equacross isn’t liable for indirect, incidental or consequential damages, or for lost data, arising from your use of Equacross.</p>

    <h2 id="changes">Changes to these terms</h2>
    <p>We may update these terms. When we do, we’ll change the date at the top. Continuing to use Equacross after an update means you accept the new terms.</p>

    <h2 id="law">Governing law</h2>
    <p>These terms are governed by the laws of the State of Georgia, USA, except where the law of your home country requires otherwise.</p>

    <h2 id="contact">Contact</h2>
    <p>Questions about these terms? Email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
  </article>
</div>
"""
page("terms/index.html", "terms", "Equacross terms of use",
     "The terms for using the Equacross website and apps: fair play, ownership, and the usual legal fine print.", TERMS)

# ---------------------------------------------------------------- 404
NOTFOUND = """
<section class="hero"><div class="wrap" style="grid-template-columns:minmax(0,1fr)">
  <div class="hero-copy">
    <span class="eyebrow">Page not found</span>
    <h1>This page doesn’t add up<span class="op">.</span></h1>
    <p class="lede">404 is a true line in Equacross (4 = 0 + 4), but this page doesn’t exist. The link may have a typo, or the page may have moved.</p>
    <div class="cta-row"><a class="btn primary" href="/play/">Play Equacross</a><a class="btn" href="/">Go to the home page</a></div>
  </div>
</div></section>
"""
page("404.html", "404", "Page not found · Equacross", "This page doesn’t exist.", NOTFOUND, base="/")
