"""Owner's stormwater direction (2026-11-18), laid out on the site plan as a planning concept.

  1. Holding pens, new barns, turnout yards, and the working spaces around them rise to a pad at BFE + 1'.
  2. The retention pond opens into the historical slough bed: one water body.
  3. The slough bed is expanded along its own alignment, with wide radii. About 30% of the open pasture stays up
     just above the BFE; the other 70% becomes modified slough-bed swale.
  4. A culvert under the road joins a similar swale dug through the north triangle pasture.
  5. High-ground paths run through the pasture to the gates, crossing the swale centerlines on culverts.

"Open pasture" is the site paddocks less the woods, the road, and the raised pad. The swale is the open ground left after
a band of high ground is held along the woods. The surveyed trees are drawn over the grading, which runs beneath them
(architect, 2026-11-18). The band's width is solved to reach the 70%. The 3.3 ac paddock has no
centerline and stays up as a dry refuge.

The BFE is the modelled 100-year elevation, +21.70' (architect, 2026-11-18); FEMA's Zone A publishes none here. The
high-ground and swale grades are planning assumptions for civil to confirm. Grades come from the survey's spot elevations; the north triangle has no interior spots and uses the median.

The swale and pond are graded as one surface and drawn with 1' contours. The swale's floor falls to the pond and meets it
just under the normal water level, so the swale works as the pond's littoral shelf. The pond keeps its designed edge on
the east and holds its top of bank 10' off the fence on the south. North is to the left on the sheets: east is up, south
is right.

Design inputs: tools/stormwater_inputs.py. Change a decision there, not here.
Writes drawings/data/stormwater-concept.js (read by tools/sheet.html). Run after build_site_map.py.

Run:  python tools/build_stormwater_concept.py
"""
import json, os, re, sys
import numpy as np
from scipy.interpolate import griddata
from scipy.ndimage import distance_transform_edt, gaussian_filter
from scipy.spatial import cKDTree
from shapely import contains_xy, set_precision, distance as sh_distance, points as sh_points
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from skimage.draw import line as raster_line
from skimage.graph import MCP_Geometric
from skimage.measure import find_contours

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DATA = os.path.join(ROOT, "drawings", "data")

from stormwater_inputs import *                                    # every design decision lives in tools/stormwater_inputs.py

m = open(os.path.join(ROOT, "slides", "data", "site-map.js"), encoding="utf8").read()
SM = json.loads(m[m.index("=") + 1:].rstrip().rstrip(";"))
svg, FT = SM["svg"], SM["ft_per_unit"]
U = lambda ft: ft / FT
acres = lambda g: g.area * FT * FT / 43560


def subpaths(d):
    out = []
    for s in re.finditer(r"M([^MZ]*)Z?", d):
        n = [float(v) for v in re.findall(r"-?\d+\.?\d*", s.group(1))]
        if len(n) >= 6:
            out.append(list(zip(n[0::2], n[1::2])))
    return out


def chaikin(pts, n=3):
    """Round a path's bends, keeping its two ends on their gates."""
    for _ in range(n):
        q = [pts[0]]
        for (x0_, y0_), (x1_, y1_) in zip(pts, pts[1:]):
            q += [(.75 * x0_ + .25 * x1_, .75 * y0_ + .25 * y1_), (.25 * x0_ + .75 * x1_, .25 * y0_ + .75 * y1_)]
        pts = q + [pts[-1]]
    return pts


MAIN[MAIN.index((1000, 392)):MAIN.index((1110, 500)) + 1] = chaikin(BARN_B_BEND)


def smooth(g, r):
    """Round the edges of g: inside bends to radius r, outside corners to ARM."""
    n = U(ARM)
    return g.buffer(r, 32).buffer(-r - n, 32).buffer(n, 32)


def polys(g, min_ac=0.0):
    return [p for p in getattr(g, "geoms", [g]) if p.geom_type == "Polygon" and acres(p) > min_ac]


pads = [Polygon(subpaths(x.group(1))[0]).buffer(0) for x in re.finditer(r'<path class="pad site" data-pad="\d+" d="([^"]+)"', svg)]
pasture = unary_union(pads)
canopy = Polygon()
for d in re.findall(r' d="([^"]+)"', re.search(r'<g id="canopy"[^>]*>(.*?)</g>', svg, re.S).group(1)):
    for q in subpaths(d):
        p = Polygon(q).buffer(0)
        if p.area > 0:
            canopy = canopy.symmetric_difference(p)
canopy = canopy.buffer(0)
fences = json.load(open(os.path.join(DATA, "fences.json")))
road = unary_union([Polygon(r["outer"]).buffer(0) for r in fences["road_area"]])
pond_design = Polygon(json.load(open(os.path.join(DATA, "retention-markup.json")))["site_ponds"][0]).buffer(0)
# the pond's limits: top of bank 10' off the south fence; on the east, nothing past the designed edge
(_sx0, _sy0), (_sx1, _sy1) = SOUTH_FENCE
_lean = (_sx1 - _sx0) / (_sy1 - _sy0)                # the fence's lean, carried past both of its ends
_fx = lambda y_: _sx0 + _lean * (y_ - _sy0) - U(SOUTH_HOLD) * 1.0001
south_zone = Polygon([(_fx(_sy0 + 400), _sy0 + 400), (_fx(_sy1 - 400), _sy1 - 400), (_sx1 + 400, _sy1 - 400), (_sx0 + 400, _sy0 + 400)])
pond = pond_design.difference(south_zone).buffer(0)
_cy = pond.centroid.y
east_zone = pads[0].intersection(Polygon([(1100, 300), (1400, 300), (1400, _cy), (1100, _cy)])).difference(pond)
hold_zone = unary_union([south_zone, east_zone])
bed = unary_union([Polygon(p["outer"]).buffer(0) for p in json.load(open(os.path.join(DATA, "slough-bed.json")))["parts"]])

# ---- the raised pad: the working barnyard's own shapes, joined across the aisles between them
_b = svg[svg.index('<g id="barnyard"'):]
a, b, c, d, e, f = [float(v) for v in re.search(r'<g transform="matrix\(([^)]+)\)"', _b).group(1).split()]
to_map = lambda x, y: (a * x + c * y + e, b * x + d * y + f)
shapes, on_pad = [], []
for g in re.finditer(r'<g class="by" data-id="([^"]+)" data-level="(\d)" data-kind="(\w+)"[^>]*>\s*<rect class="shape" x="([-\d.]+)" y="([-\d.]+)" width="([\d.]+)" height="([\d.]+)"', _b):
    id_, _, kind, x, y, w, h = g.groups()
    if kind in ("building", "yard") and not PAD_SKIP.search(id_):
        x, y, w, h = float(x), float(y), float(w), float(h)
        shapes.append(Polygon([to_map(x, y), to_map(x + w, y), to_map(x + w, y + h), to_map(x, y + h)]))
        on_pad.append(id_)
pad = Polygon([to_map(x, y) for x, y in PAD_OUTLINE])
pad_toe = pad.buffer(U(PAD_TOE), join_style=2)

# ---- paths, hubs, and what must stay out of the swale
centerlines = [LineString(MAIN)] + [LineString(v) for v in BRANCHES.values()]
# Path A runs on the centerline between the two cattle barns (x = 74 in the barnyard's grid), hub gate to pad edge
_hub_y = (936.0 - e - a * BARN_AXIS) / c
PATHS = [("Path A", "hub gate to the pad, on the centerline between the cattle barns", [to_map(BARN_AXIS, _hub_y), to_map(BARN_AXIS, PAD_OUTLINE[0][1])]),
         ("Path B", "high ground in the 4.8 ac paddock to the corner gate", PATH_B_POINTS),
         ("Path C", "triangle hub, along the fence, to the gate at the south tip", PATH_C_POINTS)]
PATHS = [(n, w, chaikin(l) if n in ("Path B", "Path C") else l) for n, w, l in PATHS]
path_lines = [LineString(p[2]) for p in PATHS]
corridors = unary_union([g.buffer(U(PATH_W / 2), cap_style=2) for g in path_lines])
hubs = unary_union([Point(p).buffer(U(HUB_R)) for p in HUBS])
woods = canopy.buffer(U(WOODS_EDGE))
open_pasture = pasture.difference(unary_union([canopy, road, pad_toe, pond])).buffer(0)
# the bed itself is always swale, wherever the woods or a tree's margin would otherwise break it
# (through the woods only a narrow connecting channel is cut)
_lines = unary_union(centerlines)
core = unary_union([bed.intersection(pasture), _lines.buffer(U(24)).difference(woods), _lines.buffer(U(12))]).difference(unary_union([road.buffer(U(4)), pad_toe, hubs, hold_zone]))


# the traced woods edge is ragged; the swale follows a cleaned edge, so its banks can hold their radii
woods_clean = unary_union(polys(canopy.buffer(-U(WOODS_SPUR), 16).buffer(U(WOODS_SPUR + WOODS_NOTCH), 16).buffer(-U(WOODS_NOTCH), 16), 0.05))
_keep = woods_clean
_fixed = unary_union([road.buffer(U(ROAD_STRIP)), pad_toe.buffer(U(PAD_EDGE)), hubs])


# the swale's arm along the road fence, carried north until it meets Path B
PATH_B_ARM = LineString(PATH_B_ARM_LINE).buffer(U(PATH_B_ARM_HALF), 32)
# where the banks are eased: around the corner of the pad at cattle barn B, and north of Pen 5
# the north triangle's own retention pond, from the architect's sketch: it collects the triangle before discharging
TRI_POND = Polygon(TRI_POND_POINTS).buffer(U(10), 32).buffer(-U(20), 32).buffer(U(10), 32)
TRI_SIDE = unary_union(pads[5:9])
SOFT_ZONES = unary_union([Point(c_).buffer(U(r_)) for c_, r_ in SOFT_CIRCLES])


def swale_at(band_ft):
    """The swale when a band this wide stays up along the woods; gaps too tight for the radius stay up with it."""
    band = _keep.buffer(U(band_ft), 16)
    s = smooth(pasture.difference(unary_union([band, _fixed])), U(RADIUS))
    s = s.intersection(pasture).difference(unary_union([_fixed, woods_clean.buffer(U(5))]))
    s = unary_union([s, core]).buffer(U(15), 16).buffer(-U(15), 16)      # no slivers of high ground between the arms
    s = s.intersection(pasture).difference(unary_union([road.buffer(U(4)), pad_toe, hubs, hold_zone]))
    s = set_precision(s.buffer(0), 0.02)
    eased = set_precision(s.buffer(U(40), 32).buffer(-U(80), 32).buffer(U(40), 32), 0.02)      # long, even banks at the two corners
    s = unary_union([s.difference(SOFT_ZONES), eased.intersection(SOFT_ZONES)]).difference(unary_union([pad_toe.buffer(U(PAD_EDGE)), hubs])).buffer(0)
    s = s.buffer(0).difference(corridors)
    # no square corners where a path meets the top of bank: each corner is cut back on the widest radius its arm allows
    # (a narrow arm stops short of the path in a rounded end, and its culvert carries on to the invert)
    near = corridors.buffer(U(60))
    tidy = lambda g: set_precision(g.buffer(0), 0.02)
    s = tidy(s)
    s = tidy(unary_union([tidy(s.difference(near)), tidy(tidy(s.buffer(-U(PATH_FILLET), 32).buffer(U(PATH_FILLET), 32)).intersection(near))]))
    zone = corridors.buffer(U(PATH_FILLET * 2))
    for r_ in (PATH_FILLET, 28, 18):
        rem = s.difference(tidy(s.buffer(-U(r_), 32).buffer(U(r_), 32)))
        wedges = [g for g in polys(rem) if g.area * FT * FT < 0.6 * r_ ** 2 and g.intersects(zone)]
        if wedges:
            s = tidy(s.difference(tidy(unary_union(wedges).buffer(U(.05)))))
    arm = PATH_B_ARM.intersection(pasture).difference(unary_union([road.buffer(U(4)), corridors]))
    s = tidy(unary_union([s, tidy(arm), tidy(TRI_POND.buffer(U(10)))]))
    s = tidy(tidy(s.buffer(U(4), 16).buffer(-U(4), 16)).difference(corridors))             # no slits along the fence lines between paddocks
    return unary_union(polys(s, 0.03))


lo, hi = 0.0, 160.0
for _ in range(12):
    mid = (lo + hi) / 2
    got = swale_at(mid).intersection(open_pasture).area / open_pasture.area
    lo, hi = (mid, hi) if got > TARGET_SWALE else (lo, mid)
reach = (lo + hi) / 2
swale = swale_at(reach)
in_open = swale.intersection(open_pasture)
high = open_pasture.difference(swale).buffer(0)
by_paddock = [{"acres": round(acres(pd), 1), "open": round(acres(pd.intersection(open_pasture)), 1),
               "high_pct": round(100 * (1 - pd.intersection(in_open).area / max(pd.intersection(open_pasture).area, 1e-6)))} for pd in pads]

# ---- culverts: wherever a path crosses a centerline, plus the road crossing
culverts = []
for (name, _, _), pl in zip(PATHS, path_lines):
    for cl in centerlines:
        x = pl.intersection(cl)
        for pt in getattr(x, "geoms", [x]):
            if pt.geom_type == "Point" and all(pt.distance(Point(q["at"])) > U(40) for q in culverts):
                t = cl.project(pt)
                p0, p1 = cl.interpolate(max(t - U(PATH_W / 2 + 6), 0)), cl.interpolate(min(t + U(PATH_W / 2 + 6), cl.length))
                culverts.append({"path": name, "at": [round(pt.x, 1), round(pt.y, 1)], "line": [[round(p0.x, 1), round(p0.y, 1)], [round(p1.x, 1), round(p1.y, 1)]]})
road_line = LineString(ROAD_CULVERT)

# every piece of swale must drain: pieces are joined by the culverts, the road crossing, and the pond
_pieces = polys(swale)
# (the entry drive's crossing is the stretch of the main centerline that passes under the drive and its shoulders)
_entry = LineString(MAIN).intersection(Point(ENTRY_CULVERT[0]).buffer(U(110)))
_links = [LineString(c["line"]) for c in culverts] + [road_line, _entry]
_group = list(range(len(_pieces)))
def _find(i):
    while _group[i] != i: i = _group[i]
    return i
for ln in _links:
    hit = [i for i, g in enumerate(_pieces) if g.distance(ln) < U(110)]
    for i in hit[1:]: _group[_find(i)] = _find(hit[0])
for i, g in enumerate(_pieces):
    for j, h in enumerate(_pieces):
        if i < j and g.buffer(U(3)).intersects(pond) and h.buffer(U(3)).intersects(pond): _group[_find(j)] = _find(i)
_main = _find(max(range(len(_pieces)), key=lambda k: _pieces[k].area))
stranded = [round(acres(g), 2) for i, g in enumerate(_pieces) if _find(i) != _main]
swale = unary_union([g for i, g in enumerate(_pieces) if _find(i) == _main])      # a piece that cannot drain stays high ground
# the open channel on each side of the entry drive, leading to the replaced culvert
_drive = road.buffer(U(1))
swale = unary_union([swale, LineString([(1118, 502), (1145, 506), (1175, 520), (1192, 526)]).buffer(U(20)).difference(unary_union([_drive, hold_zone]))]).buffer(0)
in_open = swale.intersection(open_pasture)
high = open_pasture.difference(swale).buffer(0)
by_paddock = [{"acres": round(acres(pd), 1), "open": round(acres(pd.intersection(open_pasture)), 1),
               "high_pct": round(100 * (1 - pd.intersection(in_open).area / max(pd.intersection(open_pasture).area, 1e-6)))} for pd in pads]

# ---- cut and fill on a 5' grid from the survey's spots
spots = [s for s in json.load(open(os.path.join(DATA, "survey-spots.json")))["spots"] if not road.buffer(U(12)).contains(Point(s["map"]))]
P, Z = np.array([s["map"] for s in spots]), np.array([s["z"] for s in spots])
x0, y0, x1, y1 = pasture.union(pad_toe).bounds
gx, gy = np.meshgrid(np.arange(x0, x1, U(5)), np.arange(y0, y1, U(5)))
xy = np.c_[gx.ravel(), gy.ravel()]
ground = griddata(P, Z, xy, method="linear")
gap = np.isnan(ground); ground[gap] = griddata(P, Z, xy[gap], method="nearest")
near, _ = cKDTree(P).query(xy)
unsurveyed = near > U(80)
MEDIAN = float(np.median(Z[(Z < 23)]))
ground[unsurveyed] = MEDIAN
cell = 25.0 / 27                                                  # cubic yards per foot of depth on one cell
inside = lambda g: contains_xy(g, xy[:, 0], xy[:, 1])
m_pad, m_swale = inside(pad_toe), inside(swale)
m_swale &= ~m_pad
m_high = inside(unary_union([high, corridors.intersection(pasture)])) & ~m_pad & ~m_swale
fill_pad = float(np.clip(PAD_EL - ground[m_pad], 0, None).sum() * cell)
fill_high = float(np.clip(HIGH_EL - ground[m_high], 0, None).sum() * cell)

# ---- the graded surface of the swale and pond, on a 4' grid
G = 4.0
basin = unary_union([swale, pond]).buffer(0)
bx0, by0, bx1, by1 = basin.bounds
gxs, gys = np.arange(bx0 - U(40), bx1 + U(40), U(G)), np.arange(by0 - U(40), by1 + U(40), U(G))
X, Y = np.meshgrid(gxs, gys)
XY = np.c_[X.ravel(), Y.ravel()]
mask = contains_xy(basin, X, Y)
in_pond = contains_xy(pond, X, Y)
ex_ponds = unary_union([Polygon(p["pts"]).buffer(0) for p in json.load(open(os.path.join(DATA, "site-edits.json")))["ponds"] if p["kind"] == "existing" and pasture.contains(Polygon(p["pts"]).buffer(0).representative_point())])
in_ex = contains_xy(ex_ponds, X, Y) & mask
g2 = griddata(P, Z, XY, method="linear")
_gap = np.isnan(g2); g2[_gap] = griddata(P, Z, XY[_gap], method="nearest")
g2[cKDTree(P).query(XY)[0] > U(80)] = MEDIAN
g2 = g2.reshape(X.shape)
# top of bank: 22.00' all the way around, so the 1' contours run parallel to it and never pinch together
d_in = distance_transform_edt(mask, sampling=G)
d_out = distance_transform_edt(~mask, sampling=G)
tob = np.full(X.shape, HIGH_EL)


def burn(lines):
    out_ = np.zeros(X.shape, bool)
    for ln in lines:
        for part in getattr(ln, "geoms", [ln]):
            c_ = np.array(part.coords)
            cx, cy = np.clip(((c_[:, 0] - gxs[0]) / U(G)).astype(int), 0, X.shape[1] - 1), np.clip(((c_[:, 1] - gys[0]) / U(G)).astype(int), 0, X.shape[0] - 1)
            for a0, b0, a1, b1 in zip(cy, cx, cy[1:], cx[1:]):
                rr, cc = raster_line(a0, b0, a1, b1); out_[rr, cc] = True
    return out_


# distance along the flow to the pond, carried through the culverts
_flow = [LineString(c["line"]) for c in culverts] + [road_line, LineString(MAIN).intersection(Point(ENTRY_CULVERT[0]).buffer(U(110)))]
passable = mask | burn(_flow)
_st = np.argwhere(in_pond)
s_ft = MCP_Geometric(np.where(passable, 1.0, -1.0)).find_costs([tuple(q) for q in _st[::3]])[0] * G
s_ft[~np.isfinite(s_ft)] = 3500
floor = np.interp(s_ft, *MAIN_FLOOR)
# the north triangle drains to its own pond, not to the main pond
in_tri = contains_xy(TRI_SIDE.buffer(U(3)), X, Y) & mask
in_tp = contains_xy(TRI_POND, X, Y)
_st2 = np.argwhere(in_tp)
s_t = MCP_Geometric(np.where(in_tri | burn([LineString(c["line"]) for c in culverts if c["path"] == "Path C"]), 1.0, -1.0)).find_costs([tuple(q) for q in _st2[::2]])[0] * G
s_t[~np.isfinite(s_t)] = 2600
floor[in_tri] = np.interp(s_t[in_tri], *TRI_FLOOR)     # the pasture floor stays above the pond's water
d_cl = distance_transform_edt(~burn(centerlines), sampling=G)
z = np.minimum(np.maximum(floor + d_cl * 0.001, tob - d_in / SWALE_SIDE), tob)
# at the two corners the ground falls evenly from top of bank to the swale bottom instead of a steep bank and a flat floor
_soft_w = gaussian_filter(contains_xy(SOFT_ZONES, X, Y).astype(float), 7)
_t = d_cl / np.maximum(d_cl + d_in, 1e-6)
z = z * (1 - _soft_w) + (floor + (tob - floor) * _t ** 1.5) * _soft_w
z = np.minimum(z, floor + d_cl / 4)                                # a low-flow invert carried through the narrow arms
# the deep pool: 4:1 down from the shelf and from the banks held on the east and south
d_shelf = distance_transform_edt(~(mask & ~in_pond), sampling=G)
z[in_pond] = np.maximum.reduce([np.full(in_pond.sum(), POND_BOTTOM), SHELF_EL - d_shelf[in_pond] / POND_SIDE, tob[in_pond] - d_in[in_pond] / POND_SIDE])
d_ex = distance_transform_edt(in_ex, sampling=G)
z[in_ex] = np.maximum(14.0, SHELF_EL - d_ex[in_ex] / POND_SIDE)
d_tp = distance_transform_edt(in_tp, sampling=G)
_tp_out = distance_transform_edt(~in_tp, sampling=G)
z = np.where(mask & ~in_tp, np.minimum(z, TRI_NWL - 0.5 + _tp_out / POND_SIDE), z)         # banks come down to the pond at 4:1
z[in_tp] = np.maximum(TRI_BOTTOM, TRI_NWL - 0.5 - d_tp[in_tp] / POND_SIDE)
z_raw = z.copy()
# eased so the contours turn in curves, not creases; the pond keeps its crisper banks
_ease = lambda sig: gaussian_filter(np.where(mask, z, tob + d_out / SWALE_SIDE), sig)     # the bank's slope carries past its top, so easing cannot pull the top down
z = np.where(mask, np.where(in_pond | in_tp, _ease(1.2), _ease(2.6)), np.nan)
z = np.where(mask & ~in_pond & ~in_tp, np.minimum(z, gaussian_filter(floor + d_cl / 4, 0.8) + 0.03), z)
# no bank is ever steeper than this, even where a low-flow line runs out to a culvert: the 21' contour stays clear of the 22'
d_edge = d_in.copy()
_rim = mask & (d_in < 24)
d_edge[_rim] = sh_distance(sh_points(X[_rim], Y[_rim]), basin.boundary) * FT
bank_limit = HIGH_EL - d_edge / np.where(in_pond | in_tp, POND_SIDE, 5.0)
z = np.where(mask, np.maximum(z, bank_limit), z)      # the low-flow line stays true


# ---- every culvert runs out to the invert of its swale on both sides: the nearest point of the swale's floor that a
# straight pipe can reach without leaving the swale, the path, or the road embankment
_h = np.nan_to_num(z, nan=99.0) - floor
_low = mask & ~in_ex & ~in_pond & ~in_tp & ((_h <= 0.45) | (burn(centerlines) & (_h <= 1.2)))      # a narrow arm's invert is its centerline
_inv = np.c_[X[_low], Y[_low]]
_reach = unary_union([basin, corridors.buffer(U(100)), road.buffer(U(ROAD_STRIP + 30))])


def to_invert(x_, n_, clear_ft=12):
    rel = _inv - np.array(x_)
    side = rel @ np.array(n_)
    cand = _inv[(side > U(clear_ft)) & (((rel ** 2).sum(1)) < U(260) ** 2)]
    cand = cand[np.argsort(((cand - np.array(x_)) ** 2).sum(1))]
    for q in cand[::2][:500]:
        if LineString([x_, tuple(q)]).difference(_reach).length < U(2):
            return (float(q[0]), float(q[1]))
    return tuple(x_)


def unit(v_):
    v_ = np.array(v_, float)
    return v_ / np.linalg.norm(v_)


for c_ in culverts:
    pl_ = path_lines[[n_ for n_, _, _ in PATHS].index(c_["path"])]
    t_ = pl_.project(Point(c_["at"]))
    q0, q1 = pl_.interpolate(max(t_ - U(6), 0)), pl_.interpolate(min(t_ + U(6), pl_.length))
    tan_ = unit((q1.x - q0.x, q1.y - q0.y)); nor_ = np.array([-tan_[1], tan_[0]])
    x_ = tuple(c_["at"])
    c_["line"] = [[round(a_, 1), round(b_, 1)] for a_, b_ in (to_invert(x_, nor_, PATH_W / 2 + 4), to_invert(x_, -nor_, PATH_W / 2 + 4))]
_em = tuple(np.mean(ENTRY_CULVERT, 0)); _en = unit(np.array(ENTRY_CULVERT[1]) - np.array(ENTRY_CULVERT[0]))
entry_run = [to_invert(_em, -_en), to_invert(_em, _en)]
_rm = tuple(np.mean(ROAD_CULVERT, 0)); _rn = unit(np.array(ROAD_CULVERT[1]) - np.array(ROAD_CULVERT[0]))
road_run = list(ROAD_CULVERT)
outfall_run = [to_invert(OUTFALL_LINK[0], (-1.0, 0.0), 4), OUTFALL_LINK[1]]


def _el(q):
    i_, j_ = int(round((q[1] - gys[0]) / U(G))), int(round((q[0] - gxs[0]) / U(G)))
    return None if np.isnan(z[i_, j_]) else round(float(z[i_, j_]), 2)


culvert_check = [{"name": c_["path"], "ft": round(LineString(c_["line"]).length * FT), "ends_el": [_el(c_["line"][0]), _el(c_["line"][-1])]} for c_ in culverts] + [
    {"name": n_, "ft": round(LineString(r_).length * FT), "ends_el": [_el(r_[0]), _el(r_[-1]) if n_ != "Outfall" else None]} for n_, r_ in (("Road", road_run), ("Entry drive", entry_run), ("Outfall", outfall_run))]

to_xy = lambda c_: [(float(np.interp(q[1], np.arange(len(gxs)), gxs)), float(np.interp(q[0], np.arange(len(gys)), gys))) for q in c_]
LEVELS = list(range(13, 22))
z_full = gaussian_filter(np.where(mask, z, tob + d_out / SWALE_SIDE), 1.0)
z_full = np.where(mask, np.maximum(z_full, bank_limit), z_full)              # carried past the bank so each contour runs to its end
contours, el_labels = [], []
for L in LEVELS:
    pieces = [LineString(to_xy(c_)).intersection(basin) for c_ in find_contours(z_full, L) if len(c_) > 12]
    runs = sorted((g for x_ in pieces for g in getattr(x_, "geoms", [x_]) if g.geom_type == "LineString"), key=lambda g: -g.length)
    runs = [g.simplify(U(1.0)) for g in runs if g.length > U(45)]
    if L == 18:                                                    # 18' in the triangle is under its pond's water, not the main pond's level
        _tz = TRI_SIDE.buffer(U(3))
        contours.append({"el": 18.01, "lines": [[[round(a_, 1), round(b_, 1)] for a_, b_ in g.coords] for g in runs if _tz.contains(g.representative_point())]})
        runs = [g for g in runs if not _tz.contains(g.representative_point())]
    contours.append({"el": L, "lines": [[[round(a_, 1), round(b_, 1)] for a_, b_ in g.coords] for g in runs]})
    placed = []
    for g in runs[:14]:
        q = g.interpolate(0.5, normalized=True)
        if all(q.distance(o) > 75 for o in placed) and len(placed) < 6:
            placed.append(q); el_labels.append({"el": L, "at": [round(q.x, 1), round(q.y, 1)]})
_tri_pool = [LineString(to_xy(c_)).intersection(TRI_SIDE) for c_ in find_contours(z_full, TRI_NWL) if len(c_) > 8]
contours.append({"el": TRI_NWL, "pool": True, "lines": [[[round(a_, 1), round(b_, 1)] for a_, b_ in g.coords] for x_ in _tri_pool for g in getattr(x_, "geoms", [x_]) if g.geom_type == "LineString" and g.length > U(20)]})
el_labels = [q for q in el_labels if not TRI_POND.buffer(U(40)).contains(Point(q["at"]))]
el_labels.append({"el": TRI_NWL, "text": f"NWL {TRI_NWL:.2f}'", "at": [round(TRI_POND.centroid.x, 1), round(TRI_POND.centroid.y + 1, 1)]})
_zf = np.pad(np.where(mask, z, 30.0), 1, constant_values=30.0)


def below(L):
    g = Polygon()
    for c_ in find_contours(_zf, L):
        if len(c_) >= 8:
            r_ = Polygon(to_xy(c_ - 1)).buffer(0)
            if r_.area > U(6) ** 2:
                g = g.symmetric_difference(r_)
    return g.intersection(basin).buffer(0)


def area_json(p_):
    q_ = p_.simplify(U(.8))
    return {"outer": [[round(a_, 1), round(b_, 1)] for a_, b_ in q_.exterior.coords], "holes": [[[round(a_, 1), round(b_, 1)] for a_, b_ in h_.coords] for h_ in q_.interiors]}


bands = [{"el": L, "areas": [area_json(p_) for p_ in polys(below(L), 0.002)]} for L in (21, 20, 19, 18, 16, 14)]
bands.insert(3, {"el": TRI_NWL, "areas": [area_json(p_) for p_ in polys(below(TRI_NWL).intersection(TRI_SIDE), 0.002)]})
cell2 = G * G / 27
_g, _z = g2[mask], z[mask]
cut = float(np.clip(_g - _z, 0, None).sum() * cell2)
fill_basin = float(np.clip(_z - _g, 0, None).sum() * cell2)
# floodplain storage counts only above the normal water level: the permanent pool holds no flood water
lost = float((np.clip(BFE - np.maximum(ground[m_pad], NWL), 0, None).sum() + np.clip(BFE - np.maximum(ground[m_high], NWL), 0, None).sum()) * cell)
gained = float(np.clip(np.minimum(_g, BFE) - np.maximum(np.minimum(_z, BFE), np.where(in_tri, TRI_NWL, NWL)[mask]), 0, None).sum() * cell2)
pool = below(NWL)
_hold_pt = pond.exterior.interpolate(pond.exterior.project(Point(pond.centroid.x, pond.bounds[1])))
_south_y = pond.centroid.y

# ---- the pad's slopes as contours: true offsets of its edge at 4:1. The 22' line runs all the way round; the 21' line
# shows only where the slope lands on ground lower than the high-ground plane
_plane = unary_union([high, corridors, hubs, basin])
# Path A leaves the pad on a gentle ramp, 22.70' down to 22.00' over 70' (1%), the contours running out along the path
_a1, _a0 = np.array(PATHS[0][2][0]), np.array(PATHS[0][2][-1])
_v = (_a1 - _a0) / np.linalg.norm(_a1 - _a0)
_tongue = lambda L_, hw: LineString([tuple(_a0 - _v * U(6)), tuple(_a0 + _v * U(L_ - hw))]).buffer(U(hw), 32)
_root = Point(tuple(_a0)).buffer(U(RAMP_LEN))
_fair = lambda g, r: unary_union([g, g.buffer(U(r), 32).buffer(-U(r), 32).intersection(_root)]).buffer(0)
_ring = lambda L: pad.buffer(U((PAD_EL - L) * 4), join_style=2)
_lines22 = _fair(unary_union([_ring(22), _tongue(RAMP_LEN, RAMP_HW)]), 14).exterior.difference(basin)
_ln = lambda g_: [[[round(a_, 1), round(b_, 1)] for a_, b_ in g.coords] for g in getattr(g_, "geoms", [g_]) if g.geom_type in ("LineString", "LinearRing") and g.length > U(6)]
pad_contours = [{"el": 22, "lines": _ln(_lines22)}]
ramp_labels = [{"at": [round(v_, 1) for v_ in _a0 + _v * U(RAMP_LEN - 8)], "text": "22'"}]

rnd = lambda p: [[round(x, 1), round(y, 1)] for x, y in p]
ring = lambda g: {"outer": rnd(g.exterior.coords), "holes": [rnd(h.coords) for h in g.interiors]}
out = {
    "note": "Planning concept of the owner's 2026-11-18 stormwater direction. BFE is the modelled 100-year elevation.",
    "elevations": {"bfe": BFE, "pad": round(PAD_EL, 2), "high_ground": HIGH_EL, "nwl": NWL, "tri_nwl": TRI_NWL, "tri_bottom": TRI_BOTTOM, "shelf": SHELF_EL, "swale_side": SWALE_SIDE, "pond_side": POND_SIDE, "pond_bottom": POND_BOTTOM,
                   "swale_average": round(float(np.nanmean(z[mask & ~in_pond & ~in_ex])), 1)},
    "pad": ring(pad), "pad_toe": ring(max(polys(pad_toe), key=lambda p: p.area)), "on_pad": on_pad,
    "swale": [ring(p.simplify(U(1))) for p in polys(swale)],
    "high_ground": [ring(p.simplify(U(1))) for p in polys(high, 0.01)],
    "pond": ring(pond), "basin": [ring(p) for p in polys(basin)], "contours": contours, "contour_labels": el_labels, "bands": bands,
    "outfall_link": rnd(outfall_run), "culvert_check": culvert_check, "tri_pond": ring(TRI_POND), "tri_pond_label": [round(TRI_POND.centroid.x, 1), round(TRI_POND.bounds[1] - U(16), 1)],
    "outlet_invert_at_bend": round(float(floor[int(round((395 - gys[0]) / U(G))), int(round((716 - gxs[0]) / U(G)))]), 2), "pad_contours": pad_contours, "ramp_labels": ramp_labels, "pad_label": [round(v, 1) for v in to_map(-62, 120)],
    "holds": {"east": [round(_hold_pt.x, 1), round(_hold_pt.y, 1)], "south_bank": [round(_sx0 - U(SOUTH_HOLD) + (_sx1 - _sx0) * (_sy0 - _south_y) / (_sy0 - _sy1), 1), round(_south_y, 1)],
              "south_fence": [round(_sx0 + (_sx1 - _sx0) * (_sy0 - _south_y) / (_sy0 - _sy1), 1), round(_south_y, 1)], "shelf": [1205, 531]},
    "pool_ac": round(acres(pool), 1),
    "existing_ponds": [ring(Polygon(p["pts"]).buffer(0)) for p in json.load(open(os.path.join(DATA, "site-edits.json")))["ponds"] if p["kind"] == "existing" and pasture.contains(Polygon(p["pts"]).buffer(0).representative_point())],
    "entry_culvert": rnd(entry_run), "by_paddock": by_paddock, "stranded_swale_ac": stranded,
    "woods_cleared_ac": round(acres(swale.intersection(canopy).difference(bed)), 2),
    "centerlines": [rnd(g.coords) for g in centerlines],
    "paths": [{"name": n, "what": w, "line": rnd(l), "corridor": ring(c)} for (n, w, l), c in zip(PATHS, polys(corridors) if len(polys(corridors)) == len(PATHS) else [g.buffer(U(PATH_W / 2), cap_style=2) for g in path_lines])],
    "hubs": [list(h) for h in HUBS], "culverts": culverts, "road_culvert": rnd(road_run),
    "areas_ac": {"pasture_fenced": round(acres(pasture), 1), "open_pasture": round(acres(open_pasture), 1), "swale_in_open": round(acres(in_open), 1),
                 "high_ground_in_open": round(acres(open_pasture) - acres(in_open), 1), "swale_total": round(acres(swale), 1),
                 "pond_designed": round(acres(pond_design), 2), "pad": round(acres(pad), 1), "pad_with_slopes": round(acres(pad_toe), 1), "pond": round(acres(pond), 1), "bed_existing": round(acres(bed), 1)},
    "swale_share_of_open": round(in_open.area / open_pasture.area, 3), "woods_band_ft": round(reach),
    "earthwork_cy": {"cut_swale_and_pond": round(cut, -2), "fill_in_basin": round(fill_basin, -2), "fill_pad": round(fill_pad, -2), "fill_high_ground": round(fill_high, -2),
                     "net_cut": round(cut - fill_basin - fill_pad - fill_high, -2), "storage_lost_below_bfe": round(lost, -2), "storage_gained_below_bfe": round(gained, -2)},
    "survey_gap": {"share_of_swale_unsurveyed": round(float(unsurveyed[m_swale].mean()), 2), "assumed_grade": round(MEDIAN, 1)},
}
open(os.path.join(DATA, "stormwater-concept.js"), "w", encoding="utf8").write("window.STORMWATER = " + json.dumps(out) + ";\n")
print(json.dumps({k: out[k] for k in ("areas_ac", "swale_share_of_open", "woods_band_ft", "by_paddock", "stranded_swale_ac", "woods_cleared_ac", "earthwork_cy", "survey_gap")}, indent=1))
print("swale pieces", len(polys(swale)), [round(acres(p), 2) for p in polys(swale)], "| pad elements", len(on_pad))
print("pad overlaps existing bed (ac)", round(acres(pad_toe.intersection(bed)), 2), "| road culvert ft", round(road_line.length * FT))
