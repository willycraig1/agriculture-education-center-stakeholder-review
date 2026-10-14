"""Civil engineer's stormwater sketches (2026-10-14), placed on the map.

  source/civil/2026-10-14 retention expansion sketch.png   a screenshot of study plan A0.1 with the expanded
        stormwater retention coloured cyan. Placed by SIFT feature matching against the study plan PDF (similarity
        fit, about 400 matched features): image px -> sheet pt = 2.375 * px + (449.7, 2.3), no rotation. The cyan
        is read by colour, gaps where linework crosses it are closed, and holes filled.
  source/civil/2026-10-14 floodplain compensation options.webp   an aerial with floodplain compensation Option 1
        and Option 2 outlined in green. Placed by SIFT matching against the County aerial (about 20 inliers, the
        same fit at five trial scales): image px -> aerial px = 1.2858 * px + (737.0, -0.6). Option 2's outline is
        closed and read by colour; Option 1's west side is drawn partly as a red dashed line, so its outline is
        traced by hand from the image (pixel points below).
Writes drawings/data/civil.json (presentation frame, acres).

Run:  python tools/build_civil.py   (needs numpy, scipy, shapely, pillow, scikit-image)
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage
from shapely.geometry import Polygon
from skimage import measure

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from siteframe import ROOT, OUT, M_TP, T_TP, FT_PER_PT, M_FP, reg

CIV = os.path.join(ROOT, "source", "civil")
RET = os.path.join(CIV, "2026-10-14 retention expansion sketch.png")
OPT = os.path.join(CIV, "2026-10-14 floodplain compensation options.webp")
RET_FIT = (2.375, 449.7, 2.3)                    # image px -> study sheet pt
OPT_FIT = (1.2858, 737.0, -0.6)                  # image px -> County aerial px
unit_ft = FT_PER_PT / abs(M_FP)
acres = lambda g: round(g.area * unit_ft ** 2 / 43560, 1)

def polys(mask, to_map, min_px=200):
    out = []
    for c in measure.find_contours(np.pad(mask, 1).astype(float), 0.5):
        if len(c) < 20:
            continue
        p = Polygon([to_map(x - 1, y - 1) for y, x in c]).buffer(0)
        if p.area > 0:
            out.append(p)
    return [p for p in out if p.area * 1.0 > 0]

def ret_to_map(x, y):
    s, tx, ty = RET_FIT
    z = M_TP * complex(s * x + tx, s * y + ty) + T_TP
    return (z.real, z.imag)

(a_, c_, e_), (b_, d_, f_) = reg["map_to_aerial_affine"]["aerial_to_map"]
def opt_to_map(x, y):
    s, tx, ty = OPT_FIT
    ax, ay = s * x + tx, s * y + ty
    return (a_ * ax + c_ * ay + e_, b_ * ax + d_ * ay + f_)

# ---- expanded retention: cyan
a = np.asarray(Image.open(RET).convert("RGB")).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
cyan = (g > 180) & (b > 180) & (g - r > 40) & (b - r > 40)
cyan = ndimage.binary_fill_holes(ndimage.binary_closing(cyan, iterations=2))
lab, n = ndimage.label(cyan)
keep = np.isin(lab, [i for i in range(1, n + 1) if (lab == i).sum() > 2000])
ret = [p.simplify(0.6) for p in polys(keep, ret_to_map)]
ret = sorted(ret, key=lambda p: -p.area)[:2]

# ---- compensation options
a = np.asarray(Image.open(OPT).convert("RGB")).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
green = ndimage.binary_fill_holes(ndimage.binary_closing((g > 150) & (g - r > 50) & (g - b > 50), iterations=3))
lab, n = ndimage.label(green)
big = max(range(1, n + 1), key=lambda i: (lab == i).sum())
opt2 = max(polys(lab == big, opt_to_map), key=lambda p: p.area).simplify(0.6)
OPT1_PX = [(312.5, 403.8), (335, 402.5), (340, 407.5), (363.8, 407.5), (355, 452.5), (356.3, 500), (363.8, 530), (387.5, 577.5), (390, 602.5),
           (378.8, 611.3), (352.5, 572.5), (337.5, 568.8), (331.3, 566.3), (301.3, 516.3), (297.5, 446.3), (305, 436.3), (305, 411.3)]
opt1 = Polygon([opt_to_map(x, y) for x, y in OPT1_PX]).buffer(0)

rnd = lambda p: [[round(x, 1), round(y, 1)] for x, y in p.exterior.coords]
out = {"source": "civil engineer, 2026-10-14 (see source/civil)",
       "retention_expansion": [rnd(p) for p in ret], "retention_expansion_acres": round(sum(acres(p) for p in ret), 1),
       "option1": rnd(opt1), "option1_acres": acres(opt1), "option2": rnd(opt2), "option2_acres": acres(opt2),
       "fits": {"retention_px_to_sheet": RET_FIT, "options_px_to_aerial": OPT_FIT}}
json.dump(out, open(os.path.join(OUT, "data", "civil.json"), "w"))
print("retention expansion parts", len(ret), "acres", out["retention_expansion_acres"], "| option 1 ac", out["option1_acres"], "| option 2 ac", out["option2_acres"])
