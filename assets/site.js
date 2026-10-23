// Small helpers for the Equacross site: invite-link forwarding, the hero demo, copy buttons.
(function () {
  // Old invite links pointed at the site root. Send them to the game.
  if (/^#join-[A-Za-z0-9]{6}$/.test(location.hash) && document.body.dataset.page === 'home') {
    location.replace('play/' + location.hash);
    return;
  }

  // Copy buttons: <button data-copy="text">
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var text = btn.getAttribute('data-copy'), label = btn.textContent;
      var done = function (msg) { btn.textContent = msg; setTimeout(function () { btn.textContent = label; }, 1800); };
      try {
        navigator.clipboard.writeText(text).then(function () { done('Copied'); }, function () { done('Copy failed. Select it instead.'); });
      } catch (e) { done('Copy failed. Select it instead.'); }
    });
  });

  // Hero demo: 9 _ 2  ->  9 7 2  ->  9 7 2 6 7 1
  var demo = document.getElementById('demo');
  if (!demo) return;
  var PTS = [3, 1, 1, 1, 2, 2, 2, 3, 3, 3];
  var steps = [
    { tiles: [[9], [null], [2]], eq: '', note: 'A 9 and a 2 sit on the board with an empty square between them.' },
    { tiles: [[9], [7, 'new'], [2]], eq: '9 − 7 = 2', note: 'Drop a 7 in the gap. You don’t place any symbols. The game finds the math: 9 − 7 = 2.' },
    { tiles: [[9], [7], [2], [6, 'new'], [7, 'new'], [1, 'new']], eq: '97 − 26 = 71', note: 'Now add 6, 7 and 1. The same 9, 7, 2 become part of a bigger equation: 97 − 26 = 71.' },
  ];
  var tilesEl = demo.querySelector('.tiles'), eqEl = demo.querySelector('.demo-eq'), noteEl = demo.querySelector('.demo-note');
  var dots = Array.prototype.slice.call(demo.querySelectorAll('.demo-steps button'));
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var cur = 2, timer = null, paused = false;

  function eqHTML(s) {
    if (!s) return '<span class="v" style="color:var(--muted)">waiting for a tile</span>';
    return s.split(' ').map(function (p) { return /[−+×÷=]/.test(p) ? '<span class="op">' + p + '</span>' : '<span>' + p + '</span>'; }).join('') + '<span class="v">✓ true</span>';
  }
  function show(i, animate) {
    cur = i;
    var st = steps[i];
    tilesEl.innerHTML = st.tiles.map(function (t) {
      if (t[0] === null) return '<span class="t gap" aria-hidden="true"></span>';
      var cls = 't' + (t[1] ? ' ' + t[1] : '') + (animate && t[1] ? ' drop' : '');
      return '<span class="' + cls + '">' + t[0] + '<small>' + PTS[t[0]] + '</small></span>';
    }).join('');
    tilesEl.setAttribute('aria-label', 'Tiles: ' + st.tiles.map(function (t) { return t[0] === null ? 'empty' : t[0]; }).join(', '));
    eqEl.innerHTML = eqHTML(st.eq);
    noteEl.textContent = st.note;
    dots.forEach(function (d, j) { d.setAttribute('aria-current', j === i ? 'true' : 'false'); });
  }
  function tick() { if (!paused) show((cur + 1) % steps.length, !reduce); }
  dots.forEach(function (d, j) { d.addEventListener('click', function () { show(j, !reduce); restart(); }); });
  function restart() { clearInterval(timer); if (!reduce) timer = setInterval(tick, 3400); }
  demo.addEventListener('mouseenter', function () { paused = true; });
  demo.addEventListener('mouseleave', function () { paused = false; });
  demo.addEventListener('focusin', function () { paused = true; });
  demo.addEventListener('focusout', function () { paused = false; });
  show(2, false);
  if (!reduce) setTimeout(function () { show(0, true); restart(); }, 2600);
})();
