"""Turn the proposed fence lines on the fencing plan into continuous polylines.

On "Clark Farm Proposed Fencing Plan.pdf" each fence is plotted as a row of separate dashes (about 18 units
long, 15 apart, with an X between them). This script chains the dashes back into one polyline per fence run:
  1. every stroke on the fence layers becomes a segment (curved dashes by their chord; the short X strokes are dropped);
  2. two segments are joined end to end when the gap is small and they point the same way;
  3. each chain is simplified to its corners, and loose chain ends are snapped onto the fence they run into.
Writes drawings/data/fences.json: polylines in the fencing sheet's own coordinates (the source of truth) and
in the map's presentation frame, with lengths in feet.

Run:  python tools/build_fences.py   (needs pymupdf, numpy, scipy, shapely)
"""
import json, math, os, sys
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import LineString, Point
from shapely.ops import linemerge, unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from siteframe import ROOT, OUT, FENCE, cadpdf, M_FP, T_FP, FT_PER_PT, ARROW_BOXES, WATER_BOXES, inside

MAX_GAP, MAX_TURN, SNAP = 24.0, 14.0, 22.0        # sheet units, degrees, sheet units

segs = []
for L, ds in cadpdf.export(FENCE, ["FENCE", "(none)", "P-BELOW-LIGHT"]).items():
    for d in ds:
        r = d["rect"]
        if any(inside(r, b) for b in ARROW_BOXES):                         # the sheet's SITE / BONUS arrow graphic
            continue
        # one stroke = one drawn path. Curved dashes are plotted as several tiny pieces, so work on the whole path.
        pts = []
        for it in d["items"]:
            if it[0] not in ("l", "c"):
                continue
            e_ = it[2] if it[0] == "l" else it[4]
            if not pts:
                pts.append((it[1].x, it[1].y))
            pts.append((e_.x, e_.y))
        if len(pts) < 2:
            continue
        path = LineString(pts)
        dash = 9 <= path.length <= 26
        if L != "FENCE" and not dash and any(inside(r, b) for b in WATER_BOXES):
            continue                                                       # pond and retention outlines
        if L == "P-BELOW-LIGHT" and not dash:
            continue                                                       # on this layer only dash-sized strokes are fence
        if L == "(none)" and not dash and path.length > 60:
            continue                                                       # long solid polylines here are drives
        if dash:
            segs.append((np.array(pts[0]), np.array(pts[-1])))            # a dash: its chord
        elif path.length > 26:
            q = list(path.simplify(0.8).coords)                           # a drawn fence polyline: keep its corners
            segs += [(np.array(a), np.array(b)) for a, b in zip(q, q[1:]) if np.hypot(b[0] - a[0], b[1] - a[1]) >= 4]
print("fence strokes kept:", len(segs))

# endpoints: index 2i = start of segment i, 2i+1 = end. Outward direction at each endpoint.
P = np.array([p for s in segs for p in s])
D = np.array([v for a, b in segs for v in ((a - b) / np.linalg.norm(a - b), (b - a) / np.linalg.norm(b - a))])
tree = cKDTree(P)
link = {}
cands = []
for i in range(len(P)):
    for j in tree.query_ball_point(P[i], MAX_GAP):
        if j // 2 == i // 2 or j < i:
            continue
        w = P[j] - P[i]
        dist = np.linalg.norm(w)
        if dist < 1e-6:
            cands.append((0.0, i, j)); continue
        w /= dist
        turn = max(math.degrees(math.acos(np.clip(D[i] @ w, -1, 1))), math.degrees(math.acos(np.clip(-D[j] @ w, -1, 1))))
        bend = math.degrees(math.acos(np.clip(-(D[i] @ D[j]), -1, 1)))      # change of direction across the joint
        if turn <= MAX_TURN or (dist < 3 and bend < 100):                    # collinear dash gap, or a drawn corner
            cands.append((dist + turn * 0.3, i, j))
for _, i, j in sorted(cands):                                               # closest, straightest joins first
    if i not in link and j not in link:
        link[i] = j; link[j] = i

seen, chains = set(), []
for s0 in range(len(segs)):
    if s0 in seen:
        continue
    # walk back to the start of the chain
    e = 2 * s0
    guard = 0
    while e in link and guard < len(segs):
        nxt = link[e] ^ 1                     # other end of the neighbouring segment
        if nxt // 2 == s0:
            break
        e = nxt; guard += 1
    start = e
    pts = [P[start]]
    cur = start ^ 1
    seen.add(start // 2)
    pts.append(P[cur])
    while cur in link and link[cur] // 2 not in seen:
        nb = link[cur]
        seen.add(nb // 2)
        if np.linalg.norm(P[nb] - P[cur]) > 1e-6:
            pts.append(P[nb])
        cur = nb ^ 1
        pts.append(P[cur])
    chains.append(LineString(pts).simplify(1.2))

chains = [c for c in chains if c.length > 30]
# snap loose ends onto the fence they run into (T junctions), then merge runs that now share an end point
def snap_end(c, others):
    pts = list(c.coords)
    for k in (0, -1):
        end = Point(pts[k])
        best = None
        for o in others:
            if o is c:
                continue
            dd = o.distance(end)
            if dd < SNAP and (best is None or dd < best[0]):
                best = (dd, o)
        if best and best[0] > 0.05:
            q = best[1].interpolate(best[1].project(end))
            # prefer extending along the run's own direction if that hits the other fence close by
            a, b = (np.array(pts[1]), np.array(pts[0])) if k == 0 else (np.array(pts[-2]), np.array(pts[-1]))
            u = (b - a) / (np.linalg.norm(b - a) or 1)
            ray = LineString([b, b + u * SNAP * 1.5])
            hit = ray.intersection(best[1])
            if not hit.is_empty:
                hp = hit if hit.geom_type == "Point" else list(getattr(hit, "geoms", [hit]))[0]
                if hp.geom_type == "Point":
                    q = hp
            pts[k] = (q.x, q.y)
    return LineString(pts)
chains = [snap_end(c, chains) for c in chains]
merged = linemerge(unary_union(chains))
runs = list(getattr(merged, "geoms", [merged]))
runs = [r.simplify(1.0) for r in runs if r.length > 30]

def to_p(c):
    z = M_FP * complex(c[0], c[1]) + T_FP
    return [round(z.real, 2), round(z.imag, 2)]
out = {"source": os.path.relpath(FENCE, ROOT), "ft_per_sheet_unit": FT_PER_PT, "runs": []}
for k, r in enumerate(sorted(runs, key=lambda r: -r.length)):
    out["runs"].append({"id": f"fence-{k + 1:02d}", "length_ft": round(r.length * FT_PER_PT),
                        "sheet": [[round(x, 2), round(y, 2)] for x, y in r.coords], "map": [to_p(c) for c in r.coords]})
out["total_ft"] = sum(r["length_ft"] for r in out["runs"])
json.dump(out, open(os.path.join(OUT, "data", "fences.json"), "w"), indent=1)
print("runs:", len(out["runs"]), "| total length ft:", out["total_ft"], "| vertices:", sum(len(r["sheet"]) for r in out["runs"]))
print("longest:", [(r["id"], r["length_ft"], len(r["sheet"])) for r in out["runs"][:6]], "shortest:", [r["length_ft"] for r in out["runs"][-6:]])
