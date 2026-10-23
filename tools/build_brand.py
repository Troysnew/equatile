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


FRED = load("fredoka-latin-700-normal.woff2")
NUN_B = load("nunito-sans-latin-800-normal.woff2")
NUN_K = load("nunito-sans-latin-900-normal.woff2")


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


def accents(cx, cy, scale, color=CORAL):
    """The three coral 'spark' strokes, fanning out from a point below them."""
    rays = [(-40, 0.52, 0.86), (-6, 0.42, 0.98), (34, 0.50, 0.80)]   # angle from vertical, inner radius, outer radius
    sw = 0.20 * scale
    parts = []
    for ang, r1, r2 in rays:
        a = math.radians(ang)
        x1, y1 = cx + math.sin(a) * r1 * scale, cy - math.cos(a) * r1 * scale
        x2, y2 = cx + math.sin(a) * r2 * scale, cy - math.cos(a) * r2 * scale
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
    return f'<g stroke="{color}" stroke-width="{sw:.1f}" stroke-linecap="round" fill="none">{"".join(parts)}</g>'


def wordmark(equa=FOREST, cross=CORAL, tagline=None, tag_color=None):
    size = 200
    paths, w = text_paths(FRED, "Equacross", size, 0, 0)
    equa_d = " ".join(d for i, d in paths if i < 4)
    cross_d = " ".join(d for i, d in paths if i >= 4)
    # place the spark just above the final "s", using its real outline bounds
    from fontTools.pens.boundsPen import BoundsPen
    tt = FRED[0]; gs = tt.getGlyphSet(); bp = BoundsPen(gs); gs["s"].draw(bp)
    _, _, _, s_top = bp.bounds; s_top *= size / FRED[2]
    _, w8 = text_paths(FRED, "Equacros", size, 0, 0)
    s_center = w8 + (w - w8) * 0.5
    sc = size * 0.36
    sx, sy = s_center + size * 0.02, -s_top - size * 0.16 + sc * 0.42
    pad = size * 0.06
    cap = size * 0.72
    min_y = min(-cap, sy - sc * 1.0) - size * 0.04
    body = f'<path fill="{equa}" d="{equa_d}"/><path fill="{cross}" d="{cross_d}"/>' + accents(sx, sy, sc)
    view_h = -min_y + size * 0.26
    if tagline:
        tsize = size * 0.155
        tpaths, tw = text_paths(NUN_B, tagline, tsize, 0, 0, tracking=0.22)
        tx = w - tw - size * 0.02
        ty = size * 0.26 + tsize * 1.05
        td = " ".join(d for _, d in tpaths)
        body += f'<path fill="{tag_color or equa}" fill-opacity="0.82" transform="translate({tx:.1f},{ty:.1f})" d="{td}"/>'
        view_h = -min_y + ty + tsize * 0.35
    vb = f"{-pad:.1f} {min_y:.1f} {w + 2 * pad:.1f} {view_h:.1f}"
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


def board_bg(n=512, rr=None, full_bleed=False):
    rr = n * 0.225 if rr is None else rr
    cells = 5; c = n / cells
    tint = {(0, 4): CORAL_L, (3, 0): BLUE, (4, 0): CORAL_L, (2, 4): "#F6D2CE", (0, 1): "#CFE0EE"}
    parts = [f'<rect width="{n}" height="{n}" rx="{0 if full_bleed else rr:.1f}" fill="{SAGE_D}"/>']
    for r in range(cells):
        for col in range(cells):
            fill = tint.get((r, col), SAGE if (r + col) % 2 == 0 else "#D7E3C8")
            parts.append(f'<rect x="{col * c + 3:.1f}" y="{r * c + 3:.1f}" width="{c - 6:.1f}" height="{c - 6:.1f}" rx="10" fill="{fill}"/>')
    return parts


def icon_primary(n=512, full_bleed=False, inset=1.0):
    """9 7 2 on a sage board. In Equacross the line 972 reads as 9 − 7 = 2, a true equation."""
    clip = f'<clipPath id="r"><rect width="{n}" height="{n}" rx="{0 if full_bleed else n * 0.225:.1f}"/></clipPath>'
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" role="img" aria-label="Equacross"><title>Equacross</title><defs>{clip}</defs><g clip-path="url(#r)">']
    parts += board_bg(n, full_bleed=full_bleed)
    s = n * 0.32 * inset
    cx, cy = n / 2, n / 2
    step = s * 0.80
    pos = [(-1, -1), (0, 0), (1, 1)]
    for (i, j), d in zip(pos, (9, 7, 2)):
        x = cx + i * step - s / 2; y = cy + j * step * 0.78 - s / 2 + n * 0.02
        parts.append(tile(x, y, s, d, rot=-12 + i * 5))
    parts.append(accents(cx + s * 0.12, cy - s * 0.62, s * 0.62))
    parts.append("</g></svg>\n")
    return "".join(parts)


def icon_alt(n=512, plain_bg=False):
    """A single cream tile carrying the coral spark. Reads clearly at favicon sizes."""
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" role="img" aria-label="Equacross"><title>Equacross</title>']
    if not plain_bg:
        parts.append(f'<rect width="{n}" height="{n}" rx="{n * 0.225:.1f}" fill="#A9C79B"/>')
        parts.append(f'<rect x="{n * 0.04:.1f}" y="{n * 0.04:.1f}" width="{n * 0.92:.1f}" height="{n * 0.92:.1f}" rx="{n * 0.2:.1f}" fill="{SAGE_D}"/>')
    s = n * (0.78 if plain_bg else 0.62)
    x = (n - s) / 2; y = (n - s) / 2 - n * 0.02
    parts.append(tile(x, y, s, None, shadow=not plain_bg))
    parts.append(accents(n / 2, y + s * 0.80, s * 0.78))
    parts.append("</svg>\n")
    return "".join(parts)


files = {
    "logo.svg": wordmark(tagline="A WORD GAME FOR NUMBERS"),
    "logo-wordmark.svg": wordmark(),
    "logo-wordmark-on-dark.svg": wordmark(equa=CREAM, cross="#F07261"),
    "logo-on-dark.svg": wordmark(equa=CREAM, cross="#F07261", tagline="A WORD GAME FOR NUMBERS", tag_color=CREAM),
    "icon.svg": icon_primary(),
    "icon-maskable.svg": icon_primary(full_bleed=True, inset=0.78),
    "icon-alt.svg": icon_alt(),
    "favicon.svg": icon_alt(plain_bg=False),
}
for name, svg in files.items():
    (OUT / name).write_text(svg, encoding="utf-8")
    print("wrote", name, len(svg) // 1024, "KB")

# ---------- rasterize with Chromium ----------
from playwright.sync_api import sync_playwright
rasters = [
    ("icon.svg", "apple-touch-icon.png", 180), ("icon.svg", "icon-192.png", 192), ("icon.svg", "icon-512.png", 512),
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
