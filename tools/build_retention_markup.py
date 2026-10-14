"""Retention ponds from the architect's markup of the water slide (2026-10-14).

Source: source/site-edits/retention-markup-2026-10-14.webp, a screenshot of the water-site slide's map with ponds
drawn in red. The screenshot shows the map frame unrotated, so it is placed by a scale-and-shift fit on labels
visible in it (barnyard labels, the retention pond's label, the old wildcard label). The red outlines are read by
colour and filled; one pond's open side is closed by hand. The X through the old wildcard zone is dropped.
Each pond is split at the parcel line (pl-04): the part inside is a new site retention pond, the part outside (on
Solid Waste land, like the bonus pasture) is bonus retention.
Writes drawings/data/retention-markup.json (presentation frame). Run after build_site_map.py has run once.

Run:  python tools/build_retention_markup.py
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from shapely.geometry import Polygon
from shapely.ops import unary_union
from skimage import measure

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from siteframe import ROOT, OUT, FT_PER_PT, M_FP, snapped_boundary

SRC = os.path.join(ROOT, "source", "site-edits", "retention-markup-2026-10-14.webp")
# screen px <- map: control points (map x, y) -> (screen x, y)
CP = [((1231, 483), (535, 392)), ((1673, 777), (1470, 1010)), ((1143.8, 434.4), (351, 287)), ((1133.7, 466.4), (329, 353)),
      ((1068.3, 441.4), (191, 300)), ((1162.0, 387.7), (389, 188)), ((1065.1, 366.4), (184, 143)), ((1114.2, 349.4), (288, 106))]
mp = np.array([c[0] for c in CP]); sc = np.array([c[1] for c in CP])
mm, sm = mp.mean(0), sc.mean(0)
k = float(np.sum((sc - sm) * (mp - mm)) / np.sum((mp - mm) ** 2))           # scale, no rotation
res = np.abs((mp - mm) * k + sm - sc).max()
to_map = lambda x, y: ((x - sm[0]) / k + mm[0], (y - sm[1]) / k + mm[1])
unit_ft = FT_PER_PT / abs(M_FP)
acres = lambda g: round(g.area * unit_ft ** 2 / 43560, 1)

a = np.asarray(Image.open(SRC).convert("RGB")).astype(int)
red = (a[..., 0] > 200) & (a[..., 1] < 90) & (a[..., 2] < 70)
m = Image.fromarray((red * 255).astype(np.uint8)); ImageDraw.Draw(m).line([(626, 355), (640, 410)], fill=255, width=5)
red = ndimage.binary_fill_holes(ndimage.binary_closing(np.asarray(m) > 0, iterations=4))
lab, n = ndimage.label(red)
ponds = []
for i in range(1, n + 1):
    mask = lab == i
    ys, xs = np.where(mask)
    if mask.sum() < 8000 or xs.min() > 1300:                             # strokes of the X
        continue
    c = max(measure.find_contours(np.pad(mask, 1).astype(float), 0.5), key=len)
    ponds.append(Polygon([to_map(x - 1, y - 1) for y, x in c]).buffer(0).simplify(0.4))
# the parcel line between the County site and the Solid Waste land beyond it (fences.json pl-04, the dash-dot line
# on the slide), carried on past its ends: west of it is the site, east of it the bonus land
_pl = [r["map"] for r in json.load(open(os.path.join(OUT, "data", "fences.json")))["property_lines"] if r["id"] == "pl-04"][0]
(_x0, _y0), (_x1, _y1) = _pl[0], _pl[-1]
_dx, _dy = _x1 - _x0, _y1 - _y0
site = Polygon([(_x0 - _dx * 5, _y0 - _dy * 5), (_x1 + _dx * 5, _y1 + _dy * 5), (-5000, _y1 + _dy * 5), (-5000, _y0 - _dy * 5)])
# Clean-up (architect, 2026-10-14): the pond that meets the proposed retention pond becomes one shape with it
# (no line between them), and where a pond crosses the parcel line its edges run straight across: each pond is
# filled out with the convex hull of its part within 60' of the line, then the whole is split at the line.
_ret = [Polygon(pd["pts"]).buffer(0) for pd in json.load(open(os.path.join(OUT, "data", "site-edits.json")))["ponds"] if pd["kind"] != "existing"]
_line = site.exterior
W60 = 60 / unit_ft
groups = []
for p in ponds:
    if _ret and p.distance(_ret[0]) < 3:
        p = unary_union([p, _ret[0]]).buffer(1.5).buffer(-1.5)
    near = p.intersection(_line.buffer(W60))
    if not near.is_empty:
        p = unary_union([p, near.convex_hull]).buffer(0)
    groups.append(p)
flat = lambda gs: [g for x in gs for g in getattr(x, "geoms", [x]) if g.geom_type == "Polygon" and g.area * unit_ft ** 2 > 2000]
site_p = flat([g.intersection(site) for g in groups])
bonus_p = flat([g.difference(site) for g in groups])
site_p = [g.buffer(-2).buffer(2).simplify(0.4) for g in site_p]
bonus_p = [g.buffer(-2).buffer(2).simplify(0.4) for g in bonus_p]
site_p.sort(key=lambda g: -g.area); bonus_p.sort(key=lambda g: g.centroid.x)
rnd = lambda p: [[round(x, 1), round(y, 1)] for x, y in p.exterior.coords]
out = {"source": os.path.relpath(SRC, ROOT), "fit_scale_px_per_unit": round(k, 4), "fit_max_residual_px": round(float(res), 1),
       "site_ponds": [rnd(p) for p in site_p], "site_ponds_acres": [acres(p) for p in site_p], "site_acres": round(sum(acres(p) for p in site_p), 1),
       "bonus_ponds": [rnd(p) for p in bonus_p], "bonus_ponds_acres": [acres(p) for p in bonus_p], "bonus_acres": round(sum(acres(p) for p in bonus_p), 1),
       "note": "site_ponds[0] is the proposed retention pond, merged with the markup's pond beside it; it replaces the drawn pond on the map."}
json.dump(out, open(os.path.join(OUT, "data", "retention-markup.json"), "w"))
print("fit: scale", round(k, 3), "max residual px", round(float(res), 1), "| ponds", len(ponds), "| site parts", [acres(p) for p in site_p], "| bonus parts", [acres(p) for p in bonus_p])
