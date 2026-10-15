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
                # the inset reaches ~620 pt left of its title: its patio (label, roof edge, paving lines) runs that far,
                # and left in it would show as a stray patio beside the house on Level 3 (architect, 2026-10-15)
                boxes.append((x0 - 620, 0, TITLE_BLOCK_X, y1 + 70))
                boxes.inset = boxes[-1]
                boxes.inset_geom = (x0 - 620, 0, TITLE_BLOCK_X, y0 - 8)     # the inset drawing, above its title
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
repair_walls = {k: [] for k in range(len(sheets))}     # (drawings, point map to Existing coords), for the room fill
repair_above = {k: [] for k in range(len(sheets))}
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
        if t in placed and len(placed[t]) == 1 and sum(1 for q in sh["inset_labels"] if q[0] == t) == 1 and t != "PATIO":   # the patio label sits loose, not on the rooms
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
            _f3 = lambda x, y, m=m, t0=t0, ox=ox, oy=oy: ((m * complex(x, y) + t0).real - ox, (m * complex(x, y) + t0).imag - oy)
            if part in ("walls", "openings"):
                repair_walls[K3].append(([d for d in ds if d.get("layer") != "P-DOOR"], _f3))
            elif part == "above":
                repair_above[K3].append((ds, _f3))
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
            if part in ("walls", "openings"):
                repair_walls[K3].append(([d for d in keep if d.get("layer") != "P-DOOR"], lambda x, y, pox=pox, poy=poy: (x - pox, y - poy)))
            elif part == "above":
                repair_above[K3].append((keep, lambda x, y, pox=pox, poy=poy: (x - pox, y - poy)))
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

# ---------------------------------------------------------------- program key: rooms coloured by use (Levels 1 to 3)
# Architect's convention (2026-10-14): yellow circulation, blue restrooms, red primary spaces (conference and
# teaching), grey storage, mechanical, and ancillary; offices green and kitchen support orange (Claude's pick).
# Rooms come from the walls: the walls are rasterised, the building's inside is found by closing door-width gaps,
# and a watershed grown from each room label settles room boundaries at the narrowest points, the doorways. Spaces
# outside the walls (porches, patio, covered walkway, carport) are left uncoloured.
from scipy import ndimage
from skimage.segmentation import watershed
from skimage import measure
from shapely.geometry import Polygon as _SPoly
from shapely.ops import unary_union as _sunion
PROGRAM = {"circulation": ["HALL", "LOBBY", "COMMONS"], "restroom": ["H/C R.R.", "MENS", "WOMENS"],
           "primary": ["CONFERENCE", "INSTRUCTIONAL CLASSROOM", "INSTRUCTIONAL CLASSROOM/", "EVENT SPACE", "DEMO KITCHEN"],
           "office": ["OFFICE 1", "OFFICE 2", "OFFICE 3", "OFFICE 4", "OFFICE 5"],
           "kitchen": ["DISHWASH", "COOLER", "PANTRY", "BREAKROOM"], "storage": ["STORAGE"]}   # breakroom with kitchen support (architect, 2026-10-15)
_cat = {n: c for c, ns in PROGRAM.items() for n in ns}
_PX = 2.0                                                  # raster px per pt
FT_PER_PT = (1 / 72) / (3 / 16)
def _segs(ds, f):
    for d in ds:
        for it in d["items"]:
            if it[0] == "l":
                yield f(it[1].x, it[1].y), f(it[2].x, it[2].y)
            elif it[0] == "re":
                r = it[1]; q = [f(r.x0, r.y0), f(r.x1, r.y0), f(r.x1, r.y1), f(r.x0, r.y1)]
                yield from zip(q, q[1:] + q[:1])
            elif it[0] == "c":
                yield f(it[1].x, it[1].y), f(it[4].x, it[4].y)
            elif it[0] == "qu":
                q_ = it[1]; q = [f(q_.ul.x, q_.ul.y), f(q_.ur.x, q_.ur.y), f(q_.lr.x, q_.lr.y), f(q_.ll.x, q_.ll.y)]
                yield from zip(q, q[1:] + q[:1])
program_counts = {}
for k in range(1, len(sheets)):
    ox, oy = offsets[k]
    # barriers: walls and windows (the windows close the wall's gaps). Door leaves and swings are left out. Each room's
    # core is the part of it more than r from any line, which seals doorways narrower than 2r; r is raised per room
    # until its core is closed off from the outside and from the rooms around it. The cores are then grown back out to
    # the walls, meeting at the doorways.
    _win = [d for d in sheets[k]["groups"]["openings"] if d.get("layer") != "P-DOOR"]
    src = [(sheets[k]["groups"]["walls"] + _win, lambda x, y, ox=ox, oy=oy: (x - ox, y - oy))] + repair_walls[k]
    seg = [sg for ds, f in src for sg in _segs(ds, f)]
    P_ = np.array([q for sg in seg for q in sg]); bx0, by0 = P_.min(0) - 60; bx1, by1 = P_.max(0) + 60
    W_, H_ = int((bx1 - bx0) * _PX) + 1, int((by1 - by0) * _PX) + 1
    def _raster(segs, w):
        im = Image.new("L", (W_, H_), 0); dr = ImageDraw.Draw(im)
        for (xa, ya), (xb, yb) in segs:
            dr.line([((xa - bx0) * _PX, (ya - by0) * _PX), ((xb - bx0) * _PX, (yb - by0) * _PX)], fill=255, width=w)
        return np.asarray(im) > 0
    wall = _raster(seg, 3)
    # second barrier for rooms open between posts (the instructional classroom): add the roof edge (P-ABOVE), drawn
    # heavy so its dashes join
    _ab = [(sheets[k]["groups"]["above"], lambda x, y, ox=ox, oy=oy: (x - ox, y - oy))] + repair_above[k]
    wall2 = wall | _raster([sg for ds, f in _ab for sg in _segs(ds, f)], 9)
    labs = []
    for l in sheets[k]["labels"]:
        if not l["dim"] and l["t"] in _cat:
            labs.append((l["t"], int((l["x"] - ox - bx0) * _PX), int((l["y"] - l["size"] * 0.35 - oy - by0) * _PX),
                         int(len(l["t"]) * l["size"] * 0.32 * _PX), int(l["size"] * 0.5 * _PX)))
    def _core(w_, t, px, py):
        free_ = ~w_; dist_ = ndimage.distance_transform_edt(free_)
        for r_pt in (14, 18, 22, 27, 33, 41, 50):
            lab_, _ = ndimage.label(dist_ > r_pt * _PX)
            y0_, x0_ = max(py - int(r_pt * _PX), 0), max(px - int(r_pt * _PX), 0)
            win_ = lab_[y0_:py + int(r_pt * _PX), x0_:px + int(r_pt * _PX)]
            ids = [v for v in np.unique(win_) if v]
            if not ids:
                continue
            c_ = lab_[py, px] or max(ids, key=lambda v: (win_ == v).sum())
            cm = lab_ == c_
            ys_, xs_ = np.nonzero(cm)
            if ys_.min() == 0 or xs_.min() == 0 or ys_.max() == H_ - 1 or xs_.max() == W_ - 1:
                continue                                    # open to the outside
            if cm.sum() / _PX ** 2 * FT_PER_PT ** 2 > 1500:
                continue
            # a room's core must not run under another use's room name (its text box)
            _hit = [t2 for t2, x2, y2, hw, hh in labs if _cat[t2] != _cat[t] and cm[max(y2 - hh, 0):y2 + hh, max(x2 - hw, 0):x2 + hw].any()]
            if _hit:
                continue                                    # runs into a room of another use: seal it tighter
            return cm, r_pt, free_
        return None
    free = ~wall
    dist = ndimage.distance_transform_edt(free)
    cores = {}; names = {}; skipped = []
    for t, px, py, _hw, _hh in labs:
        if not (0 <= px < W_ and 0 <= py < H_):
            skipped.append(t); continue
        got = _core(wall, t, px, py) or _core(wall2, t, px, py)
        if got is None and not wall[py, px]:
            # a small room whose doorway is as wide as the room: seed it at its label and let it grow to its walls
            disk = np.zeros(wall.shape, bool); disk[py - 3:py + 4, px - 3:px + 4] = True
            got = (disk & ~wall, 30, ~wall)
        if got is None:
            skipped.append(t); continue
        names[len(names) + 1] = t; cores[len(names)] = got
    markers = np.zeros(wall.shape, int); grown = np.zeros(wall.shape, bool)
    sq = np.ones((3, 3), bool)                             # square growth: rectangular rooms keep their corners
    for i_, (cm, r_pt, free_) in cores.items():
        markers[cm & (markers == 0)] = i_
        grown |= ndimage.binary_dilation(cm, structure=sq, iterations=int(r_pt * _PX) + 2) & free_
    reg = watershed(-dist, markers, mask=grown)
    if os.environ.get("RH_DEBUG"):
        _dbg = np.zeros(wall.shape + (3,), np.uint8); _dbg[wall] = (255, 255, 255)
        _cols = np.random.default_rng(1).integers(60, 230, (len(names) + 1, 3))
        for i_ in names: _dbg[reg == i_] = _cols[i_]
        for t2, x2, y2, _hw, _hh in labs:
            _dbg[max(y2 - 4, 0):y2 + 5, max(x2 - 4, 0):x2 + 5] = (255, 0, 0)
        Image.fromarray(_dbg).resize((W_ // 2, H_ // 2)).save(os.path.join(os.environ["RH_DEBUG"], f"rooms{k}.png"))
        print(k, "skipped:", skipped)
    rooms = []
    for i, t in names.items():
        m_ = ndimage.binary_opening(reg == i, iterations=2)
        polys = [_SPoly([(x / _PX + bx0, y / _PX + by0) for y, x in c]).buffer(0) for c in measure.find_contours(m_.astype(float), 0.5) if len(c) > 8]
        g = _sunion([p for p in polys if p.area > 30]).buffer(0.8).simplify(0.6)
        if g.is_empty:
            continue
        d_ = " ".join("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in r.exterior.coords) + "Z" for r in getattr(g, "geoms", [g]))
        rooms.append(f'<path class="pg-{_cat[t]}" d="{d_}"/>')
    levels[k]["program"] = "".join(rooms)
    program_counts[NAMES[k]] = len(rooms)
print("program rooms per Level:", program_counts)

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
