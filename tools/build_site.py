"""Builds the static pages of equatile.com from one shared layout.

Run from the repo root:  python3 tools/build_site.py
The game itself lives in play/index.html and is not touched by this script.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://equatile.com"
EMAIL = "support@equatile.com"
UPDATED = "October 22, 2026"
FONTS = ("https://fonts.googleapis.com/css2?family=Azeret+Mono:wght@500;700;800"
         "&family=Bricolage+Grotesque:opsz,wght@12..96,700;12..96,800"
         "&family=Instrument+Sans:wght@400;500;600;700&display=swap")

NAV = [("how-to-play/", "How to play", "how"), ("support/", "Support", "support")]


def mark():
    return ('<svg class="brand-mark" viewBox="0 0 64 64" aria-hidden="true"><rect x="4" y="4" width="56" height="56" rx="12" fill="var(--tile)"/>'
            '<rect x="4" y="50" width="56" height="10" rx="5" fill="var(--tile-edge)"/><rect x="4" y="44" width="56" height="10" fill="var(--tile)"/>'
            '<rect x="17" y="22" width="30" height="6" rx="3" fill="var(--pencil)"/><rect x="17" y="34" width="30" height="6" rx="3" fill="var(--pencil)"/></svg>')


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
<meta property="og:site_name" content="Equatile">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#e3edd6" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#16251c" media="(prefers-color-scheme: dark)">
<link rel="icon" href="{pre}assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{pre}assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{FONTS}">
<link rel="stylesheet" href="{pre}assets/site.css">
</head>
<body data-page="{key}">
<a class="skip" href="#main">Skip to content</a>
<header class="site-head">
  <div class="wrap">
    <a class="brand" href="{pre if pre else './'}" aria-label="Equatile home">{mark()}<span>Equa<span class="eq">tile</span></span></a>
    <nav class="nav" aria-label="Main">{nav}<a class="btn primary" href="{pre}play/">Play</a></nav>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-foot">
  <div class="wrap">
    <div style="display:flex;flex-direction:column;gap:8px">
      <a class="brand" href="{pre if pre else './'}">{mark()}<span>Equa<span class="eq">tile</span></span></a>
      <p class="fine">Every line is an equation.</p>
    </div>
    <nav class="foot-links" aria-label="Footer">
      <a href="{pre}play/">Play</a><a href="{pre}how-to-play/">How to play</a><a href="{pre}support/">Support</a><a href="{pre}privacy/">Privacy</a><a href="{pre}terms/">Terms</a>
    </nav>
    <p class="fine" style="flex-basis:100%">© 2026 Equatile. Questions? <a href="mailto:{EMAIL}">{EMAIL}</a></p>
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
      <h1>Every line is an equation<span class="op">.</span></h1>
      <p class="lede">Place digit tiles like Scrabble. Equatile finds the math hiding in every line you build, and scores it.</p>
      <div class="cta-row">
        <a class="btn primary" href="play/">Play in your browser</a>
        <span class="soon">iPhone app coming soon</span>
      </div>
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
        <span class="tag">Solo</span>
        <h3>Vs the computer</h3>
        <p>Three levels, from short safe plays to an opponent that hunts for the highest-scoring move every turn.</p>
        <div class="pills"><span class="pill">Easy</span><span class="pill">Medium</span><span class="pill">Hard</span></div>
      </article>
      <article class="mode">
        <span class="tag">Online</span>
        <h3>Vs a friend, anywhere</h3>
        <p>Start a game and send a six-character code. Take turns at your own pace. Each player sees only their own tiles, and the server checks every move.</p>
        <div class="pills"><span class="pill">Invite by code</span><span class="pill">No account needed</span></div>
      </article>
      <article class="mode">
        <span class="tag">Same device</span>
        <h3>Pass and play</h3>
        <p>Share one phone or tablet. Your rack stays hidden until you hand it over.</p>
      </article>
      <article class="mode">
        <span class="tag">Daily</span>
        <h3>The daily puzzle</h3>
        <p>A partly built board, a handful of tiles, and one goal: make every line true. Everyone gets the same puzzle each day.</p>
        <div class="pills"><span class="pill">New at midnight</span><span class="pill">Random puzzles too</span></div>
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
      <span>Equatile Daily #1</span>
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
page("index.html", "home", "Equatile: every line is an equation",
     "Equatile is a Scrabble-style game with number tiles. Build lines of digits, and the game finds the equation in each one. Play the computer, a friend, or the daily puzzle.",
     HOME, base="")

# ---------------------------------------------------------------- how to play
HOW = f"""
<section class="doc-hero"><div class="wrap">
  <span class="eyebrow">Rules</span>
  <h1>How to play</h1>
  <p>Everything you need to play Equatile, from your first move to the daily puzzle.</p>
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
      <li>Adding 0, subtracting 0, multiplying by 0 and dividing 0 don’t count. Results of 0 are fine: <span class="num">7 − 7 = 0</span> works.</li>
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
      <li>Your game is saved on the device you started it on. Open Equatile on that device to pick it back up.</li>
    </ul>

    <h2 id="puzzles">Puzzles</h2>
    <ul>
      <li>A puzzle gives you a partly built board with outlined empty squares, and exactly the tiles needed to fill them.</li>
      <li>Fill every outlined square so every line is true, then press <strong>Check</strong>. Lines that don’t work turn red.</li>
      <li>Any arrangement that works counts.</li>
      <li><strong>Reveal a tile</strong> places one correct tile for you and adds 30 seconds to your time.</li>
      <li>The daily puzzle is the same for everyone and changes at midnight your time. Random puzzles come in Easy (5 tiles), Medium (8) and Hard (11).</li>
    </ul>
    <p><a class="btn primary" href="../play/">Play Equatile</a></p>
  </article>
</div>
"""
page("how-to-play/index.html", "how", "How to play Equatile",
     "The full rules of Equatile: how lines of digits are read as equations, placing tiles, scoring, online games and the daily puzzle.", HOW)

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
    <div class="copy-row"><a class="btn primary" href="mailto:{EMAIL}?subject=Equatile%20support">Send an email</a><button class="btn" type="button" data-copy="{EMAIL}">Copy address</button></div>
    <p class="fine">If you’re reporting a problem with an online game, include the 6-character game code.</p>
  </div>
  <div class="prose">
    <h2 id="faq">Common questions</h2>
    <div class="faq">
      <details><summary>Why won’t the game accept my play?</summary><div>
        <p>Every line of touching tiles, across and down, has to read as a true equation, including lines your tiles create sideways. The panel next to the board shows which line failed and why.</p>
        <p>Common causes: two tiles side by side with nothing else in the line, a number that starts with 0, or a trick with 0 like adding 0 or multiplying by 0. See <a href="../how-to-play/#rules">the equation rules</a>.</p>
      </div></details>
      <details><summary>How do I play online with a friend?</summary><div>
        <p>Choose New game, then Online, then Start a game. Send your friend the 6-character code or the link. They choose Join a game and enter the code, or just open the link.</p>
      </div></details>
      <details><summary>My online game disappeared. How do I get it back?</summary><div>
        <p>Online games are saved on the device and browser you started or joined them on. Open Equatile there to pick the game back up. Clearing your browser’s data for this site, or using a private window, removes the saved game from that device.</p>
      </div></details>
      <details><summary>When does the daily puzzle change?</summary><div>
        <p>At midnight in your own time zone. Everyone gets the same puzzle on the same date.</p>
      </div></details>
      <details><summary>Why did my score go down?</summary><div>
        <p>Using Show a move costs points, and at the end of the game the points on any tiles left in your rack are subtracted. See <a href="../how-to-play/#turns">turn options</a> and <a href="../how-to-play/#ending">ending the game</a>.</p>
      </div></details>
      <details><summary>Does Equatile cost anything?</summary><div>
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
page("support/index.html", "support", "Equatile support",
     "Get help with Equatile: common questions about rules, online games and the daily puzzle, and how to contact us.", SUPPORT)

# ---------------------------------------------------------------- privacy
PRIVACY = f"""
<section class="doc-hero"><div class="wrap">
  <span class="eyebrow">Legal</span>
  <h1>Privacy policy</h1>
  <p class="updated">Last updated {UPDATED}</p>
</div></section>
<div class="wrap doc">
  <nav class="toc" aria-label="On this page"><strong>On this page</strong>
    <a href="#summary">Summary</a><a href="#device">On your device</a><a href="#online">Online games</a><a href="#providers">Service providers</a>
    <a href="#use">How we use data</a><a href="#retention">How long we keep it</a><a href="#children">Children</a><a href="#choices">Your choices</a><a href="#changes">Changes</a><a href="#contact">Contact</a>
  </nav>
  <article class="prose">
    <p>This policy explains what information Equatile (“Equatile,” “we,” “us”) collects when you use the Equatile website at equatile.com and the Equatile apps, and how it’s used.</p>

    <h2 id="summary">Summary</h2>
    <ul>
      <li>There are no accounts, no ads and no analytics or tracking.</li>
      <li>Games against the computer, pass and play, and puzzles stay on your device.</li>
      <li>Online games store the name you enter and the game itself on our server so both players can play.</li>
      <li>We don’t sell your information or share it for advertising.</li>
    </ul>

    <h2 id="device">Information stored on your device</h2>
    <p>Equatile saves your current game, your daily puzzle results and your settings in your browser’s or device’s local storage, so you can pick up where you left off. This information stays on your device and isn’t sent to us, except for online games as described below.</p>

    <h2 id="online">Online games</h2>
    <p>When you start or join an online game, we store on our server:</p>
    <ul>
      <li>The name you enter, up to 24 characters. You don’t have to use your real name.</li>
      <li>The game: the board, each player’s tiles, scores, the list of moves, and the 6-character game code.</li>
      <li>A scrambled (hashed) version of a random player key. The key itself is created on our server and saved on your device so you can rejoin your game. We keep only the scrambled version, which can’t be turned back into the key.</li>
    </ul>
    <p>The other player in your game can see the name you entered, the board, the scores and the moves. They can’t see your tiles.</p>

    <h2 id="providers">Service providers</h2>
    <p>Like any website, the services that deliver Equatile receive standard technical information, such as your IP address, browser type and the time of each request, and may keep it in their logs. We use:</p>
    <ul>
      <li><strong>Supabase</strong>, which hosts our server and database for online games.</li>
      <li><strong>GitHub Pages</strong>, which hosts this website.</li>
      <li><strong>Google Fonts</strong>, which provides the typefaces.</li>
      <li><strong>jsDelivr</strong>, which delivers a code library used for live online game updates.</li>
    </ul>
    <p>These providers process information under their own privacy policies. We don’t use them to track you.</p>

    <h2 id="use">How we use information</h2>
    <ul>
      <li>To run online games: dealing tiles, checking moves, keeping scores, and telling each player when it’s their turn.</li>
      <li>To keep games fair, for example by rejecting moves from someone who isn’t in the game.</li>
      <li>To fix problems and keep the service working.</li>
      <li>To answer you when you contact us.</li>
    </ul>
    <p>We may also disclose information if the law requires it.</p>

    <h2 id="retention">How long we keep it</h2>
    <p>We keep online game records so players can return to their games. We may delete old or inactive games at any time. If you email us, we keep your message and our reply for as long as we need them to help you.</p>

    <h2 id="children">Children</h2>
    <p>Equatile is a general audience game. We don’t ask for anyone’s age, and the only personal information online play asks for is a name, which can be a nickname. We don’t knowingly collect personal information from children under 13. If you’re a parent or guardian and think your child has given us personal information, email us and we’ll delete it.</p>

    <h2 id="choices">Your choices</h2>
    <ul>
      <li>You can play every mode except online without sending us any information.</li>
      <li>You can remove everything stored on your device by clearing your browser’s or device’s data for Equatile.</li>
      <li>You can ask us to delete an online game by emailing us with its game code.</li>
    </ul>

    <h2 id="changes">Changes to this policy</h2>
    <p>If we change how Equatile handles information, we’ll update this page and the date at the top.</p>

    <h2 id="contact">Contact</h2>
    <p>Questions about privacy? Email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
  </article>
</div>
"""
page("privacy/index.html", "privacy", "Equatile privacy policy",
     "How Equatile handles information: no accounts, ads or tracking. Offline games stay on your device; online games store your chosen name and the game.", PRIVACY)

# ---------------------------------------------------------------- terms
TERMS = f"""
<section class="doc-hero"><div class="wrap">
  <span class="eyebrow">Legal</span>
  <h1>Terms of use</h1>
  <p class="updated">Last updated {UPDATED}</p>
</div></section>
<div class="wrap doc">
  <nav class="toc" aria-label="On this page"><strong>On this page</strong>
    <a href="#using">Using Equatile</a><a href="#conduct">Fair play</a><a href="#ip">Ownership</a><a href="#apple">App Store</a><a href="#warranty">No warranty</a><a href="#liability">Liability</a><a href="#changes">Changes</a><a href="#law">Governing law</a><a href="#contact">Contact</a>
  </nav>
  <article class="prose">
    <p>These terms apply to the Equatile website at equatile.com and the Equatile apps. By using Equatile, you agree to them.</p>

    <h2 id="using">Using Equatile</h2>
    <p>You may use Equatile for your own personal, non-commercial entertainment. We may change, pause or stop any part of Equatile, including online play, at any time.</p>

    <h2 id="conduct">Fair play</h2>
    <ul>
      <li>Don’t use names that are offensive, hateful, or that impersonate someone else.</li>
      <li>Don’t try to cheat, interfere with other players’ games, or access games you aren’t part of.</li>
      <li>Don’t try to disrupt, overload or break the service.</li>
    </ul>
    <p>We may delete games or block access when these terms are broken.</p>

    <h2 id="ip">Ownership</h2>
    <p>The Equatile name, game design, artwork and software belong to Equatile. These terms don’t give you any ownership of them.</p>

    <h2 id="apple">Apps from the App Store</h2>
    <p>If you got Equatile from Apple’s App Store, Apple’s Licensed Application End User License Agreement also applies. If it conflicts with these terms, Apple’s agreement controls for the app.</p>

    <h2 id="warranty">No warranty</h2>
    <p>Equatile is provided “as is” and “as available,” without warranties of any kind, to the extent the law allows. We don’t promise that it will always be available or free of errors, or that saved games will never be lost.</p>

    <h2 id="liability">Limitation of liability</h2>
    <p>To the extent the law allows, Equatile isn’t liable for indirect, incidental or consequential damages, or for lost data, arising from your use of Equatile.</p>

    <h2 id="changes">Changes to these terms</h2>
    <p>We may update these terms. When we do, we’ll change the date at the top. Continuing to use Equatile after an update means you accept the new terms.</p>

    <h2 id="law">Governing law</h2>
    <p>These terms are governed by the laws of the State of Georgia, USA, except where the law of your home country requires otherwise.</p>

    <h2 id="contact">Contact</h2>
    <p>Questions about these terms? Email <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
  </article>
</div>
"""
page("terms/index.html", "terms", "Equatile terms of use",
     "The terms for using the Equatile website and apps: fair play, ownership, and the usual legal fine print.", TERMS)

# ---------------------------------------------------------------- 404
NOTFOUND = """
<section class="hero"><div class="wrap" style="grid-template-columns:minmax(0,1fr)">
  <div class="hero-copy">
    <span class="eyebrow">Page not found</span>
    <h1>404 isn’t an equation<span class="op">.</span></h1>
    <p class="lede">And this page doesn’t exist. 4 − 0 = 4 would need subtracting 0, which Equatile doesn’t allow. The link may have a typo, or the page may have moved.</p>
    <div class="cta-row"><a class="btn primary" href="/play/">Play Equatile</a><a class="btn" href="/">Go to the home page</a></div>
  </div>
</div></section>
"""
page("404.html", "404", "Page not found · Equatile", "This page doesn’t exist.", NOTFOUND, base="/")
