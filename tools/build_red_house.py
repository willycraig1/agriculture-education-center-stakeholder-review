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
    class Boxes(list):
        inset = None
        inset_geom = None
    boxes = Boxes([(TITLE_BLOCK_X, 0, 9999, 9999)])
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = "".join(s["text"] for s in l["spans"]).strip()
            x0, y0, x1, y1 = l["bbox"]
            if t.startswith("FLOOR PLAN"):
                boxes.append((x0 - 120, y0 - 70, TITLE_BLOCK_X, 9999))
            elif t.startswith("ADDITION FLOOR PLAN"):
                boxes.append((x0 - 400, 0, TITLE_BLOCK_X, y1 + 70))
                boxes.inset = boxes[-1]
                boxes.inset_geom = (x0 - 400, 0, TITLE_BLOCK_X, y0 - 8)     # the inset drawing, above its title
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
    inset_groups = {k: [] for k in LAYERS}
    for d in page.get_drawings():
        L = d.get("layer")
        for k, ls in LAYERS.items():
            if L in ls and not inside(d["rect"], boxes):
                groups[k].append(d)
            elif L in ls and boxes.inset_geom and inside(d["rect"], [boxes.inset_geom]):
                inset_groups[k].append(d)
    inset_labels = []
    labels = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = "".join(s["text"] for s in l["spans"]).strip()
            r = pymupdf.Rect(l["bbox"])
            if boxes.inset_geom and inside(r, [boxes.inset_geom]) and len(t) >= 2:
                inset_labels.append((t, (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2))
            if len(t) < 2 or inside(r, boxes) or l["dir"] != (1.0, 0.0):
                continue
            size = max(s["size"] for s in l["spans"])
            labels.append({"t": t, "x": (r.x0 + r.x1) / 2, "y": r.y1 - size * 0.22, "size": size,
                           "dim": "X" in t and any(ch.isdigit() for ch in t)})
    sheets.append({"groups": groups, "labels": labels, "boxes": boxes, "inset": inset_groups, "inset_labels": inset_labels,
                   "clip": [min((d["rect"].x0 for d in groups["furniture"] + groups["walls"]), default=0),
                            max((d["rect"].y1 for d in groups["walls"]), default=0)]})

# ---------------------------------------------------------------- align every sheet to the Existing sheet
offsets = [(0, 0)]
rasters = [wall_raster(s["groups"]["walls"]) for s in sheets]
for k in range(1, len(sheets)):
    dx, dy = shift(rasters[k - 1], rasters[k])
    px, py = offsets[-1]
    offsets.append((px + dx, py + dy))          # sheet k coords = existing coords + offset

# ---------------------------------------------------------------- accessibility edit: no closets in Offices 1 and 2
# The architect's accessibility comments (2026-10-14), not yet on the sheets: the closets along the south walls of
# Office 1 and Office 2 are removed on Levels 1, 2, and 3, giving each office its full depth. Defined once on the
# Level 1 sheet (A1.0-1, points) and carried to the other sheets by the Office 1 label. Every drawn segment with
# both ends inside a closet box is dropped (closet walls, bifold doors, headers); the office walls are closed along
# the corridor wall's face.
import types
CLOSETS = [(199, 895, 314, 941), (412, 895, 522, 941)]
CLOSE = [[(200.1, 909.2), (200.1, 940.0), (313.5, 940.0)], [(412.8, 940.0), (520.8, 940.0), (520.8, 909.2)]]
def _pts(it):
    if it[0] == "re":
        return [it[1].tl, it[1].br]
    if it[0] == "qu":
        return [it[1].ul, it[1].ur, it[1].ll, it[1].lr]
    return [q for q in it[1:] if hasattr(q, "x")] or [pymupdf.Point(-1e9, -1e9)]   # unknown items are kept
_removed_closet = {}
for k in range(1, len(sheets)):
    # carried by the "OFFICE 1" label rather than the raster alignment, which is only good to a point or two
    _o1 = lambda k_: next((l["x"], l["y"]) for l in sheets[k_]["labels"] if l["t"] == "OFFICE 1")
    dx, dy = _o1(k)[0] - _o1(1)[0], _o1(k)[1] - _o1(1)[1]
    boxes = [(x0 + dx, y0 + dy, x1 + dx, y1 + dy) for x0, y0, x1, y1 in CLOSETS]
    inb = lambda q: any(x0 <= q.x <= x1 and y0 <= q.y <= y1 for x0, y0, x1, y1 in boxes)
    n = 0
    for part, ds in sheets[k]["groups"].items():
        keep = []
        for d in ds:
            items = [it for it in d["items"] if not all(inb(q) for q in _pts(it))]
            n += len(d["items"]) - len(items)
            if items:
                if len(items) != len(d["items"]):
                    d = dict(d, items=items, closePath=False)
                keep.append(d)
        sheets[k]["groups"][part] = keep
    for pl in CLOSE:
        P_ = [pymupdf.Point(x + dx, y + dy) for x, y in pl]
        sheets[k]["groups"]["walls"].append({"items": [("l", a_, b_) for a_, b_ in zip(P_, P_[1:])], "closePath": False, "layer": "P-WALL",
                                             "rect": pymupdf.Rect(min(q.x for q in P_), min(q.y for q in P_), max(q.x for q in P_), max(q.y for q in P_))})
    _removed_closet[NAMES[k]] = n

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

# ---------------------------------------------------------------- repair what the Level 3 sheet crops
# Sheet A1.0-3 is plotted so that (a) the addition, placed at an angle, runs off the top-left corner and
# (b) the bottom of the house runs off the bottom edge. Nothing past the sheet border is in the PDF.
#   (a) The same sheet draws the whole addition again as an orthogonal inset. The inset is moved onto the
#       placed addition with a rigid fit: seeded on the shared room labels, refined on the walls.
#   (b) The cropped strip (porch, storage) is unchanged from Level 2, so it is taken from that sheet.
# Both repairs are tagged in the output (class "repair") so they can be told apart from sheet linework.
def rigid_fit(a, b):
    am, bm = a.mean(), b.mean()
    r = np.conj(a - am) @ (b - bm)
    m = r / abs(r)
    return m, bm - m * am


repairs = {k: {} for k in range(len(sheets))}
repair_note = {}
K3 = next((k for k, sh in enumerate(sheets) if sh["boxes"].inset_geom), None)
if K3 is not None:
    sh = sheets[K3]
    placed = {}
    for l in sh["labels"]:
        if l["y"] < sh["boxes"].inset[3] + 300 and l["x"] < 1000:
            placed.setdefault(l["t"], []).append(complex(l["x"], l["y"]))
    src, dst = [], []
    for t, x, y in sh["inset_labels"]:
        if t in placed and len(placed[t]) == 1 and sum(1 for q in sh["inset_labels"] if q[0] == t) == 1:
            src.append(complex(x, y)); dst.append(placed[t][0])
    m, t0 = rigid_fit(np.array(src), np.array(dst))
    A = np.vstack([samples(d, 3) for d in sh["inset"]["walls"]])
    a = A[:, 0] + 1j * A[:, 1]
    B = np.vstack([samples(d, 2) for d in sh["groups"]["walls"] if d["rect"].y1 < 1000 and d["rect"].x1 < 1000])
    tb = cKDTree(B)
    cx, cy = sh["clip"][0] + 4, min(d["rect"].y0 for d in sh["groups"]["walls"]) + 4   # sheet crop edges
    for it in range(120):
        z = m * a + t0
        on_sheet = (z.real > cx) & (z.imag > cy)             # only this part of the addition was plotted
        dist, i = tb.query(np.c_[z.real, z.imag])
        lim = max(1.2, 12 * 0.94 ** it)                      # tighten the match distance as the fit settles
        k = on_sheet & (dist <= lim)
        m, t0 = rigid_fit(a[k], B[i[k], 0] + 1j * B[i[k], 1])
    z = m * a + t0
    on_sheet = (z.real > cx) & (z.imag > cy)
    dist = tb.query(np.c_[z.real, z.imag])[0][on_sheet]
    ox, oy = offsets[K3]
    mat = f"matrix({m.real:.6f} {m.imag:.6f} {-m.imag:.6f} {m.real:.6f} {t0.real - ox:.2f} {t0.imag - oy:.2f})"
    for part, ds in sh["inset"].items():
        body = "".join(f'<path d="{cadpdf.path_d(d)}"/>' for d in ds if cadpdf.path_d(d))
        if body:
            repairs[K3].setdefault("new" if part == "walls" else part, []).append(f'<g class="repair" transform="{mat}">{body}</g>')
    repair_note["addition_from_inset"] = {"rotation_deg": float(np.degrees(np.angle(m))), "label_pairs": len(src),
                                          "walls_within_1pt": float(np.mean(dist < 1.0)), "median_resid_pt": float(np.median(dist[dist < 20]))}
    # (b) bottom strip from the previous Level
    clip_y = sh["clip"][1] - oy                       # crop line in Existing coords
    pox, poy = offsets[K3 - 1]
    n = 0
    for part, ds in sheets[K3 - 1]["groups"].items():
        keep = [d for d in ds if d["rect"].y1 - poy > clip_y - 1 and d["rect"].y0 - poy > clip_y - 140]
        body = "".join(f'<path d="{cadpdf.path_d(d)}"/>' for d in keep if cadpdf.path_d(d))
        if body:
            n += len(keep)
            repairs[K3].setdefault(part, []).append(f'<g class="repair" transform="translate({-pox} {-poy})">{body}</g>')
    repair_note["bottom_strip_from_previous_level"] = {"crop_line_y": float(clip_y), "paths": n}

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
    R = {part: "".join(v) for part, v in repairs[k].items()}
    levels.append({
        "name": NAMES[k], "repaired": bool(R),
        "below": frag(g["below"], k) + R.get("below", ""), "above": frag(g["above"], k) + R.get("above", ""), "furniture": frag(g["furniture"], k) + R.get("furniture", ""),
        "fixtures": frag(g["fixtures"], k) + R.get("fixtures", ""), "openings": frag(g["openings"], k) + R.get("openings", ""),
        "walls": frag(g["walls"], k, kept) + R.get("walls", ""), "new": frag(g["walls"], k, nw) + R.get("new", ""), "removed": rm, "labels": lab,
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
json.dump({"offsets_pt": offsets, "view": view, "closet_segments_removed": _removed_closet, "counts": [l["counts"] for l in levels], "repairs": repair_note},
          open(os.path.join(ROOT, "drawings", "data", "red-house.json"), "w"), indent=2)
print("north (deg clockwise from up):", north_cw)
print("repairs:", repair_note)
print("offsets", offsets, "view", [round(v) for v in view])
for l in levels:
    print(l["name"], l["counts"], "KB", sum(len(v) for v in l.values() if isinstance(v, str)) // 1024)
