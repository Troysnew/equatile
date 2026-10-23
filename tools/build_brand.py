"""Builds the Equacross logo and icon assets as outlined SVG (no font needed to display them),
then renders the PNG/ICO sizes with headless Chromium.

Run from the repo root:  python3 tools/build_brand.py
Needs: fonttools, brotli, uharfbuzz, playwright (Chromium), Pillow.
"""
import io, math
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
import uharfbuzz as hb

ROOT = Path(__file__).resolve().parent.parent
FONTS, OUT = ROOT / "assets/fonts", ROOT / "assets/brand"
OUT.mkdir(parents=True, exist_ok=True)

# Approved palette
FOREST, CORAL, SAGE, CREAM, BLUE = "#193B2C", "#C83C30", "#E2EBD6", "#FFF8E8", "#91B9D8"
SAGE_D, SAGE_DD, CORAL_L, TILE_EDGE = "#CFDDBF", "#B9CCA6", "#EE9C92", "#D9CBA6"


def load(name):
    f = TTFont(str(FONTS / name))          # woff2 decoded via brotli
    buf = io.BytesIO(); f.flavor = None; f.save(buf)
    data = buf.getvalue()
    face = hb.Face(data); font = hb.Font(face)
    return TTFont(io.BytesIO(data)), font, face.upem


NUN_W = load("../../tools/fonts/nunito-latin-900-normal.woff2")   # Nunito Black (rounded): wordmark only, not shipped
NUN_B = load("nunito-sans-latin-700-normal.woff2")
NUN_K = load("nunito-sans-latin-900-normal.woff2")
KIT = ROOT / "tools/kit"   # the approved handoff SVGs


def text_paths(fontpack, text, size, x, y, tracking=0.0):
    """Shape text with HarfBuzz and return [(char_index, svg_path_d)], plus the advance width."""
    tt, font, upem = fontpack
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": False})
    gs, order = tt.getGlyphSet(), tt.getGlyphOrder()
    s = size / upem; pen_x = 0; out = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        sp = SVGPathPen(gs)
        tp = TransformPen(sp, (s, 0, 0, -s, x + (pen_x + pos.x_offset) * s, y - pos.y_offset * s))
        gs[name].draw(tp)
        out.append((info.cluster, sp.getCommands()))
        pen_x += pos.x_advance + tracking * upem
    return out, (pen_x - tracking * upem) * s


def bbox_of(fontpack, text, size):
    tt, font, upem = fontpack
    from fontTools.pens.boundsPen import BoundsPen
    paths, w = text_paths(fontpack, text, size, 0, 0)
    gs, order = tt.getGlyphSet(), tt.getGlyphOrder()
    return w


def spark(ox, oy, em, color=CORAL):
    """The three coral accent strokes, using the geometry from the supplied handoff wordmark."""
    k = em * 0.95 / 110
    segs = [((0, -19), (-8, -34)), ((17, -21), (19, -42)), ((33, -14), (49, -27))]
    lines = "".join(f'<line x1="{ox + x1 * k:.1f}" y1="{oy + y1 * k:.1f}" x2="{ox + x2 * k:.1f}" y2="{oy + y2 * k:.1f}"/>' for (x1, y1), (x2, y2) in segs)
    return f'<g stroke="{color}" stroke-width="{10 * k:.1f}" stroke-linecap="round" fill="none">{lines}</g>'


# Small per-letter tilt (degrees) and baseline lift (em) that give the hand-set, bouncy feel of the approved logo.
BOUNCE = [(-3, 0.0), (2, 0.012), (0, 0.0), (-2, 0.006), (2.5, 0.0), (-2.5, 0.01), (1.5, 0.0), (-2, 0.008), (3, 0.0)]


def wordmark(equa=FOREST, cross=CORAL, tagline=None, tag_color=None):
    """Outlined wordmark: Nunito Black, tightened, thickened with a round-joined outline, each letter slightly tilted."""
    from fontTools.pens.boundsPen import BoundsPen
    size = 200
    tt, font, upem = NUN_W
    sc = size / upem
    buf = hb.Buffer(); buf.add_str("Equacross"); buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True})
    gs, order = tt.getGlyphSet(), tt.getGlyphOrder()
    track = -0.035 * upem
    pen_x = 0; parts = []; boxes = []
    thick = size * 0.05
    for i, (info, pos) in enumerate(zip(buf.glyph_infos, buf.glyph_positions)):
        name = order[info.codepoint]
        sp = SVGPathPen(gs); x0 = pen_x * sc
        gs[name].draw(TransformPen(sp, (sc, 0, 0, -sc, x0, 0)))
        bp = BoundsPen(gs); gs[name].draw(bp); xmin, ymin, xmax, ymax = bp.bounds
        cx = x0 + (xmin + xmax) / 2 * sc
        rot, lift = BOUNCE[i]
        color = equa if i < 4 else cross
        parts.append(f'<path d="{sp.getCommands()}" fill="{color}" stroke="{color}" stroke-width="{thick:.1f}" stroke-linejoin="round" '
                     f'transform="translate(0 {-lift * size:.1f}) rotate({rot} {cx:.1f} {-size * 0.3:.1f})"/>')
        boxes.append((x0 + xmin * sc, x0 + xmax * sc, ymax * sc))
        pen_x += pos.x_advance + (track if i < 8 else 0)
    w = boxes[-1][1] + thick / 2
    xh = boxes[-1][2]
    s1, s2 = boxes[7], boxes[8]
    ox = (s1[0] + s1[1]) / 2 + size * 0.11
    oy = -xh - thick / 2 + size * 0.065
    body = "".join(parts) + spark(ox, oy, size * 1.02)
    cap = size * 0.72
    min_y = min(-cap - thick, oy - size * 0.42) - size * 0.03
    pad = size * 0.04
    view_h = -min_y + size * 0.27
    if tagline:
        tsize = size * 0.155
        tpaths, tw = text_paths(NUN_B, tagline, tsize, 0, 0, tracking=0.2)
        tx = w - tw
        ty = size * 0.17 + tsize * 1.0
        td = " ".join(d for _, d in tpaths)
        body += f'<path fill="{tag_color or "#5E7366"}" transform="translate({tx:.1f},{ty:.1f})" d="{td}"/>'
        view_h = -min_y + ty + tsize * 0.32
    x_min = boxes[0][0] - thick / 2 - pad
    vb = f"{x_min:.1f} {min_y:.1f} {w - x_min + pad:.1f} {view_h:.1f}"
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="Equacross"><title>Equacross</title>{body}</svg>\n'


def tile(x, y, s, digit=None, rot=0, shadow=True, edge=TILE_EDGE, face=CREAM):
    """A raised cream tile with a bottom edge. s = side length."""
    r = s * 0.2
    g = [f'<g transform="rotate({rot} {x + s / 2:.1f} {y + s / 2:.1f})">']
    if shadow:
        g.append(f'<rect x="{x + s * 0.03:.1f}" y="{y + s * 0.12:.1f}" width="{s:.1f}" height="{s:.1f}" rx="{r:.1f}" fill="#193B2C" fill-opacity="0.18"/>')
    g.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{s:.1f}" height="{s:.1f}" rx="{r:.1f}" fill="{edge}"/>')
    g.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{s:.1f}" height="{s * 0.9:.1f}" rx="{r:.1f}" fill="{face}"/>')
    g.append(f'<rect x="{x + s * 0.06:.1f}" y="{y + s * 0.05:.1f}" width="{s * 0.88:.1f}" height="{s * 0.3:.1f}" rx="{r * 0.8:.1f}" fill="#FFFFFF" fill-opacity="0.45"/>')
    if digit is not None:
        ds = s * 0.78
        paths, dw = text_paths(NUN_K, str(digit), ds, 0, 0)
        d = " ".join(p for _, p in paths)
        g.append(f'<path fill="{FOREST}" transform="translate({x + (s - dw) / 2:.1f},{y + s * 0.45 + ds * 0.36:.1f})" d="{d}"/>')
    g.append("</g>")
    return "".join(g)


def outline_digits(svg):
    """Replace the handoff icon's <text> numerals with Nunito Sans Black outlines so they render the same everywhere."""
    import re
    def rep(m):
        x, y, size, digit = float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4)
        paths, dw = text_paths(NUN_K, digit, size, 0, 0)
        d = " ".join(p for _, p in paths)
        return f'<path fill="{FOREST}" transform="translate({x - dw / 2:.1f},{y + size * 0.02:.1f})" d="{d}"/>'
    return re.sub(r'<text x="([\d.]+)" y="([\d.]+)" text-anchor="middle"[^>]*font-size="([\d.]+)"[^>]*>(\d)</text>', rep, svg)


def kit_icon(full_bleed=False, safe=1.0):
    """The supplied primary app icon, with outlined numerals. full_bleed fills the square (Apple, maskable)."""
    svg = outline_digits((KIT / "equacross-app-icon.svg").read_text())
    svg = svg.replace('width="1024" height="1024" ', '').replace('<svg ', '<svg role="img" aria-label="Equacross" ', 1)
    svg = svg.replace('<defs>', '<title>Equacross</title><defs>', 1)
    if full_bleed:
        svg = svg.replace('<rect x="24" y="24" width="976" height="976" rx="220"/>', '<rect width="1024" height="1024"/>')
        # stretch the 4x4 board to the edges
        svg = svg.replace('<g opacity=".9">', '<g opacity=".9" transform="translate(512 512) scale(1.0505) translate(-512 -512)">', 1)
    if safe != 1.0:
        i = svg.index('<g transform="translate(84 150)')
        j = svg.rindex('</svg>')
        svg = svg[:i] + f'<g transform="translate(512 512) scale({safe}) translate(-512 -512)">' + svg[i:j] + '</g></svg>'
    return svg if svg.endswith("\n") else svg + "\n"


def kit_alt():
    svg = (KIT / "equacross-app-icon-alt.svg").read_text().replace('width="1024" height="1024" ', '')
    return svg.replace('<svg ', '<svg role="img" aria-label="Equacross" ', 1).replace('<defs>', '<title>Equacross</title><defs>', 1) + "\n"


def nav_mark():
    """Small cream tile with a coral equals sign, as in the approved navigation bar."""
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" aria-hidden="true">'
            '<rect x="3" y="7" width="58" height="54" rx="13" fill="#E2D3AE"/><rect x="3" y="3" width="58" height="54" rx="13" fill="#FFF8E8" stroke="#E7D9B7" stroke-width="1.5"/>'
            '<rect x="18" y="20" width="28" height="6.5" rx="3.25" fill="#C83C30"/><rect x="18" y="33" width="28" height="6.5" rx="3.25" fill="#C83C30"/></svg>\n')


files = {
    "logo.svg": wordmark(tagline="A WORD GAME FOR NUMBERS"),
    "logo-wordmark.svg": wordmark(),
    "logo-wordmark-on-dark.svg": wordmark(equa=CREAM, cross="#F07261"),
    "logo-on-dark.svg": wordmark(equa=CREAM, cross="#F07261", tagline="A WORD GAME FOR NUMBERS", tag_color="#B9C9B4"),
    "icon.svg": kit_icon(),
    "icon-full.svg": kit_icon(full_bleed=True),
    "icon-maskable.svg": kit_icon(full_bleed=True, safe=0.8),
    "icon-alt.svg": kit_alt(),
    "favicon.svg": kit_alt(),
    "nav-mark.svg": nav_mark(),
}
for name, svg in files.items():
    (OUT / name).write_text(svg, encoding="utf-8")
    print("wrote", name, len(svg) // 1024, "KB")

# ---------- rasterize with Chromium ----------
from playwright.sync_api import sync_playwright
rasters = [
    ("icon-full.svg", "apple-touch-icon.png", 180), ("icon.svg", "icon-192.png", 192), ("icon.svg", "icon-512.png", 512), ("icon.svg", "icon-1024.png", 1024), ("icon-alt.svg", "icon-alt-512.png", 512),
    ("icon-maskable.svg", "icon-maskable-512.png", 512), ("icon-maskable.svg", "icon-maskable-192.png", 192),
    ("favicon.svg", "favicon-16.png", 16), ("favicon.svg", "favicon-32.png", 32), ("favicon.svg", "favicon-48.png", 48),
    ("logo.svg", "logo-1200.png", 1200), ("logo-wordmark.svg", "logo-wordmark-600.png", 600),
]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    for src, dst, w in rasters:
        svg = (OUT / src).read_text()
        pg.set_viewport_size({"width": w, "height": w})
        pg.set_content(f'<html><body style="margin:0;background:transparent">{svg.replace("<svg ", f"<svg width=\"{w}\" ", 1)}</body></html>')
        el = pg.query_selector("svg")
        el.screenshot(path=str(OUT / dst), omit_background=True)
        print("rendered", dst)
    b.close()

from PIL import Image
imgs = [Image.open(OUT / f"favicon-{s}.png").convert("RGBA") for s in (16, 32, 48)]
imgs[2].save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)], append_images=imgs[:2])
print("wrote favicon.ico")
