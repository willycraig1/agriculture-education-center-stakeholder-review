"""Build the layered site map for section 02 (The site), north to the left.

Writes
  drawings/site-layers.svg   editable master (one Inkscape/Illustrator layer per theme)
  slides/data/site-map.js    the same SVG as a string, for slides/site.html (works from file://)
  drawings/data/soils.json   soil units, drainage class and acreage inside the map

Layers: aerial · soils · water · trees · paddocks · campus · labels.
Soils are rebuilt from the survey sheet's soil map: each soil unit is drawn there as a fill or a dense
hatch in one color, so strokes and fills of a color are merged into polygons and named from the
sheet's soil labels. Drainage classes follow the NRCS official series descriptions (confirm in Web
Soil Survey before relying on them).

Run:  python tools/build_site_map.py   (needs pymupdf, numpy, scipy, openpyxl, shapely)
"""
import json, os, sys
import numpy as np
import pymupdf
from shapely import affinity
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from siteframe import *  # noqa: F401,F403

SLIDES = os.path.join(ROOT, "slides")

# soil unit -> drainage class (NRCS series descriptions)
DRAINAGE = {
    "4": ("Bradenton fine sand", "poorly"),
    "8": ("Delray fine sand", "very poorly"),
    "10": ("EauGallie & Myakka fine sands", "poorly"),
    "55": ("EauGallie & Myakka fine sands, urban land complex", "poorly"),
    "15": ("Floridana & Gator soils", "very poorly"),
    "22": ("Holopaw fine sand", "poorly"),
    "27": ("Matlacha gravelly fine sand (fill), urban land", "somewhat poorly"),
    "31": ("Pineda & Pineda wet fine sand", "poorly"),
}
SOIL_FILL = {"somewhat poorly": "#EFE7D4", "poorly": "#D8C69E", "very poorly": "#9FB9C6"}


def sp_shape(geom, m, t):
    """Apply a complex similarity to a shapely geometry."""
    return affinity.affine_transform(geom, [m.real, -m.imag, m.imag, m.real, t.real, t.imag])


def poly_d(g):
    out = []
    for p in getattr(g, "geoms", [g]):
        if p.is_empty or p.geom_type != "Polygon":
            continue
        for ring in [p.exterior, *p.interiors]:
            c = np.asarray(ring.coords)
            out.append("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in c) + "Z")
    return "".join(out)


def pt(m, t, x, y):
    z = m * complex(x, y) + t
    return z.real, z.imag


x0, y0, x1, y1 = VIEW
frame = box(x0, y0, x1, y1)

# site footprint: fence lines (presentation frame) grown, merged, holes filled, then shrunk back
from shapely.geometry import LineString
_fl = []
for d in fence_ds + drive_ds:
    for it in d["items"]:
        if it[0] == "l":
            (ax_, ay_), (bx_, by_) = pt(M_FP, T_FP, it[1].x, it[1].y), pt(M_FP, T_FP, it[2].x, it[2].y)
            _fl.append(LineString([(ax_, ay_), (bx_, by_)]))
_u = unary_union([l.buffer(45) for l in _fl])
_parts = [Polygon(g.exterior) for g in getattr(_u, "geoms", [_u])]
footprint = max(_parts, key=lambda g: g.area).buffer(-30).buffer(10)

# ---------------------------------------------------------------- soils
soil_ds = cadpdf.export(SURVEY, ["I-DWG-PEN-01"])["I-DWG-PEN-01"]
by_color = {}
for d in soil_ds:
    c = d.get("fill") if d["type"] in ("f", "fs") else d.get("color")
    if not c:
        continue
    key = tuple(round(v, 2) for v in c)
    by_color.setdefault(key, []).append(d)
soil_polys = {}
SCALE = 3.0                                    # raster px per survey pt
sb = (820, 56, 1645, 1650)                     # survey soil-map extent (pt)
from PIL import Image, ImageDraw
from scipy import ndimage
from skimage import measure
Wpx, Hpx = int((sb[2] - sb[0]) * SCALE), int((sb[3] - sb[1]) * SCALE)
to_px = lambda p: ((p.x - sb[0]) * SCALE, (p.y - sb[1]) * SCALE)
for key, ds in by_color.items():
    im = Image.new("1", (Wpx, Hpx), 0)
    dr = ImageDraw.Draw(im)
    for d in ds:
        pts = []
        for it in d["items"]:
            if it[0] == "l":
                a, b = to_px(it[1]), to_px(it[2])
                dr.line([a, b], fill=1, width=3)
                pts += [a, b]
            elif it[0] == "c":
                pts += [to_px(it[1]), to_px(it[4])]
            elif it[0] == "re":
                r = it[1]; dr.rectangle([to_px(r.tl), to_px(r.br)], fill=1)
            elif it[0] == "qu":
                q = it[1]; dr.polygon([to_px(q.ul), to_px(q.ur), to_px(q.lr), to_px(q.ll)], fill=1)
        if d["type"] in ("f", "fs") and len(pts) >= 3:
            dr.polygon(pts, fill=1)
    a = np.asarray(im, dtype=bool)
    a = ndimage.binary_closing(a, iterations=3)
    a = ndimage.binary_fill_holes(a)
    a = ndimage.binary_opening(a, iterations=2)
    polys = []
    for c in measure.find_contours(np.pad(a, 1).astype(float), 0.5):
        xy = np.c_[c[:, 1] - 1, c[:, 0] - 1] / SCALE + [sb[0], sb[1]]
        if len(xy) >= 4:
            p = Polygon(xy).buffer(0)
            if p.area > 20:
                polys.append(p)
    # contours of holes come back as separate rings; even-odd combine via symmetric difference
    geo = Polygon()
    for p in sorted(polys, key=lambda p: -p.area):
        geo = geo.symmetric_difference(p)
    soil_polys[key] = geo.simplify(0.5)

# name each color from the soil labels on the sheet
page = pymupdf.open(SURVEY)[0]
soil_labels = []
for b in page.get_text("dict")["blocks"]:
    for l in b.get("lines", []):
        t = "".join(s["text"] for s in l["spans"]).strip()
        if " - " in t and t.split(" - ")[0].strip().isdigit():
            bx = l["bbox"]
            soil_labels.append((t.split(" - ")[0].strip(), Point((bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2)))
units = {}
for key, geo in soil_polys.items():
    codes = sorted({c for c, p in soil_labels if geo.buffer(2).contains(p)}, key=int)
    if codes:
        units[key] = codes

ft2_per_pt2 = (FT_PER_PT / abs(M_FP)) ** 2
soil_layer, soil_json = [], []
for cls in ("somewhat poorly", "poorly", "very poorly"):
    geos = [sp_shape(g, M_SP, T_SP) for k, g in soil_polys.items()
            if k in units and DRAINAGE[units[k][0]][1] == cls]
    if not geos:
        continue
    g = unary_union(geos).intersection(footprint)
    soil_layer.append(f'<path class="soil" data-drainage="{cls}" d="{poly_d(g)}" fill="{SOIL_FILL[cls]}"/>')
for k, codes in units.items():
    g = sp_shape(soil_polys[k], M_SP, T_SP).intersection(footprint)
    soil_json.append({"codes": codes, "names": [DRAINAGE[c][0] for c in codes],
                      "drainage": DRAINAGE[codes[0]][1], "color_on_survey": k,
                      "acres_in_map": round(g.area * ft2_per_pt2 / 43560, 1)})

# ---------------------------------------------------------------- water
sv = cadpdf.export(SURVEY, ["TOP OF BANK", "FEMA FLOOD ZONE", "TREE LINE", "BUILDING", "EDGE OF PAVEMENT"])
slough = [d for d in sv.get("TOP OF BANK", []) if d["rect"].height > 150 or d["rect"].width > 150]


def g_paths(ds, m, t, attrs):
    # expose stroke width / dash pattern as data-w / data-dash so the viewer can hold them steady on zoom
    import re
    w = re.search(r'stroke-width="([\d.]+)"', attrs)
    dash = re.search(r'stroke-dasharray="([\d. ]+)"', attrs)
    extra = (f' data-w="{w.group(1)}"' if w else "") + (f' data-dash="{dash.group(1)}"' if dash else "")
    return (f'<g transform="{mat(m, t)}" {attrs}{extra}>' + paths(ds) + "</g>")


water = (g_paths(slough, M_SP, T_SP, f'fill="none" stroke="{P["water"]["base"]}" stroke-width="{6/abs(M_SP):.3f}" stroke-opacity="0.9"')
         + g_paths(water_ds, M_FP, T_FP, f'fill="{P["water"]["tint"]}" stroke="{P["water"]["base"]}" stroke-width="3"')
         + g_paths(sv.get("FEMA FLOOD ZONE", []), M_SP, T_SP,
                   f'fill="none" stroke="{P["water"]["base"]}" stroke-width="{5/abs(M_SP):.3f}" '
                   f'stroke-dasharray="{18/abs(M_SP):.2f} {10/abs(M_SP):.2f}"'))

# ---------------------------------------------------------------- trees
tree_svg = "".join(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{5.2 if s > 20 else 3.8}"/>'
                   for src, x, y, s in trees for px, py in [pt(M_FP, T_FP, x, y)])
trees_layer = (g_paths(sv.get("TREE LINE", []), M_SP, T_SP,
                       f'fill="none" stroke="{P["woodland"]["base"]}" stroke-width="{2.6/abs(M_SP):.3f}" '
                       f'stroke-dasharray="{7/abs(M_SP):.2f} {3.5/abs(M_SP):.2f}" stroke-linecap="round"')
               + f'<g fill="{P["woodland"]["base"]}" fill-opacity="0.85" stroke="#fff" stroke-width="0.8">{tree_svg}</g>')

# ---------------------------------------------------------------- paddocks
tags = []
for ac, x, y in labels:
    area, cls = canopy.get(ac, ("?", "?"))
    c = P["pasture"] if area == "Site Pasture" else P["bonus"]
    px, py = pt(M_FP, T_FP, x, y)
    tags.append(f'<g transform="translate({px:.1f} {py:.1f})"><g data-fixed="1"><rect x="-42" y="-17" width="84" height="34" rx="17" '
                f'fill="{c["tint"]}" stroke="{c["base"]}" stroke-width="2"/>'
                f'<text y="7" text-anchor="middle" font-size="20" font-weight="700" fill="{N["ink"]}">{ac:g} ac</text></g></g>')
paddocks = (g_paths(fence_ds, M_FP, T_FP, f'fill="none" stroke="#fff" stroke-width="4.5" stroke-linecap="round"')
            + g_paths(fence_ds, M_FP, T_FP, f'fill="none" stroke="{N["ink"]}" stroke-width="2" stroke-linecap="round"')
            + g_paths(drive_ds, M_FP, T_FP, f'fill="none" stroke="{P["circulation"]["base"]}" stroke-width="2.6"')
            + "".join(tags))

# ---------------------------------------------------------------- campus
campus = (g_paths(sv.get("BUILDING", []), M_SP, T_SP,
                  f'fill="{P["education"]["base"]}" stroke="{P["education"]["base"]}" stroke-width="{1/abs(M_SP):.3f}"')
          + g_paths(bldg_ds, M_FP, T_FP, f'fill="{P["circulation"]["tint"]}" stroke="{P["circulation"]["base"]}" stroke-width="1.2"')
          + g_paths(sv.get("EDGE OF PAVEMENT", []), M_SP, T_SP,
                    f'fill="none" stroke="{P["circulation"]["base"]}" stroke-width="{1.4/abs(M_SP):.3f}"'))
# Red House: centroid of the survey buildings, used for the campus callout
rh = pt(M_SP, T_SP, 1358, 1137)

# ---------------------------------------------------------------- labels
sl = []
for b in page.get_text("dict")["blocks"]:
    for l in b.get("lines", []):
        if "".join(s["text"] for s in l["spans"]).strip() == "COWPEN SLOUGH":
            bx = l["bbox"]
            sl.append(pt(M_SP, T_SP, (bx[0] + bx[2]) / 2, (bx[1] + bx[3]) / 2))
sl = [p for p in sl if x0 + 80 < p[0] < x1 - 80 and y0 + 40 < p[1] < y1 - 40]
slough_lbl = "".join(f'<g transform="translate({p[0]:.0f} {p[1]:.0f})"><text data-fixed="1" text-anchor="middle" font-size="30" font-style="italic" font-weight="600" '
                     f'fill="{P["water"]["base"]}" stroke="#fff" stroke-width="5" paint-order="stroke">Cowpen Slough</text></g>'
                     for p in sl[:1])

# ---------------------------------------------------------------- aerial
ax0, ay0 = 0, 0
aw, ah = AERIAL_SIZE
aerial = (f'<image href="../source/Site%20Aerial%20from%20SCPA.jpg" x="0" y="0" width="{aw}" height="{ah}" '
          f'transform="{mat(M_AP, T_AP)}" preserveAspectRatio="none"/>')

W, H = x1 - x0, y1 - y0
font = "font-family=\"'Avenir Next','Segoe UI','Helvetica Neue',Arial,sans-serif\""
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
       f'viewBox="{x0} {y0} {W} {H}" {font}>'
       f'<title>Clark Farm site layers (north to the left)</title>'
       f'<defs><clipPath id="frame"><rect x="{x0}" y="{y0}" width="{W}" height="{H}"/></clipPath></defs>'
       f'<rect x="{x0 - 4000}" y="{y0 - 4000}" width="{W + 8000}" height="{H + 8000}" fill="{N["paper"]}"/>'
       f'<g id="map-content">'
       + layer("aerial", "Aerial (Sarasota County PA)", aerial)
       + layer("veil", "Outside the site (veil)", f'<path d="{poly_d(box(x0 - 4000, y0 - 4000, x1 + 4000, y1 + 4000).difference(footprint))}" fill="{N["paper"]}" fill-opacity="0.72"/>'
               f'<path d="{poly_d(footprint)}" fill="none" stroke="{N["paper"]}" stroke-width="3"/>')
       + layer("soils", "Soils by drainage class", "".join(soil_layer), opacity="0.82")
       + layer("water", "Water: slough, ponds, flood zone line", water)
       + layer("trees", "Existing trees and woodland edge", trees_layer)
       + layer("paddocks", "Proposed paddocks", paddocks)
       + layer("campus", "Campus", campus)
       + layer("labels", "Labels", slough_lbl)
       + "</g></svg>")

open(os.path.join(OUT, "site-layers.svg"), "w").write(svg)
os.makedirs(os.path.join(SLIDES, "data"), exist_ok=True)
meta = {"view": VIEW, "site_acres_footprint": round(footprint.area * ft2_per_pt2 / 43560, 1), "red_house": [round(rh[0], 1), round(rh[1], 1)], "trees": len(trees),
        "soils": soil_json, "ft_per_unit": FT_PER_PT}
with open(os.path.join(SLIDES, "data", "site-map.js"), "w") as fh:
    fh.write("// Generated by tools/build_site_map.py. Do not edit by hand.\n")
    fh.write("window.SITE_MAP = " + json.dumps({"svg": svg, **meta}) + ";\n")
json.dump(soil_json, open(os.path.join(OUT, "data", "soils.json"), "w"), indent=2)
print("soil units:", [(s["codes"], s["drainage"], s["acres_in_map"]) for s in soil_json])
print("slough labels:", sl[:2], "red house:", rh, "svg KB:", len(svg) // 1024)
