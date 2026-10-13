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

def chain(segs, max_gap, max_turn, snap, min_len=30, protect=None, protect_r=8.0, snap_protect=None):
    """protect: points (gate leaf ends). Fence ends within protect_r of one are left exactly as drawn: they are the
    deliberately offset ends that form a pinwheel, and must not be joined or snapped to their neighbours."""
    ptree = cKDTree(protect) if protect is not None and len(protect) else None
    guarded = lambda q: ptree is not None and ptree.query(q)[0] < protect_r

    # endpoints: index 2i = start of segment i, 2i+1 = end. Outward direction at each endpoint.
    P = np.array([p for s in segs for p in s])
    D = np.array([v for a, b in segs for v in ((a - b) / np.linalg.norm(a - b), (b - a) / np.linalg.norm(b - a))])
    tree = cKDTree(P)
    link = {}
    cands = []
    for i in range(len(P)):
        for j in tree.query_ball_point(P[i], max_gap):
            if j // 2 == i // 2 or j < i:
                continue
            w = P[j] - P[i]
            dist = np.linalg.norm(w)
            if dist < 1e-6:
                cands.append((0.0, i, j)); continue
            if guarded(P[i]) and guarded(P[j]):
                # at a pinwheel only pieces of the same fence may join (its stub beyond the gate hinge);
                # never one fence to its neighbour
                w0 = (P[j] - P[i]) / dist
                if max(math.degrees(math.acos(np.clip(D[i] @ w0, -1, 1))), math.degrees(math.acos(np.clip(-D[j] @ w0, -1, 1)))) > 6:
                    continue
            w /= dist
            turn = max(math.degrees(math.acos(np.clip(D[i] @ w, -1, 1))), math.degrees(math.acos(np.clip(-D[j] @ w, -1, 1))))
            bend = math.degrees(math.acos(np.clip(-(D[i] @ D[j]), -1, 1)))      # change of direction across the joint
            if turn <= max_turn or (dist < 3 and bend < 100):                    # collinear dash gap, or a drawn corner
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

    chains = [c for c in chains if c.length > min_len]
    # snap loose ends onto the fence they run into (T junctions), then merge runs that now share an end point
    stree = cKDTree(snap_protect) if snap_protect is not None and len(snap_protect) else None
    def snap_end(c, others):
        """Close the gap where a dashed run stops just short of the fence it meets. The run is extended along its
        own heading (a vertex is added; nothing already drawn is moved). Ends at a gate are left open: the gap
        is the gate."""
        pts = list(c.coords)
        for k in (0, -1):
            end = Point(pts[k])
            if guarded(pts[k]) or (stree is not None and stree.query(pts[k])[0] < 14.0):
                continue
            a, b = (np.array(pts[1]), np.array(pts[0])) if k == 0 else (np.array(pts[-2]), np.array(pts[-1]))
            u = (b - a) / (np.linalg.norm(b - a) or 1)
            ray = LineString([b, b + u * snap])
            best = None
            for o in others:
                if o is c or o.distance(end) < 0.05:
                    continue
                hit = ray.intersection(o)
                if hit.is_empty:
                    continue
                hp = hit if hit.geom_type == "Point" else list(getattr(hit, "geoms", [hit]))[0]
                if hp.geom_type == "Point" and (best is None or hp.distance(end) < best.distance(end)):
                    best = hp
            if best is not None:
                if k == 0:
                    pts.insert(0, (best.x, best.y))
                else:
                    pts.append((best.x, best.y))
        return LineString(pts)
    chains = [snap_end(c, chains) for c in chains]
    merged = linemerge(unary_union(chains))
    runs = list(getattr(merged, "geoms", [merged]))
    runs = [r.simplify(1.0) for r in runs if r.length > min_len]

    return runs

segs = []
solids = []
for L, ds in cadpdf.export(FENCE, ["FENCE", "(none)"]).items():      # P-BELOW-LIGHT is the circulation sketch and pond outlines: not fence
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
        dash = (3 if L == "FENCE" else 9) <= path.length <= 26     # short end pieces at gates are real fence
        if L != "FENCE" and not dash and any(inside(r, b) for b in WATER_BOXES):
            continue                                                       # pond and retention outlines
        if L == "P-BELOW-LIGHT" and not dash:
            continue                                                       # on this layer only dash-sized strokes are fence
        if L == "(none)" and not dash and path.length > 60:
            solids.append(path)                                            # a drive, or a solid stretch of fence: decided below
            continue
        if dash:
            segs.append((np.array(pts[0]), np.array(pts[-1])))            # a dash: its chord
        elif path.length > 26:
            q = list(path.simplify(0.8).coords)                           # a drawn fence polyline: keep its corners
            segs += [(np.array(a), np.array(b)) for a, b in zip(q, q[1:]) if np.hypot(b[0] - a[0], b[1] - a[1]) >= 4]
# A long solid polyline is part of the fence when both of its ends meet fence strokes (it bridges two dashed
# runs); otherwise it is a drive and is left out.
_ends = cKDTree(np.array([p for sg in segs for p in sg]))
n_solid = 0
for path in solids:
    q = list(path.simplify(0.8).coords)
    if all(_ends.query(e)[0] < MAX_GAP for e in (q[0], q[-1])):
        segs += [(np.array(a), np.array(b)) for a, b in zip(q, q[1:]) if np.hypot(b[0] - a[0], b[1] - a[1]) >= 2]
        n_solid += 1
print("fence strokes kept:", len(segs), "| solid stretches taken as fence:", n_solid, "of", len(solids))
# Gates (layer A-DOOR): a straight leaf with a swing arc. Where four fences meet they are deliberately offset
# into a pinwheel, each with a gate, around a shared space for feed and water.
gate_leaves, gate_arcs = [], []
for d in cadpdf.export(FENCE, ["A-DOOR"]).get("A-DOOR", []):
    for it in d["items"]:
        if it[0] == "l":
            gate_leaves.append([[it[1].x, it[1].y], [it[2].x, it[2].y]])
        elif it[0] == "c":
            gate_arcs.append([[q.x, q.y] for q in it[1:5]])
gate_leaves = [g for g in gate_leaves if np.hypot(g[1][0] - g[0][0], g[1][1] - g[0][1]) > 2]
GP = np.array([q for g in gate_leaves for q in g])
GA = np.array([q for a_ in gate_arcs for q in (a_[0], a_[3])] + [q for g in gate_leaves for q in g])      # every gate end point
runs = chain(segs, MAX_GAP, MAX_TURN, SNAP, protect=GP, snap_protect=GA)

# ---- property lines (layer SECTION LINE): short dashes with dots between them
pl_segs = []
for d in cadpdf.export(FENCE, ["SECTION LINE"]).get("SECTION LINE", []):
    pts = []
    for it in d["items"]:
        if it[0] in ("l", "c"):
            e_ = it[2] if it[0] == "l" else it[4]
            if not pts:
                pts.append((it[1].x, it[1].y))
            pts.append((e_.x, e_.y))
    if len(pts) >= 2 and LineString(pts).length >= 4:                  # the dots have no length
        pl_segs.append((np.array(pts[0]), np.array(pts[-1])))
print("property line dashes kept:", len(pl_segs))
pl_runs = chain(pl_segs, 16.0, 16.0, 14.0, min_len=60)

def to_p(c):
    z = M_FP * complex(c[0], c[1]) + T_FP
    return [round(z.real, 2), round(z.imag, 2)]
out = {"source": os.path.relpath(FENCE, ROOT), "ft_per_sheet_unit": FT_PER_PT, "runs": []}
for k, r in enumerate(sorted(runs, key=lambda r: -r.length)):
    out["runs"].append({"id": f"fence-{k + 1:02d}", "length_ft": round(r.length * FT_PER_PT),
                        "sheet": [[round(x, 2), round(y, 2)] for x, y in r.coords], "map": [to_p(c) for c in r.coords]})
out["total_ft"] = sum(r["length_ft"] for r in out["runs"])
def _cluster(pts, r):
    pairs = cKDTree(pts).query_pairs(r); par = list(range(len(pts)))
    def f(i):
        while par[i] != i:
            par[i] = par[par[i]]; i = par[i]
        return i
    for i, j in pairs:
        par[f(i)] = f(j)
    g = {}
    for i in range(len(pts)):
        g.setdefault(f(i), []).append(i)
    return list(g.values())
_mid = np.array([[(g[0][0] + g[1][0]) / 2, (g[0][1] + g[1][1]) / 2] for g in gate_leaves])
out["gates"] = [{"length_ft": round(float(np.hypot(g[1][0] - g[0][0], g[1][1] - g[0][1]) * FT_PER_PT), 1),
                 "sheet": [[round(v, 2) for v in q] for q in g], "map": [to_p(q) for q in g]} for g in gate_leaves]
out["gate_arcs"] = [{"sheet": [[round(v, 2) for v in q] for q in a], "map": [to_p(q) for q in a]} for a in gate_arcs]
out["pinwheels"] = [{"gates": len(c), "map": to_p(_mid[c].mean(0))} for c in _cluster(_mid, 30) if len(c) >= 4]
# Roads: the survey's edge-of-pavement lines are plotted in short pieces; chain them the same way so each
# road edge is one continuous polyline.
from siteframe import SURVEY, M_SP, T_SP
rd = []
for d in cadpdf.export(SURVEY, ["EDGE OF PAVEMENT"]).get("EDGE OF PAVEMENT", []):
    pts = []
    for it in d["items"]:
        if it[0] in ("l", "c"):
            e_ = it[2] if it[0] == "l" else it[4]
            if not pts:
                z = M_SP * complex(it[1].x, it[1].y) + T_SP; pts.append((z.real, z.imag))
            z = M_SP * complex(e_.x, e_.y) + T_SP; pts.append((z.real, z.imag))
    rd += [(np.array(a), np.array(b)) for a, b in zip(pts, pts[1:]) if np.hypot(b[0] - a[0], b[1] - a[1]) > 0.05]
road_runs = chain(rd, 16.0, 9.0, 0.0, min_len=12)     # bridge dash gaps only where the heading holds
out["roads"] = [{"length_ft": round(r.length * FT_PER_PT), "map": [[round(x, 2), round(y, 2)] for x, y in r.coords]} for r in sorted(road_runs, key=lambda r: -r.length)]
print("road edge pieces:", len(rd), "-> runs:", len(out["roads"]), "| longest ft:", [r["length_ft"] for r in out["roads"][:6]])
out["property_lines"] = [{"id": f"pl-{k + 1:02d}", "length_ft": round(r.length * FT_PER_PT),
                          "sheet": [[round(x, 2), round(y, 2)] for x, y in r.coords], "map": [to_p(c) for c in r.coords]}
                         for k, r in enumerate(sorted(pl_runs, key=lambda r: -r.length))]
json.dump(out, open(os.path.join(OUT, "data", "fences.json"), "w"), indent=1)
print("runs:", len(out["runs"]), "| total length ft:", out["total_ft"], "| vertices:", sum(len(r["sheet"]) for r in out["runs"]))
print("gates:", len(out["gates"]), "| pinwheels:", len(out["pinwheels"]), "| gate lengths ft:", sorted({round(g["length_ft"]) for g in out["gates"]}))
print("property lines:", [(r["id"], r["length_ft"], len(r["sheet"])) for r in out["property_lines"]])
print("longest:", [(r["id"], r["length_ft"], len(r["sheet"])) for r in out["runs"][:6]], "shortest:", [r["length_ft"] for r in out["runs"][-6:]])
