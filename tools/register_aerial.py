"""Re-register the County aerial against the surveyed property lines on the fencing plan.

The property lines on "Revised fencing plan with PL.pdf" are the source of truth for alignment. The aerial
carries the County's parcel lines in yellow. This fits the aerial to the plan by matching the plan's property
lines (chained by tools/build_fences.py, in map coordinates) to those yellow pixels: ICP on a similarity
transform, starting from the earlier survey-based registration.
Writes "map_to_aerial_pl" into tools/registration.json; tools/siteframe.py prefers it when present.

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

pts = []
for r in F["property_lines"]:
    ln = LineString(r["map"])
    pts += [ln.interpolate(d).coords[0] for d in np.arange(0, ln.length, 2.0)]
A = np.array(pts)
a = A[:, 0] + 1j * A[:, 1]

im = np.asarray(Image.open(sf.AERIAL).convert("RGB")).astype(int)
r_, g_, b_ = im[..., 0], im[..., 1], im[..., 2]
ys, xs = np.nonzero((r_ > 200) & (g_ > 150) & (b_ < 110) & (r_ - b_ > 110))
Y = np.c_[xs, ys].astype(float)
tree = cKDTree(Y)

# start: the survey-based registration, map -> aerial px
cz = lambda v: complex(*v)
M_SA, T_SA = cz(reg["survey_to_aerial"]["m"]), cz(reg["survey_to_aerial"]["t"])
M_SF, T_SF = cz(reg["survey_to_fence"]["m"]), cz(reg["survey_to_fence"]["t"])
M_SP, T_SP = sf.M_FP * M_SF, sf.M_FP * T_SF + sf.T_FP
m0 = M_SA / M_SP
t0 = T_SA - m0 * T_SP

def resid(m, t):
    z = m * a + t
    d, _ = tree.query(np.c_[z.real, z.imag])
    return d

def lsq(x, y):
    xm, ym = x.mean(), y.mean()
    m = (np.conj(x - xm) @ (y - ym)) / (np.conj(x - xm) @ (x - xm))
    return m, ym - m * xm

m, t = m0, t0
for it in range(80):
    z = m * a + t
    d, i = tree.query(np.c_[z.real, z.imag])
    k = d <= max(2.0, np.quantile(d, 0.7))
    m, t = lsq(a[k], Y[i[k], 0] + 1j * Y[i[k], 1])
d0, d1 = resid(m0, t0), resid(m, t)
px_ft = sf.FT_PER_PT / abs(sf.M_FP) / abs(m)          # feet per aerial pixel
# how far the aerial moves on the map, at three places
inv = lambda mm, tt, z: (z - tt) / mm
probe = {"campus": complex(1190, 330), "north-west end": complex(120, 250), "south end": complex(2150, 1450)}
moves = {}
for name, zmap in probe.items():
    zpx = m0 * zmap + t0                                 # the pixel that used to sit here
    moves[name] = round(abs(inv(m, t, zpx) - zmap) * sf.FT_PER_PT / abs(sf.M_FP))
reg["map_to_aerial_pl"] = {"m": [m.real, m.imag], "t": [t.real, t.imag],
                           "median_residual_px": float(np.median(d1)), "median_residual_ft": float(np.median(d1) * px_ft),
                           "before_median_residual_ft": float(np.median(d0) * px_ft), "aerial_shift_ft": moves,
                           "scale_change_pct": float((abs(m) / abs(m0) - 1) * 100), "rotation_change_deg": float(np.degrees(np.angle(m / m0)))}
json.dump(reg, open(reg_path, "w"), indent=2)
print(json.dumps(reg["map_to_aerial_pl"], indent=1))
