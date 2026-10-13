"""Approximate the unsurveyed drives on the south part of the property.

The survey's edge-of-pavement lines stop at the campus. South of there the drives are approximated from two sources:
  lane     the lane that carries on along Cow Pen Slough: located from the drive pixels of the aerial trace
           (drawings/data/aerial-derived.json), measured as an offset from the west property line, bridged
           where trees hide it, and smoothed. It starts at the end of the surveyed road.
  drives   the two drive lines on the fencing plan's sketch layer (P-BELOW-LIGHT) that the aerial confirms: the
           one from the lane past the house to the long barn, and the one to the south building and round it.
Writes drawings/data/south-roads.json: centrelines in the map's presentation frame with a width in feet.
These are approximations for the diagram, not survey. Run after build_fences.py and build_canopy.py.

Run:  python tools/build_south_roads.py
"""
import json, os, re, sys
import numpy as np
from scipy import ndimage
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely.prepared import prep

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from siteframe import OUT, FENCE, cadpdf, M_FP, T_FP, FT_PER_PT

unit_ft = FT_PER_PT / abs(M_FP)
F = json.load(open(os.path.join(OUT, "data", "fences.json")))
A = json.load(open(os.path.join(OUT, "data", "aerial-derived.json")))
E = json.load(open(os.path.join(OUT, "data", "site-edits.json")))
site = Polygon(E["boundary"]).buffer(0)

# drive pixels from the trace, as polygons
polys = []
for sub in A["drives"].split("M")[1:]:
    q = [tuple(map(float, p.split())) for p in re.findall(r"[-\d.]+ [-\d.]+", sub)]
    if len(q) >= 3:
        polys.append(Polygon(q).buffer(0))
trace = prep(unary_union(polys).buffer(1.5))

# ---- the lane along the slough
road_end = np.mean([F["roads"][1]["map"][-1], F["roads"][2]["map"][0]], axis=0)       # middle of the surveyed road's south end
lane_w = float(np.hypot(*(np.array(F["roads"][1]["map"][-1]) - np.array(F["roads"][2]["map"][0])))) * unit_ft
sketch = []
for d in cadpdf.export(FENCE, ["P-BELOW-LIGHT"]).get("P-BELOW-LIGHT", []):
    pts = []
    for it in d["items"]:
        if it[0] in ("l", "c"):
            e_ = it[2] if it[0] == "l" else it[4]
            if not pts:
                pts.append(it[1])
            pts.append(e_)
    q = [M_FP * complex(p.x, p.y) + T_FP for p in pts]
    q = [(z.real, z.imag) for z in q]
    if len(q) >= 10 and LineString(q).length > 150 and min(x for x, _ in q) > 1290:
        sketch.append(LineString(q))
sketch.sort(key=lambda g: g.bounds[0])                      # house drive first, south building drive second
south_start = Point(sketch[-1].coords[0])                    # where the south building drive leaves the lane

west = max((LineString(r["map"]) for r in F["property_lines"] if len(r["map"]) > 8), key=lambda g: g.bounds[2])   # the slough's centreline, south run
s0, s1 = sorted((west.project(Point(*road_end)), west.project(south_start)))
step = 6.0
ss = np.arange(max(s0, 3.0), min(s1, west.length - 3.0), step)       # stay inside the line: its ends have no direction
probe = np.arange(6, 70, 1.0)
offs, pts_, nrm = [], [], []
for s in ss:
    p, p2 = west.interpolate(s), west.interpolate(min(west.length, s + 2))
    p1 = west.interpolate(max(0, s - 2))
    t = np.array([p2.x - p1.x, p2.y - p1.y]); t /= np.linalg.norm(t) or 1
    n = np.array([-t[1], t[0]])
    if not site.contains(Point(p.x + n[0] * 30, p.y + n[1] * 30)):
        n = -n                                               # the normal points into the site
    hit = [o for o in probe if trace.contains(Point(p.x + n[0] * o, p.y + n[1] * o))]
    # the lane is the first band of drive pixels in from the bank
    if hit:
        band = [hit[0]]
        for o in hit[1:]:
            if o - band[-1] > 1.5:
                break
            band.append(o)
        offs.append(float(np.mean(band)))
    else:
        offs.append(np.nan)
    pts_.append((p.x, p.y)); nrm.append(n)
offs = np.array(offs)
# pin both ends: the surveyed road's end, and the junction with the south building drive
end_off = [west.distance(Point(*road_end)), west.distance(south_start)]
if west.project(Point(*road_end)) > west.project(south_start):
    end_off = end_off[::-1]
offs[0], offs[-1] = end_off
good = ~np.isnan(offs)
med = np.nanmedian(offs)
good &= np.abs(offs - med) < 14                              # stray bare ground is not the lane
idx = np.arange(len(offs))
offs = np.interp(idx, idx[good], offs[good])
sm = ndimage.uniform_filter1d(ndimage.median_filter(offs, size=7, mode="nearest"), size=9, mode="nearest")
sm[0], sm[-1] = offs[0], offs[-1]
_lp = [(x + n[0] * o, y + n[1] * o) for (x, y), n, o in zip(pts_, nrm, sm)]
# The lane starts exactly on the middle of the surveyed road's end and leaves it on the road's own heading: the
# sections nearest the join are dropped so the two meet as one continuous road.
if west.project(Point(*road_end)) <= west.project(south_start):
    _lp = [tuple(road_end)] + [q for q in _lp if np.hypot(q[0] - road_end[0], q[1] - road_end[1]) > 30]
else:
    _lp = [q for q in _lp if np.hypot(q[0] - road_end[0], q[1] - road_end[1]) > 30] + [tuple(road_end)]
lane = LineString(_lp).simplify(0.8)

def rnd(g):
    return [[round(x, 1), round(y, 1)] for x, y in g.coords]
out = {"note": "Approximate. The lane is located from the aerial trace; the drives are the architect's sketch lines on the fencing plan.",
       "roads": [{"id": "south-lane", "source": "aerial trace", "width_ft": round(lane_w), "length_ft": round(lane.length * unit_ft), "map": rnd(lane)}]
                + [{"id": i, "source": "fencing plan sketch layer", "width_ft": 12, "length_ft": round(g.length * unit_ft), "map": rnd(g.simplify(0.5))}
                   for i, g in zip(("house-and-long-barn-drive", "south-building-drive"), sketch)]}
json.dump(out, open(os.path.join(OUT, "data", "south-roads.json"), "w"), indent=1)
print("lane: found on", int(good.sum()), "of", len(good), "sections | offset from property line ft: median", round(med * unit_ft), "| width ft", round(lane_w))
print([(r["id"], r["length_ft"], len(r["map"])) for r in out["roads"]])
