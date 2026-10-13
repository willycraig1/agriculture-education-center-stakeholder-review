"""Derive tree canopy, drives and Cowpen Slough from the architect's vector trace of the aerial.

Source: source/site-edits/aerial-trace-2026-10-13.svg, an Illustrator image trace of the County aerial in ten
flat colours at half the aerial's pixel size. It is placed with the aerial's registration (tools/registration.json),
so it carries the aerial's misfit against the survey: a few feet near the campus, more toward the edges.
Method: render the trace in the map's presentation frame, sort pixels by trace colour, then clean each mask
(close gaps, drop specks) and trace its outline back to simple polygons.
  canopy  the three darkest colours (tree crowns and their shadows), inside the site boundary, ponds removed
  drives  the lightest colour (pavement, shell and bare ground), inside the site, buildings removed, thin runs only
  slough  the dark water band that follows the west property line, within a corridor around that line
Writes drawings/data/aerial-derived.json. Run before tools/build_site_map.py.   (needs pymupdf, numpy, scipy, scikit-image, shapely)
"""
import json, os, re, sys
import numpy as np
import pymupdf
from scipy import ndimage
from skimage import measure
from shapely.geometry import LineString, Polygon, Point
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from siteframe import ROOT, OUT, VIEW, aerial_matrix, FT_PER_PT, M_FP

TRACE = os.path.join(ROOT, "source", "site-edits", "aerial-trace-2026-10-13.svg")
E = json.load(open(os.path.join(OUT, "data", "site-edits.json")))
SC = 2                                   # raster px per map unit
x0, y0, x1, y1 = VIEW
W, H = int((x1 - x0) * SC), int((y1 - y0) * SC)
unit_ft = FT_PER_PT / abs(M_FP)

src = open(TRACE).read()
css = dict(re.findall(r"\.(st\d+)\s*\{\s*fill:\s*(#[0-9a-fA-F]{6})", src))
body = src[src.index("</defs>") + 7:src.rindex("</svg>")]
body = re.sub(r'class="(st\d+)"', lambda m: f'fill="{css[m.group(1)]}"', body)
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}" width="{W}" height="{H}">'
       f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="#ffffff"/><g transform="{aerial_matrix(2)}">{body}</g></svg>')
tmp = os.path.join(OUT, "data", "_trace_tmp.svg")
open(tmp, "w").write(svg)
pix = pymupdf.open(tmp)[0].get_pixmap(matrix=pymupdf.Matrix(1, 1), alpha=False)
os.remove(tmp)
img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3).astype(int)
cols = sorted(css.values(), key=lambda h: sum(int(h[i:i + 2], 16) for i in (1, 3, 5)))      # dark -> light
rgb = np.array([[int(h[i:i + 2], 16) for i in (1, 3, 5)] for h in cols])
cls = np.argmin(((img[:, :, None, :] - rgb[None, None, :, :]) ** 2).sum(-1), axis=2)         # 0 = darkest
yellow = [i for i, h in enumerate(cols) if int(h[1:3], 16) > 200 and int(h[5:7], 16) < 120]  # parcel lines
greys = [i for i in range(len(cols)) if i not in yellow]

def raster(geom):
    from PIL import Image, ImageDraw
    im = Image.new("1", (pix.width, pix.height), 0)
    dr = ImageDraw.Draw(im)
    for g in getattr(geom, "geoms", [geom]):
        if g.geom_type == "Polygon" and not g.is_empty:
            dr.polygon([((px - x0) * SC, (py - y0) * SC) for px, py in g.exterior.coords], fill=1)
    return np.asarray(im, dtype=bool)

def polys(mask, min_area, simplify=1.2):
    out = []
    lab, n = ndimage.label(mask)
    for c in measure.find_contours(np.pad(mask, 1).astype(float), 0.5):
        xy = np.c_[c[:, 1] - 1, c[:, 0] - 1] / SC + [x0, y0]
        if len(xy) >= 4:
            p = Polygon(xy).buffer(0)
            if p.area >= min_area:
                out.append(p)
    g = Polygon()
    for p in sorted(out, key=lambda p: -p.area):      # even-odd: holes come back as their own rings
        g = g.symmetric_difference(p)
    return g.simplify(simplify)

def d_of(g):
    d = ""
    for p in getattr(g, "geoms", [g]):
        if p.geom_type != "Polygon" or p.is_empty:
            continue
        for ring in [p.exterior, *p.interiors]:
            d += "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in ring.coords) + "Z"
    return d

site = Polygon(E["boundary"]).buffer(0)
site_m = raster(site)
ponds = unary_union([Polygon(p["pts"]).buffer(3) for p in E["ponds"] if len(p["pts"]) >= 3])
structs = unary_union([Polygon(s["pts"]).buffer(4) for s in E["structures"] if len(s["pts"]) >= 3])

# ---- slough: dark band along the west property line (the boundary's long curved side)
B = E["boundary"]
seg_len = [np.hypot(B[i + 1][0] - B[i][0], B[i + 1][1] - B[i][1]) for i in range(len(B) - 1)]
i_n = min(range(len(B)), key=lambda i: B[i][0] + B[i][1] * 0.2)          # north-west end of the west side
i_s = max(range(len(B)), key=lambda i: B[i][1])                           # south end
a, b = sorted((i_n, i_s))
chain1, chain2 = B[a:b + 1], B[b:] + B[:a + 1]
west = chain1 if len(chain1) > len(chain2) else chain2                    # the many-vertex side follows the slough
west_line = LineString(west)
corridor = west_line.buffer(34)
dark = np.isin(cls, greys[:2])
m = dark & raster(corridor)
m = ndimage.binary_closing(m, iterations=6)
m = ndimage.binary_opening(m, iterations=1)
lab, n = ndimage.label(m)
if n:
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    m = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s > 0.04 * sizes.max()])
# Redraw it as a clean band: walk the property line, measure where the dark water sits across it and how wide
# it is, smooth both along the line, and draw the smoothed centreline at the typical width.
step = 6.0
n_s = int(west_line.length // step)
offs = np.arange(-34, 34.5, 0.5)
cen, wid, pts_, nrm = [], [], [], []
for k in range(n_s + 1):
    p0, p1 = west_line.interpolate(max(0, k * step - 3)), west_line.interpolate(min(west_line.length, k * step + 3))
    pc = west_line.interpolate(k * step)
    tx, ty = p1.x - p0.x, p1.y - p0.y
    L = np.hypot(tx, ty) or 1
    nx, ny = -ty / L, tx / L
    xs = ((pc.x + offs * nx - x0) * SC).astype(int)
    ys = ((pc.y + offs * ny - y0) * SC).astype(int)
    ok = (xs >= 0) & (xs < pix.width) & (ys >= 0) & (ys < pix.height)
    hit = np.zeros(len(offs), bool)
    hit[ok] = m[ys[ok], xs[ok]]
    pts_.append((pc.x, pc.y)); nrm.append((nx, ny))
    cen.append(offs[hit].mean() if hit.any() else np.nan)
    wid.append(hit.sum() * 0.5)
cen, wid = np.array(cen), np.array(wid)
good = ~np.isnan(cen)
idx = np.arange(len(cen))
cen = np.interp(idx, idx[good], cen[good])                        # bridge stretches hidden by trees
cen = ndimage.median_filter(cen, size=9, mode="nearest")
cen = ndimage.uniform_filter1d(cen, size=13, mode="nearest")
width = float(np.median(wid[good & (wid > 2)]))
centre = [(px + c * nx, py + c * ny) for (px, py), (nx, ny), c in zip(pts_, nrm, cen)]
slough_line = LineString(centre).simplify(0.8)
slough_offset_ft = float(np.median(np.abs(cen[good]))) * unit_ft     # how far the traced water sits from the boundary line
# The west property line is the centreline of the waterway (architect). When the surveyed property lines are
# available, the slough is drawn centred on that line; the trace only supplies its width.
_fp = os.path.join(OUT, "data", "fences.json")
if os.path.exists(_fp):
    from shapely.ops import linemerge
    _pl = [LineString(r["map"]) for r in json.load(open(_fp)).get("property_lines", []) if len(r["map"]) > 8]   # the curved runs
    if _pl:
        _m = linemerge(_pl)
        _parts = sorted(getattr(_m, "geoms", [_m]), key=lambda g: -g.length)
        # the measured centreline tells us how far the traced water sits from the true centreline
        _d = [slough_line.interpolate(k, normalized=True).distance(_parts[0]) for k in np.linspace(0.05, 0.95, 40)]
        slough_offset_ft = float(np.median(_d)) * unit_ft
        slough_line = _parts[0] if len(_parts) == 1 else LineString([c for g in sorted(_parts[:2], key=lambda g: g.coords[0][0]) for c in g.coords])
slough = slough_line.buffer(width / 2, cap_style=2, join_style=1)
slough_raw_width_ft = width * unit_ft

# ---- canopy
m = np.isin(cls, greys[:3]) & site_m & ~raster(ponds) & ~raster(slough.buffer(4))
m = ndimage.binary_closing(m, iterations=3)
m = ndimage.binary_opening(m, iterations=3)
m = ndimage.binary_fill_holes(m) & (ndimage.binary_closing(m, iterations=8) )
canopy = polys(m, 260, 1.6).buffer(2).buffer(-2)

# ---- drives: lightest colour, thin runs only (wide light patches are bare ground or roofs)
m = (cls == greys[-1]) & site_m & ~raster(structs)
m = ndimage.binary_closing(m, iterations=4)
wide = ndimage.binary_opening(m, iterations=13)                           # anything wider than about 13 units (35'): roofs, bare ground
m = m & ~ndimage.binary_dilation(wide, iterations=5)
lab, n = ndimage.label(m)
keep = []
for i, sl in enumerate(ndimage.find_objects(lab)):
    h_, w_ = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
    if max(h_, w_) > 120:                                                 # long runs only (60 units, about 155' and up)
        keep.append(i + 1)
m = np.isin(lab, keep)
drives = polys(m, 40, 1.0).buffer(1.5).buffer(-1.5)

acres = lambda g: round(g.area * unit_ft ** 2 / 43560, 1)
out = {"source": os.path.relpath(TRACE, ROOT), "canopy": d_of(canopy), "drives": d_of(drives), "slough": d_of(slough),
       "canopy_acres": acres(canopy), "site_acres": acres(site), "slough_centre": [[round(x, 1), round(y, 1)] for x, y in slough_line.coords], "slough_width_ft": round(slough_raw_width_ft), "traced_water_offset_from_centreline_ft": round(slough_offset_ft)}
json.dump(out, open(os.path.join(OUT, "data", "aerial-derived.json"), "w"))
print("canopy", out["canopy_acres"], "ac of", out["site_acres"], "ac site |", "paths KB: canopy", len(out["canopy"]) // 1024, "drives", len(out["drives"]) // 1024, "slough", len(out["slough"]) // 1024, "| slough width ft", out["slough_width_ft"], "| traced water off the property line by ft", out["traced_water_offset_from_centreline_ft"])
