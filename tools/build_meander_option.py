"""Option: a meandering low-flow channel cut into the floor of the stormwater concept's swales.

Reads drawings/data/stormwater-concept.js and never changes it. Writes drawings/data/stormwater-meander-option.js, which
tools/sheet.html draws only when asked for the option (?option=meander). The base plan stays as it is.

The channel bends on true arcs of one radius wherever its full width fits on the swale floor, and runs straight into every
culvert, junction, and pool. Coordinates are the site map's presentation frame (1 unit = 2.59 ft). Distances are feet.
Run: python tools/build_meander_option.py     Needs: numpy, scipy, shapely, scikit-image.
"""
import json, math, os, re
import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter, gaussian_filter1d, map_coordinates
from shapely import contains_xy
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import substring, unary_union
from skimage.graph import route_through_array

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DATA = os.path.join(ROOT, "drawings", "data")
FT = 2.59

# ---- design decisions (all assumed until civil confirms them)
RADIUS = 15                  # bend radius
SWING = 75                   # how far each bend turns off the swale's axis, degrees
DEPTH = 1.0                  # below the normal water level, so the channel always holds water
BOTTOM, SIDE = 2.0, 2.0      # bottom width, and side slope horizontal to 1 vertical
HOLD = 30                    # straight run kept at each culvert, junction, and pool
EDGE = 3                     # the channel's edge stays this far inside the floor
FLOOR_EL = 19                # the swale floor is the ground below this contour
NECK_DEPTH = 2.0             # typical cut where the channel crosses a narrow arm above the floor

WIDTH = BOTTOM + 2 * SIDE * DEPTH


def tier(deg, radius=RADIUS, leg=0):
    """One bend shape. Narrower floor: the bends swing less. Wider floor: a straight leg between bends reaches farther."""
    phi = math.radians(deg)
    peak = (2 * radius * (1 - math.cos(phi)) + leg * math.sin(phi)) / 2        # the bends' reach to each side of the axis
    tl = (peak - 2 * radius * (1 - math.cos(phi))) / math.sin(phi)              # the first and last bends ease on and off the axis
    alpha = phi if tl > 0 else math.acos(1 - peak / (2 * radius))
    tl = max(tl, 0)
    return {"phi": phi, "alpha": alpha, "r": radius, "leg": leg, "tl": tl, "belt": 2 * peak + WIDTH,
            "lead": 2 * (2 * radius * math.sin(alpha) + tl * math.cos(alpha)), "half": 2 * radius * math.sin(phi) + leg * math.cos(phi)}


TIERS = [tier(d) for d in (SWING, 60, 45)]
BELT = TIERS[0]["belt"]
# the architect's wide spot in the 4.8 ac paddock. Bends reach farther here only.
WIDE_RADIUS, WIDE_SWING = 20, 85
WIDE_TIERS = [dict(tier(WIDE_SWING, WIDE_RADIUS, leg), wide=True) for leg in (60, 40, 25, 10, 0)]
WIDE_ZONES = [Polygon([(814, 332), (923, 332), (923, 424), (814, 424)])]

src = open(os.path.join(DATA, "stormwater-concept.js"), encoding="utf8").read()
SW = json.loads(src[src.index("{"):src.rindex("}") + 1])
CL = [LineString(c) for c in SW["centerlines"]]
CULV = {c["path"]: c["line"] for c in SW["culverts"]}
ENTRY = SW["entry_culvert"]
ring = lambda a: Polygon(a["outer"], a["holes"]).buffer(0)
band = lambda el: unary_union([ring(a) for b in SW["bands"] if b["el"] == el for a in b["areas"]])
FLOOR = band(FLOOR_EL)
POOL = unary_union([band(18), band(SW["elevations"]["tri_nwl"]), ring(SW["pond"]), ring(SW["tri_pond"])])
BASIN = unary_union([ring(b) for b in SW["basin"]])

BEND, JA, JT, JW = (716, 395), (1000, 392), (520, 388), (345, 425)
PA, PB, PC = CULV["Path A"], CULV["Path B"], CULV["Path C"]
PIPE = {}                                                           # each culvert end, and the direction the channel leaves it
for _a, _b in (PA, PB, PC, ENTRY):
    _n = math.dist(_a, _b)
    PIPE[tuple(_a)] = ((_a[0] - _b[0]) / _n, (_a[1] - _b[1]) / _n); PIPE[tuple(_b)] = ((_b[0] - _a[0]) / _n, (_b[1] - _a[1]) / _n)
# side, centerline, from, to, which ends stop at a pool (0 = start, 1 = end)
SEGMENTS = [
    ("main", 0, (712, 345), BEND, [0]),
    ("main", 0, BEND, PB[0], []),
    ("main", 0, PB[1], JA, []),
    ("main", 0, JA, ENTRY[0], []),
    ("main", 0, ENTRY[1], (1200, 524), [1]),
    ("main", 1, JA, PA[0], []),
    ("main", 1, PA[1], (1022, 285), ["free"]),
    ("main", 2, (672, 318), (578, 300), [0, "free"]),
    ("main", 3, (726, 316), (885, 298), [0, "free"]),
    ("triangle", 5, (650, 412), JT, [0]),
    ("triangle", 5, JT, PC[0], []),
    ("triangle", 5, PC[1], JW, []),
    ("triangle", 7, JT, (398, 286), ["free"]),
    ("triangle", 8, JW, (140, 320), ["free"]),
]
VIA = {(tuple(PB[1]), JA): [(830, 384), (868, 378), (906, 384)]}    # carried through the middle of the 4.8 ac paddock
END_AT = {(1022, 285): (1055, 218.7)}                               # the branch east of Path A runs on into the upper floor of the 7.8 ac paddock
# the architect's sketch of that branch, followed as drawn: a wide S on the lower floor, then north through the neck
DRAWN = {(tuple(PA[1]), (1022, 285)): [tuple(PA[1]), (1027, 325), (1030.3, 316), (1023.7, 311), (1005, 310.7), (993.7, 309.3), (992.3, 304.4), (995, 298.7),
                                       (1013.7, 295.9), (1028, 291.6), (1033.2, 284.4), (1029.4, 275.9), (1028, 268.7), (1032.8, 256), (1032.2, 243.1),
                                       (1027.9, 231.6), (1030.8, 226.4), (1045, 225.3), (1055, 224.4), (1055, 218.7)]}

# ---- the surveyed tree canopy, from the site map
_map = open(os.path.join(ROOT, "slides", "data", "site-map.js"), encoding="utf8").read()
_svg = json.loads(_map[_map.index("{"):_map.rindex("}") + 1])["svg"]
CANOPY = Polygon()
for _d in re.findall(r' d="([^"]+)"', re.search(r'<g id="canopy"[^>]*>(.*?)</g>', _svg, re.S).group(1)):
    for _s in re.finditer(r"M([^MZ]*)Z?", _d):
        _n = [float(v) for v in re.findall(r"-?\d+\.?\d*", _s.group(1))]
        if len(_n) >= 6:
            _p = Polygon(list(zip(_n[0::2], _n[1::2]))).buffer(0)
            if _p.area > 0: CANOPY = CANOPY.symmetric_difference(_p)
CANOPY = CANOPY.buffer(0)

# ---- clearances, in feet, on a one-unit grid
x0, y0, x1, y1 = [int(v) for v in BASIN.bounds]
gx, gy = np.arange(x0 - 5, x1 + 6), np.arange(y0 - 5, y1 + 6)
XX, YY = np.meshgrid(gx, gy)
ISLANDS = unary_union([Polygon(h) for g in getattr(BASIN, "geoms", [BASIN]) for h in g.interiors if Polygon(h).intersects(CANOPY)])    # canopy the swale wraps around
OPEN = contains_xy(BASIN, XX, YY)                                    # the swale, with those stands of trees left out
BANKS = distance_transform_edt(OPEN) * FT                            # distance to the nearest top of bank
CLEAR = distance_transform_edt(contains_xy(FLOOR, XX, YY) & OPEN) * FT   # distance to the edge of the usable floor
SOFT = gaussian_filter(BANKS, 1.2)
GY, GX = np.gradient(SOFT)
COST = np.where(OPEN, 1 + 500 / (1 + BANKS) ** 2, 800.0)             # the line midway between the banks is cheapest; trees and high ground the dearest
at = lambda grid, p: map_coordinates(grid, [p[:, 1] - gy[0], p[:, 0] - gx[0]], order=1, mode="nearest")


def resample(p, step=1 / FT):
    ln = LineString(p)
    return np.array([ln.interpolate(s).coords[0] for s in np.linspace(0, ln.length, max(int(ln.length / step), 3))])


def piece(i, a, b, pool_ends):
    """The stretch of a centerline between two points, trimmed where it enters a pool."""
    ln = CL[i]
    sa, sb = ln.project(Point(a)), ln.project(Point(b))
    mid = [c for c in substring(ln, sa, sb).coords][1:-1]
    for e in (a, b):                                                # a culvert end off the centerline is met in one easy curve
        if ln.distance(Point(e)) > 2 or tuple(e) in PIPE: mid = [c for c in mid if math.dist(c, e) > 22]
    lead = lambda e: [(e[0] + PIPE[tuple(e)][0] * HOLD / FT, e[1] + PIPE[tuple(e)][1] * HOLD / FT)] if tuple(e) in PIPE else []   # straight off the pipe's own line
    out = LineString([tuple(a)] + lead(a) + mid + lead(b)[::-1] + [tuple(b)])
    if 0 in pool_ends or 1 in pool_ends:
        rest = out.difference(POOL)
        out = max(getattr(rest, "geoms", [rest]), key=lambda g: g.length)
    if "free" in pool_ends:                                         # a branch stops where its floor runs out
        on = out.intersection(FLOOR)
        out = substring(out, 0, max(out.project(Point(g.coords[-1])) for g in getattr(on, "geoms", [on])))
    # the channel itself takes the best way along the floor between those two ends, around any high ground
    c = np.array(out.coords)
    head, tail = c[:1 + bool(lead(a))], c[-1 - bool(lead(b)):]
    if tuple(b) in END_AT: tail = np.array([END_AT[tuple(b)]], float)
    cell = lambda p: (int(round(p[1] - gy[0])), int(round(p[0] - gx[0])))
    stops = [head[-1]] + [np.array(v, float) for v in VIA.get((tuple(a), tuple(b)), [])] + [tail[0]]
    way = []
    for u, v in zip(stops, stops[1:]):
        leg_, _ = route_through_array(COST, cell(u), cell(v), fully_connected=True, geometric=True)
        way += leg_[1:] if way else leg_
    way = np.array([(gx[j], gy[i]) for i, j in way], float)
    return np.vstack([head, way[1:-1], tail])


def centered(p):
    """Eases the axis to the middle between the banks, with both ends pinned. Tight swales follow their banks closely."""
    p0 = resample(p); ends = p0[[0, -1]].copy()
    p0 = gaussian_filter1d(p0, 6, axis=0, mode="nearest"); p0[[0, -1]] = ends; p0 = resample(p0)
    q = p0.copy(); n = len(q)
    pin = np.clip((np.minimum(np.arange(n), np.arange(n)[::-1]) - HOLD * .6) / HOLD, 0, 1)[:, None]
    pin = pin * pin * (3 - 2 * pin)
    def ease(v, tight, wide):
        w = np.clip((gaussian_filter1d(at(BANKS, v), 12, mode="nearest") - 25) / 35, 0, 1)[:, None]    # 0 in a tight swale, 1 on open floor
        return gaussian_filter1d(v, tight, axis=0, mode="nearest") * (1 - w) + gaussian_filter1d(v, wide, axis=0, mode="nearest") * w
    for _ in range(120):
        g = np.c_[at(GX, q), at(GY, q)]
        g /= np.maximum(np.hypot(*g.T)[:, None], 1e-6)
        inside = (at(BANKS, q) > 0)[:, None]
        q = q + .4 * g * inside * pin
        q = q * (1 - pin) + ease(q, 9, 20) * pin
        d = q - p0; m = np.hypot(*d.T)[:, None]
        q = p0 + d * np.minimum(1, 14 / np.maximum(m, 1e-6))
    q = q * (1 - pin) + ease(q, 10, 26) * pin
    q[0], q[-1] = p0[0], p0[-1]
    return resample(q)


def off_center(axis):
    """How far the axis sits from the midpoint between its banks, where the swale is tight (ft)."""
    t = np.gradient(axis, axis=0); t /= np.maximum(np.hypot(*t.T)[:, None], 1e-9)
    nrm = np.c_[-t[:, 1], t[:, 0]]; res = []
    for i in range(int(HOLD), len(axis) - int(HOLD), 5):
        reach = []
        for sgn in (1, -1):
            d_ = 0.0
            while d_ < 110 and at(BANKS, (axis[i] + sgn * nrm[i] * (d_ + 1) / FT)[None])[0] > 0: d_ += 1
            reach.append(d_)
        if sum(reach) < 110: res.append(abs(reach[0] - reach[1]) / 2)
    return res


def arc_template(half_waves, T):
    """Station along the axis and offset from it (ft): true arcs of one radius, on and off the axis tangent."""
    moves = [(T["alpha"], T["tl"]), (0, 0)]                         # each move: turn to this heading, then run straight this far
    sign = -1
    for _ in range(half_waves):
        moves += [(sign * T["phi"], T["leg"]), (0, 0)]; sign = -sign
    moves += [(sign * T["alpha"], T["tl"]), (0, 0)]
    x, y, h, out = 0.0, 0.0, 0.0, [(0.0, 0.0)]
    for target, run in moves:
        steps = max(int(abs(target - h) * T["r"] / .5), 1); dh = (target - h) / steps; ds = abs(dh) * T["r"]
        for _ in range(steps):
            x += ds * math.cos(h + dh / 2); y += ds * math.sin(h + dh / 2); h += dh; out.append((x, y))
        for _ in range(int(run / .5)):
            x += .5 * math.cos(h); y += .5 * math.sin(h); out.append((x, y))
    return np.array(out)


def wiggle(axis, free_end=False):
    """The channel's line along one axis. Returns the line and the axis length that carries bends."""
    n = len(axis); seg = np.hypot(*np.diff(axis, axis=0).T) * FT
    s = np.r_[0, np.cumsum(seg)]; L = s[-1]
    t = np.gradient(axis, axis=0); t /= np.maximum(np.hypot(*t.T)[:, None], 1e-9)
    nrm = np.c_[-t[:, 1], t[:, 0]]
    free = (s >= HOLD) & (s <= L - (8 if free_end else HOLD))
    in_zone = np.array([any(z.contains(Point(q)) for z in WIDE_ZONES) for q in axis])
    runs = []
    for T in WIDE_TIERS + TIERS:                                   # the widest bends first, then gentler ones in what is left
        fits = free & (at(CLEAR, axis) >= T["belt"] / 2 + EDGE) & (in_zone if T.get("wide") else True)
        edges = np.flatnonzero(np.diff(np.r_[0, fits.astype(int), 0]))
        for a, b in zip(edges[::2], edges[1::2] - 1):
            room = s[b] - s[a]
            waves = int((room - T["lead"]) // T["half"])
            if waves < (2 if T.get("wide") else 1): continue           # the wide bends read as an even series, not one lone hump
            span = T["lead"] + waves * T["half"]
            start = s[a] + (room - span) / 2
            runs.append((start, span, waves, T))
            free &= ~((s >= start - 2) & (s <= start + span + 2))
    out, cursor, bent = [], 0.0, 0.0
    fx = lambda v: np.interp(v, s, axis[:, 0]); fy = lambda v: np.interp(v, s, axis[:, 1])
    fnx = lambda v: np.interp(v, s, nrm[:, 0]); fny = lambda v: np.interp(v, s, nrm[:, 1])
    straight = lambda a, b: [(fx(v), fy(v)) for v in np.arange(a, b, 1.0)]
    for start, span, waves, T in sorted(runs, key=lambda r: r[0]):
        out += straight(cursor, start)
        tp = arc_template(waves, T); sc = span / tp[-1, 0]         # the arcs land exactly on the end of the run
        for x_, y_ in tp:
            v = start + x_ * sc
            out.append((fx(v) + fnx(v) * y_ / FT, fy(v) + fny(v) * y_ / FT))
        cursor = start + span; bent += span
    out += straight(cursor, L) + [tuple(axis[-1])]
    clean = [out[0]] + [q for p_, q in zip(out, out[1:]) if math.hypot(q[0] - p_[0], q[1] - p_[1]) > 1e-3]
    return np.array(clean), bent


def min_radius(p, window=6.0):
    q = resample(p, .5 / FT) * FT; k = int(window / .5)
    q = q[50:-50]                                                  # the last 25' at each end meet a culvert, junction, or pool
    if len(q) <= 2 * k + 1: return 1e9
    a, b, c = q[:-2 * k], q[k:-k], q[2 * k:]
    ab, bc, ca = np.hypot(*(a - b).T), np.hypot(*(b - c).T), np.hypot(*(c - a).T)
    area = np.abs((b[:, 0] - a[:, 0]) * (c[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - a[:, 0])) / 2
    return float(np.min(ab * bc * ca / np.maximum(4 * area, 1e-9)))


lines, tally = [], {"main": [0, 0, 0, 0], "triangle": [0, 0, 0, 0]}     # axis ft, channel ft, ft bent, neck ft
checks = {"min_radius_ft": 1e9, "self_crossing": 0, "min_floor_clearance_ft": 1e9}
offs = []
for side, i, a, b, pools in SEGMENTS:
    raw = piece(i, a, b, pools)
    if LineString(raw).length * FT < 30:
        print(f"  {side:8s} cl{i} from {a}: skipped, under 30 ft of floor"); continue
    axis = centered(raw)
    offs += off_center(axis)
    drawn = DRAWN.get((tuple(a), tuple(b)))
    if drawn:                                                       # followed as sketched, only eased so the line runs smoothly
        p = resample(np.array(drawn, float)); _e = p[[0, -1]].copy()
        p = gaussian_filter1d(p, 7, axis=0, mode="nearest"); p[[0, -1]] = _e; p = resample(p)
        bent = LineString(axis).length * FT
    else:
        p, bent = wiggle(axis, "free" in pools)
    ln = LineString(p)
    if not ln.is_simple: checks["self_crossing"] += 1
    r_ = min_radius(p)
    checks["min_radius_ft"] = min(checks["min_radius_ft"], r_)
    print(f"  {side:8s} cl{i} {tuple(np.round(p[0]).astype(int).tolist())} to {tuple(np.round(p[-1]).astype(int).tolist())}: {ln.length * FT:5.0f} ft, bends over {bent:4.0f} ft, tightest radius {r_:5.1f} ft")
    off = LineString(axis).distance
    moved = resample(p); mv = np.array([off(Point(q)) * FT for q in moved]) > 4
    if mv.any() and not drawn: checks["min_floor_clearance_ft"] = min(checks["min_floor_clearance_ft"], float(at(CLEAR, moved[mv]).min()) - WIDTH / 2)
    t = tally[side]; t[0] += LineString(axis).length * FT; t[1] += ln.length * FT; t[2] += bent
    t[3] += ln.difference(FLOOR).length * FT
    lines.append({"side": side, "line": [[round(float(x), 2), round(float(y), 2)] for x, y in p[::2].tolist() + [p[-1].tolist()]]})

water = unary_union([LineString(l["line"]).buffer(WIDTH / 2 / FT, quad_segs=6) for l in lines]).simplify(.05)
wet = list(getattr(water, "geoms", [water]))
_out = water.difference(BASIN.buffer(1))
checks["outside_basin_sf"] = round(_out.area * FT * FT)
checks["tree_island_clearance_ft"] = round(water.distance(ISLANDS) * FT, 1)
checks["tight_swale_off_center_ft"] = {"typical": round(float(np.median(offs)), 1), "95th_percentile": round(float(np.percentile(offs, 95)), 1), "worst": round(float(np.max(offs)), 1)}
for g in getattr(_out, "geoms", [_out]):
    if g.area * FT * FT > 20: print(f"  outside the basin: {g.area * FT * FT:5.0f} sf near ({g.centroid.x:.0f}, {g.centroid.y:.0f})")
axis_ft, ch_ft, bent_ft, neck_ft = [sum(t[k] for t in tally.values()) for k in range(4)]
sec = lambda d: d * (BOTTOM + SIDE * d)                                    # cross section below the ground, sf
FLOOR_DEPTH = DEPTH + .1
cut = ((ch_ft - neck_ft) * sec(FLOOR_DEPTH) + neck_ft * sec(NECK_DEPTH)) / 27
near = lambda v, n: int(round(v / n) * n)
out = {
    "note": "Option only: a meandering low-flow channel in the swale floor of the 2026-11-18 stormwater concept. Assumed until civil confirms it.",
    "design": {"radius_ft": RADIUS, "wide_radius_ft": WIDE_RADIUS, "swing_deg": SWING, "width_ft": WIDTH, "depth_ft": DEPTH, "belt_ft": round(BELT), "wave_ft": round(2 * TIERS[0]["half"]),
               "invert_main": SW["elevations"]["nwl"] - DEPTH, "invert_triangle": SW["elevations"]["tri_nwl"] - DEPTH},
    "lines": lines,
    "water": [{"outer": [[round(x, 2), round(y, 2)] for x, y in g.exterior.coords], "holes": [[[round(x, 2), round(y, 2)] for x, y in h.coords] for h in g.interiors]} for g in wet],
    "stats": {"straight_run_ft": near(axis_ft, 10), "channel_ft": near(ch_ft, 10), "added_ft": near(ch_ft - axis_ft, 10), "added_pct": round((ch_ft / axis_ft - 1) * 100),
              "axis_with_bends_ft": near(bent_ft, 10), "cut_cy": near(cut, 10), "wet_ac": round(ch_ft * WIDTH / 43560, 1),
              "by_side": {k: {"straight_run_ft": near(v[0], 10), "channel_ft": near(v[1], 10)} for k, v in tally.items()}},
    "checks": {k: round(v, 1) if isinstance(v, float) else v for k, v in checks.items()},
}
open(os.path.join(DATA, "stormwater-meander-option.js"), "w", encoding="utf8").write("window.MEANDER_OPTION = " + json.dumps(out, separators=(",", ":")) + ";\n")
print(json.dumps({k: out[k] for k in ("design", "stats", "checks")}, indent=1))
