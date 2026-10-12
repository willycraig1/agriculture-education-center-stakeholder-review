"""Build the Red House Level sequence from "26 09 03 4H Study Plan_Red House Levels.pdf".

Sheets: 1 Existing (A1.0) · 2 Level 1 (A1.0-1) · 3 Level 2 (A1.0-2) · 4 Level 3 (A1.0-3).
All four are 3/16" = 1'-0", but the plan sits at a different spot on each sheet. Each sheet is
aligned to the Existing sheet by cross-correlating its wall layer with the previous sheet's (pure
translation). Walls are then compared Level to Level: a wall path with less than 40% of its length
near the previous Level's walls is "new"; a previous wall path with less than 40% near the current
walls is "removed". Room names and sizes are the sheets' own text.

Writes
  drawings/red-house-levels.svg   editable master, one layer per Level (walls / new / removed / ...)
  slides/data/red-house.js        per-Level SVG fragments for slides/red-house.html
  drawings/data/red-house.json    alignment offsets and wall-diff counts (for audit)

Run:  python tools/build_red_house.py   (needs pymupdf, numpy, scipy, pillow)
"""
import json, os, sys
import numpy as np
import pymupdf
from PIL import Image, ImageDraw
from scipy.signal import fftconvolve
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import cadpdf

PDF = os.path.join(ROOT, "source", "26 09 03 4H Study Plan_Red House Levels.pdf")
pal = json.load(open(os.path.join(ROOT, "design", "palette.json")))
EDU = pal["program"]["education"]
N = pal["neutral"]
NAMES = ["Existing", "Level 1", "Level 2", "Level 3"]
LAYERS = {
    "walls": ["P-WALL"],
    "openings": ["P-DOOR", "P-WINDOW"],
    "fixtures": ["P-FIXTURE", "P-CASEWORK", "A-FIXT", "P-RAILING"],
    "furniture": ["P-FURNITURE"],
    "above": ["P-ABOVE"],
    "below": ["P-BELOW-LIGHT", "P-BELOW-MED"],
}
TITLE_BLOCK_X = 2370


def excluded_boxes(page):
    """Sheet furniture to drop: plan titles with their scale/legend/north symbol, and on Level 3 the
    enlarged 'ADDITION FLOOR PLAN' inset (the addition is kept where it is placed on the site)."""
    boxes = [(TITLE_BLOCK_X, 0, 9999, 9999)]
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = "".join(s["text"] for s in l["spans"]).strip()
            x0, y0, x1, y1 = l["bbox"]
            if t.startswith("FLOOR PLAN"):
                boxes.append((x0 - 120, y0 - 70, TITLE_BLOCK_X, 9999))
            elif t.startswith("ADDITION FLOOR PLAN"):
                boxes.append((x0 - 400, 0, TITLE_BLOCK_X, y1 + 70))
    return boxes


def inside(r, boxes):
    return any(r.x0 >= a and r.y0 >= b and r.x1 <= c and r.y1 <= d for a, b, c, d in boxes)


def wall_raster(ds):
    im = Image.new("L", (1296, 864), 0)
    dr = ImageDraw.Draw(im)
    for x in ds:
        for it in x["items"]:
            if it[0] == "l":
                dr.line([(it[1].x / 2, it[1].y / 2), (it[2].x / 2, it[2].y / 2)], fill=255, width=2)
            elif it[0] == "re":
                r = it[1]
                dr.rectangle([r.x0 / 2, r.y0 / 2, r.x1 / 2, r.y1 / 2], outline=255, width=2)
    return np.asarray(im, float) / 255


def shift(a, b):
    """Offset (dx, dy) in points such that sheet b ≈ sheet a moved by (dx, dy)."""
    c = fftconvolve(b, a[::-1, ::-1], mode="full")
    iy, ix = np.unravel_index(np.argmax(c), c.shape)
    return int(ix - (a.shape[1] - 1)) * 2, int(iy - (a.shape[0] - 1)) * 2


def samples(d, step=2.0):
    pts = []
    for it in d["items"]:
        if it[0] == "l":
            a, b = it[1], it[2]
            n = max(1, int(abs(b - a) / step))
            pts += [(a.x + (b.x - a.x) * k / n, a.y + (b.y - a.y) * k / n) for k in range(n + 1)]
        elif it[0] == "re":
            r = it[1]
            for a, b in [(r.tl, r.tr), (r.tr, r.br), (r.br, r.bl), (r.bl, r.tl)]:
                n = max(1, int(abs(b - a) / step))
                pts += [(a.x + (b.x - a.x) * k / n, a.y + (b.y - a.y) * k / n) for k in range(n + 1)]
        elif it[0] == "c":
            pts += [(q.x, q.y) for q in it[1:5]]
    return np.array(pts) if pts else np.zeros((0, 2))


doc = pymupdf.open(PDF)
sheets = []
for page in doc:
    boxes = excluded_boxes(page)
    groups = {k: [] for k in LAYERS}
    for d in page.get_drawings():
        L = d.get("layer")
        for k, ls in LAYERS.items():
            if L in ls and not inside(d["rect"], boxes):
                groups[k].append(d)
    labels = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = "".join(s["text"] for s in l["spans"]).strip()
            r = pymupdf.Rect(l["bbox"])
            if len(t) < 2 or inside(r, boxes) or l["dir"] != (1.0, 0.0):
                continue
            size = max(s["size"] for s in l["spans"])
            labels.append({"t": t, "x": (r.x0 + r.x1) / 2, "y": r.y1 - size * 0.22, "size": size,
                           "dim": "X" in t and any(ch.isdigit() for ch in t)})
    sheets.append({"groups": groups, "labels": labels, "boxes": boxes})

# ---------------------------------------------------------------- align every sheet to the Existing sheet
offsets = [(0, 0)]
rasters = [wall_raster(s["groups"]["walls"]) for s in sheets]
for k in range(1, len(sheets)):
    dx, dy = shift(rasters[k - 1], rasters[k])
    px, py = offsets[-1]
    offsets.append((px + dx, py + dy))          # sheet k coords = existing coords + offset

# ---------------------------------------------------------------- wall diff, Level to Level (in Existing coords)
def wall_pts(k):
    ox, oy = offsets[k]
    out = []
    for d in sheets[k]["groups"]["walls"]:
        p = samples(d)
        out.append(p - [ox, oy] if len(p) else p)
    return out


diff = [{"new": set(), "removed": set()}]
for k in range(1, len(sheets)):
    cur, prev = wall_pts(k), wall_pts(k - 1)
    P = np.vstack([p for p in prev if len(p)])
    C = np.vstack([p for p in cur if len(p)])
    tp, tc = cKDTree(P), cKDTree(C)
    new = {i for i, p in enumerate(cur) if len(p) and np.mean(tp.query(p)[0] < 1.8) < 0.4}
    removed = {i for i, p in enumerate(prev) if len(p) and np.mean(tc.query(p)[0] < 1.8) < 0.4}
    diff.append({"new": new, "removed": removed})

# ---------------------------------------------------------------- SVG fragments (Existing-sheet coords)
def frag(ds, k, idx=None):
    ox, oy = offsets[k]
    body = "".join(f'<path d="{cadpdf.path_d(d)}"/>' for i, d in enumerate(ds)
                   if (idx is None or i in idx) and cadpdf.path_d(d))
    return f'<g transform="translate({-ox} {-oy})">{body}</g>' if body else ""


levels = []
all_pts = []
for k, s in enumerate(sheets):
    g = s["groups"]
    nw = diff[k]["new"]
    kept = set(range(len(g["walls"]))) - nw
    ox, oy = offsets[k]
    lab = "".join(
        f'<text x="{l["x"] - ox:.1f}" y="{l["y"] - oy:.1f}" font-size="{l["size"] * (0.85 if l["dim"] else 1.05):.1f}" '
        f'{"class=\"dim\"" if l["dim"] else ""} text-anchor="middle">{l["t"].replace("&", "&amp;")}</text>'
        for l in s["labels"])
    rm = ""
    if k > 0:
        rm = frag(sheets[k - 1]["groups"]["walls"], k - 1, diff[k]["removed"])
    levels.append({
        "name": NAMES[k],
        "below": frag(g["below"], k), "above": frag(g["above"], k), "furniture": frag(g["furniture"], k),
        "fixtures": frag(g["fixtures"], k), "openings": frag(g["openings"], k),
        "walls": frag(g["walls"], k, kept), "new": frag(g["walls"], k, nw), "removed": rm, "labels": lab,
        "counts": {"walls": len(g["walls"]), "new": len(nw), "removed": len(diff[k]["removed"])},
    })
    for d in g["walls"]:
        r = d["rect"]
        all_pts += [(r.x0 - ox, r.y0 - oy), (r.x1 - ox, r.y1 - oy)]

A = np.array(all_pts)
pad = 30
view = [float(A[:, 0].min() - pad), float(A[:, 1].min() - pad), float(A[:, 0].max() + pad), float(A[:, 1].max() + pad)]
FT_PER_PT = (1 / 72) / (3 / 16)               # 3/16" = 1'-0": 1 pt = (1/72 in) / (3/16 in per ft)

# North on these sheets. The study plan (north up, same as the survey) carries the same room labels as
# real text, rotated with the house; the label baseline gives the house rotation, and north follows.
import math
STUDY = os.path.join(ROOT, "source", "Clark Farm Study Plan-A0.1 (3)1.pdf")
north_cw = None
for b in pymupdf.open(STUDY)[0].get_text("dict")["blocks"]:
    for l in b.get("lines", []):
        if "".join(sp["text"] for sp in l["spans"]).strip() == "DEMO KITCHEN":
            rot = math.atan2(l["dir"][1], l["dir"][0])            # sheet x-axis as drawn on the study plan
            nx, ny = math.cos(-math.pi / 2 - rot), math.sin(-math.pi / 2 - rot)   # study north (0,-1) on this sheet
            north_cw = math.degrees(math.atan2(nx, -ny))          # degrees clockwise from "up"
data = {"view": view, "ft_per_pt": FT_PER_PT, "north_cw_from_up": north_cw, "levels": levels}
os.makedirs(os.path.join(ROOT, "slides", "data"), exist_ok=True)
with open(os.path.join(ROOT, "slides", "data", "red-house.js"), "w") as fh:
    fh.write("// Generated by tools/build_red_house.py. Do not edit by hand.\n")
    fh.write("window.RED_HOUSE = " + json.dumps(data) + ";\n")

# editable master: one layer per Level, sub-layers per content type
x0, y0, x1, y1 = view
style = (f'.walls{{fill:none;stroke:{N["ink"]};stroke-width:1.1}} .new{{fill:none;stroke:{EDU["base"]};stroke-width:2.2}} '
         f'.removed{{fill:none;stroke:{N["muted"]};stroke-width:1;stroke-dasharray:4 3}} '
         f'.openings,.fixtures{{fill:none;stroke:{N["ink"]};stroke-width:.5}} .furniture,.above,.below{{fill:none;stroke:{N["line"]};stroke-width:.4}} '
         f'text{{font-family:Avenir Next,Helvetica,Arial,sans-serif;fill:{N["ink"]}}} .dim{{fill:{N["muted"]}}}')
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
       f'viewBox="{x0} {y0} {x1 - x0} {y1 - y0}"><style>{style}</style>'
       f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{N["paper"]}"/>']
for k, L in enumerate(levels):
    vis = "" if k == len(levels) - 1 else ' style="display:none"'
    svg.append(f'<g id="level-{k}" inkscape:groupmode="layer" inkscape:label="{L["name"]}"{vis}>')
    for part in ("below", "above", "furniture", "fixtures", "openings", "walls", "new", "removed"):
        if L[part]:
            svg.append(f'<g class="{part}" inkscape:groupmode="layer" inkscape:label="{part}">{L[part]}</g>')
    svg.append(f'<g class="labels" inkscape:groupmode="layer" inkscape:label="labels">{L["labels"]}</g></g>')
svg.append("</svg>")
open(os.path.join(ROOT, "drawings", "red-house-levels.svg"), "w").write("".join(svg))
json.dump({"offsets_pt": offsets, "view": view, "counts": [l["counts"] for l in levels]},
          open(os.path.join(ROOT, "drawings", "data", "red-house.json"), "w"), indent=2)
print("north (deg clockwise from up):", north_cw)
print("offsets", offsets, "view", [round(v) for v in view])
for l in levels:
    print(l["name"], l["counts"], "KB", sum(len(v) for v in l.values() if isinstance(v, str)) // 1024)
