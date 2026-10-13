"""Re-register the County aerial against the surveyed property lines on the fencing plan.

The property lines on "Revised fencing plan with PL.pdf" are the source of truth for alignment. The aerial
carries the County's parcel lines in yellow. This fits the aerial to the plan with an affine transform (it can
stretch the two directions differently, which a scale-and-rotate fit cannot), using two references:
  west   the curved property line along Cowpen Slough, matched to the nearest yellow parcel line;
  east   the long straight property line. The aerial shows two parallel yellow lines there, one on each side
         of the road; the plan's line is matched to the one on the site side only.
The short and interior lines are left out of the fit and reported as a check.
Writes "map_to_aerial_affine" into tools/registration.json; tools/siteframe.py prefers it when present.

Run:  python tools/build_fences.py && python tools/register_aerial.py   (needs numpy, scipy, pillow, shapely)
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree
from shapely.geometry import LineString

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import siteframe as sf

reg_path = os.path.join(HERE, "registration.json")
reg = json.load(open(reg_path))
F = json.load(open(os.path.join(sf.OUT, "data", "fences.json")))
unit_ft = sf.FT_PER_PT / abs(sf.M_FP)

def sample(ln, step=2.0):
    return np.array([ln.interpolate(d).coords[0] for d in np.arange(0, ln.length, step)])

runs = {r["id"]: LineString(r["map"]) for r in F["property_lines"]}
west_ids = [k for k, r in zip(runs, F["property_lines"]) if len(r["map"]) > 8]                 # curved: follows the slough
east_id = max((k for k in runs if k not in west_ids), key=lambda k: runs[k].length)             # the long straight line
W = np.vstack([sample(runs[k]) for k in west_ids])
Epts = sample(runs[east_id])
site_c = W.mean(0)

im = np.asarray(Image.open(sf.AERIAL).convert("RGB")).astype(int)
r_, g_, b_ = im[..., 0], im[..., 1], im[..., 2]
ys, xs = np.nonzero((r_ > 200) & (g_ > 150) & (b_ < 110) & (r_ - b_ > 110))
Y = np.c_[xs, ys].astype(float)
tree = cKDTree(Y)

# start from the survey-based similarity, written as an affine map -> aerial px:  p = [x, y, 1] @ C
cz = lambda v: complex(*v)
M_SA, T_SA = cz(reg["survey_to_aerial"]["m"]), cz(reg["survey_to_aerial"]["t"])
M_SF, T_SF = cz(reg["survey_to_fence"]["m"]), cz(reg["survey_to_fence"]["t"])
M_SP, T_SP = sf.M_FP * M_SF, sf.M_FP * T_SF + sf.T_FP
m0 = M_SA / M_SP
t0 = T_SA - m0 * T_SP
C0 = np.array([[m0.real, m0.imag], [-m0.imag, m0.real], [t0.real, t0.imag]])
H = lambda P: np.c_[P, np.ones(len(P))]

def east_targets(C):
    """For each point of the east line: the nearest point on the site-side yellow line, in aerial px."""
    Q = H(Epts) @ C
    d = Q[-1] - Q[0]; d /= np.linalg.norm(d)
    n = np.array([-d[1], d[0]])
    if ((H(site_c[None]) @ C)[0] - Q[len(Q) // 2]) @ n < 0:
        n = -n                                             # n points toward the site
    idx = tree.query_ball_point(Q[::6], 45)
    cand = Y[np.unique(np.concatenate([np.array(i, int) for i in idx if len(i)]))]
    off = (cand - Q[0]) @ n
    hist, edges = np.histogram(off, bins=np.arange(-45, 46, 2))
    peaks = [i for i in range(1, len(hist) - 1) if hist[i] >= hist[i - 1] and hist[i] >= hist[i + 1] and hist[i] > 0.25 * hist.max()]
    centre = max(edges[i] + 1 for i in peaks)             # the peak furthest toward the site
    line_px = cand[np.abs(off - centre) < 4]
    # straight-line fit through those pixels, then drop each plan point onto it
    c0 = line_px.mean(0)
    _, _, vt = np.linalg.svd(line_px - c0)
    v = vt[0]
    return c0 + np.outer((Q - c0) @ v, v), len(peaks)

C = C0.copy()
for it in range(60):
    Qw = H(W) @ C
    dw, iw = tree.query(Qw)
    kw = dw <= max(2.0, np.quantile(dw, 0.8))
    Te, n_peaks = east_targets(C)
    src = np.vstack([W[kw], Epts])
    dst = np.vstack([Y[iw[kw]], Te])
    C, *_ = np.linalg.lstsq(H(src), dst, rcond=None)

px_ft = unit_ft / np.sqrt(abs(np.linalg.det(C[:2])))
def resid_ft(P, C_):
    return tree.query(H(P) @ C_)[0] * px_ft
Te, _ = east_targets(C)
checks = {k: round(float(np.median(resid_ft(sample(runs[k]), C))), 1) for k in runs}
checks[east_id] = round(float(np.median(np.linalg.norm(H(Epts) @ C - Te, axis=1)) * px_ft), 1)
Ci = np.linalg.inv(np.vstack([C.T, [0, 0, 1]]))            # aerial px -> map, as a 3x3 acting on column vectors
C0i = np.linalg.inv(np.vstack([C0.T, [0, 0, 1]]))
probe = {"campus": (1190, 330), "north-west end": (120, 250), "south end": (2150, 1450), "east line, south end": (2300, 190)}
moves = {}
for name, zmap in probe.items():
    px = np.array([*zmap, 1.0]) @ C0                         # the pixel that sat here under the first registration
    new = Ci @ np.array([px[0], px[1], 1.0])
    moves[name] = round(float(np.hypot(new[0] - zmap[0], new[1] - zmap[1]) * unit_ft))
sv = np.linalg.svd(C[:2], compute_uv=False)
reg["map_to_aerial_affine"] = {
    "C": C.tolist(), "aerial_to_map": Ci[:2].tolist(),
    "fit_lines": {"west": west_ids, "east": east_id}, "east_yellow_lines_found": int(n_peaks),
    "median_residual_ft_by_line": checks, "aerial_shift_ft_vs_first_registration": moves,
    "stretch_ratio": float(sv[0] / sv[1]), "ft_per_aerial_px": float(px_ft)}
reg.pop("map_to_aerial_pl", None)
json.dump(reg, open(reg_path, "w"), indent=2)
print(json.dumps({k: v for k, v in reg["map_to_aerial_affine"].items() if k not in ("C", "aerial_to_map")}, indent=1))
