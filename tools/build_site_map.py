"""Build the layered site map for section 02 (The site), north to the left.

Writes
  drawings/site-layers.svg   editable master (one Inkscape/Illustrator layer per theme)
  slides/data/site-map.js    the same SVG as a string, for slides/site.html (works from file://)
  drawings/data/soils.json   soil units, drainage class and acreage inside the map

Layers: aerial · ground · soils · water · trees · paddocks · campus · barnyard · labels.
The barnyard layer is the diagram from tools/build_ag_area.py (run that first), placed to scale on the survey.
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
footprint_auto = footprint
# Architect's edits (tools/import_site_edits.py): a hand-drawn site boundary replaces the fence-derived one,
# and hand-drawn outlines replace the survey linework for the ponds and the existing structures.
EDITS = None
_ep = os.path.join(OUT, "data", "site-edits.json")
if os.path.exists(_ep):
    EDITS = json.load(open(_ep))
    footprint = Polygon(EDITS["boundary"]).buffer(0)

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
soil_by_class = {}
for cls in ("somewhat poorly", "poorly", "very poorly"):
    geos = [sp_shape(g, M_SP, T_SP) for k, g in soil_polys.items()
            if k in units and DRAINAGE[units[k][0]][1] == cls]
    if not geos:
        continue
    g = unary_union(geos).intersection(footprint)
    soil_by_class[cls] = g
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


AD = None
_ad = os.path.join(OUT, "data", "aerial-derived.json")
if os.path.exists(_ad):
    AD = json.load(open(_ad))          # canopy, drives and Cowpen Slough from the architect's aerial trace (tools/build_canopy.py)
water = ((f'<path id="slough" d="{AD["slough"]}" fill="{P["water"]["base"]}" fill-opacity=".85"/>' if AD else "")
         + g_paths(slough, M_SP, T_SP, f'fill="none" stroke="{P["water"]["base"]}" stroke-width="{(2.2 if AD else 6)/abs(M_SP):.3f}" stroke-opacity="0.9"')
         + (g_paths(water_ds, M_FP, T_FP, f'fill="{P["water"]["tint"]}" stroke="{P["water"]["base"]}" stroke-width="3"') if not EDITS else
            "".join(f'<path class="pond {"proposed" if pd_["kind"] != "existing" else "existing"}" transform="translate({EDITS["origin"][0]} {EDITS["origin"][1]})" d="{pd_["d"]}Z" '
                    f'fill="{P["water"]["tint"]}" stroke="{P["water"]["base"]}" stroke-width="3" data-w="3"'
                    + (' stroke-dasharray="8 5" data-dash="8 5"' if pd_["kind"] != "existing" else "") + "/>" for pd_ in EDITS["ponds"]))
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
tag_pts = {}
for ac, x, y in labels:
    area, cls = canopy.get(ac, ("?", "?"))
    c = P["pasture"] if area == "Site Pasture" else P["bonus"]
    px, py = pt(M_FP, T_FP, x, y)
    tag_pts.setdefault(area, []).append((px, py, ac))
    tags.append(f'<g class="tag {"site" if area == "Site Pasture" else "bonus"}" transform="translate({px:.1f} {py:.1f})"><g data-fixed="1"><rect x="-42" y="-17" width="84" height="34" rx="17" '
                f'fill="{c["tint"]}" stroke="{c["base"]}" stroke-width="2"/>'
                f'<text y="7" text-anchor="middle" font-size="20" font-weight="700" fill="{N["ink"]}">{ac:g} ac</text></g></g>')
# Fences: continuous polylines chained from the plan's dashes (tools/build_fences.py) when available,
# so line weight, dash pattern and colour are ours to set; otherwise the raw dashes.
_fp = os.path.join(OUT, "data", "fences.json")
if os.path.exists(_fp):
    FENCES = json.load(open(_fp))
    _pl = "".join(f'<polyline id="{r_["id"]}" points="{" ".join(f"{x},{y}" for x, y in r_["map"])}"/>' for r_ in FENCES["runs"])
    _fence_art = (f'<g fill="none" stroke="#fff" stroke-width="5" data-w="5" stroke-linejoin="round" stroke-linecap="round">{_pl.replace(" id=", " data-id=")}</g>'
                  f'<g id="fence-lines" fill="none" stroke="{N["ink"]}" stroke-width="2" data-w="2" stroke-dasharray="14 6" data-dash="14 6" stroke-linejoin="round">{_pl}</g>')
else:
    _fence_art = (g_paths(fence_ds, M_FP, T_FP, f'fill="none" stroke="#fff" stroke-width="4.5" stroke-linecap="round"')
                  + g_paths(fence_ds, M_FP, T_FP, f'fill="none" stroke="{N["ink"]}" stroke-width="2" stroke-linecap="round"'))
_gd = cadpdf.export(FENCE, ["A-DOOR"]).get("A-DOOR", [])
_leaf = [d for d in _gd if all(it[0] == "l" for it in d["items"])]
_arc = [d for d in _gd if any(it[0] == "c" for it in d["items"])]
gates = (g_paths(_arc, M_FP, T_FP, f'fill="none" stroke="{P["cattle"]["base"]}" stroke-width="1" stroke-opacity=".8"')
         + g_paths(_leaf, M_FP, T_FP, f'fill="none" stroke="{P["cattle"]["base"]}" stroke-width="3" stroke-linecap="round"'))
_pw = "".join(f'<g transform="translate({pw_["map"][0]:.1f} {pw_["map"][1]:.1f})"><g data-fixed="1"><text y="-16" text-anchor="middle" font-size="15" font-weight="700" '
              f'fill="{P["water"]["base"]}" stroke="#fff" stroke-width="4" paint-order="stroke">Feed + water</text></g></g>' for pw_ in FENCES.get("pinwheels", [])) if os.path.exists(_fp) else ""
paddocks = (_fence_art + f'<g id="gates">{gates}</g><g id="pinwheel-labels">{_pw}</g>'
            + "".join(tags))

# ---------------------------------------------------------------- the land (existing: no proposed fences)
def land_label(area, key, title):
    pts = tag_pts.get(area, [])
    tot = sum(p[2] for p in pts)
    cx_ = sum(p[0] * p[2] for p in pts) / tot
    cy_ = sum(p[1] * p[2] for p in pts) / tot
    c = P[key]
    return (f'<g transform="translate({cx_:.0f} {cy_:.0f})"><g data-fixed="1">'
            f'<rect x="-150" y="-46" width="300" height="92" rx="16" fill="{c["tint"]}" stroke="{c["base"]}" stroke-width="3"/>'
            f'<text y="-8" text-anchor="middle" font-size="30" font-weight="700" fill="{N["ink"]}">{title}</text>'
            f'<text y="28" text-anchor="middle" font-size="30" font-weight="700" fill="{c["base"]}">{tot:.1f} ac</text></g></g>')


land = (f'<path d="{poly_d(footprint)}" fill="none" stroke="#fff" stroke-width="7" data-w="7"/>'
        f'<path d="{poly_d(footprint)}" fill="none" stroke="{N["ink"]}" stroke-width="3" data-w="3"/>'
        + land_label("Site Pasture", "pasture", "Site pasture") + land_label("Bonus Pasture", "bonus", "Bonus pasture"))

# ---------------------------------------------------------------- campus
# The unfinished barn is not among the architect's outlines. On the survey it is an open, roofed frame: a
# dashed overhang rectangle (BUILDING OH, about 41' x 52') with no wall lines, north of the existing barn.
from shapely.geometry import MultiPoint as _MP
_ub = [(M_SP * complex(q.x, q.y) + T_SP) for d in cadpdf.export(SURVEY, ["BUILDING OH"]).get("BUILDING OH", [])
       for it in d["items"] if it[0] == "l" for q in (it[1], it[2])]
_ub = [(z.real, z.imag) for z in _ub if abs(z.real - 1177) < 25 and abs(z.imag - 264) < 25]
UNFINISHED_BARN = list(_MP(_ub).minimum_rotated_rectangle.exterior.coords) if len(_ub) >= 3 else []
if EDITS:
    # open-sided structures are drawn with the canopies below, not as enclosed buildings (architect, 2026-10-13):
    # the unfinished barn, and the 27' x 10' shed north-west of the cattle pens
    OPEN_SHED = lambda st_: abs((st_["bbox"][0] + st_["bbox"][2]) / 2 - 1128.8) < 3 and abs((st_["bbox"][1] + st_["bbox"][3]) / 2 - 338.5) < 3
    _structs = "".join(f'<path transform="translate({EDITS["origin"][0]} {EDITS["origin"][1]})" d="{st_["d"]}Z"/>' for st_ in EDITS["structures"] if not OPEN_SHED(st_))
    _camp0 = f'<g fill="{P["education"]["base"]}" stroke="{P["education"]["base"]}" stroke-width="1">{_structs}</g>'
    # the buildings in the south bonus pasture are drawn on the fencing plan (layer P-WALL), not in the edits file
    _camp0 += g_paths(bldg_ds, M_FP, T_FP, f'id="bonus-buildings" fill="{P["education"]["base"]}" fill-opacity=".85" stroke="{P["education"]["base"]}" stroke-width="1"')
else:
    _camp0 = (g_paths(sv.get("BUILDING", []), M_SP, T_SP, f'fill="{P["education"]["base"]}" stroke="{P["education"]["base"]}" stroke-width="{1/abs(M_SP):.3f}"')
              + g_paths(bldg_ds, M_FP, T_FP, f'fill="{P["circulation"]["tint"]}" stroke="{P["circulation"]["base"]}" stroke-width="1.2"'))
# Open canopies (roof, no walls) come from the survey's overhang lines (BUILDING OH): the cattle pens' lean-to
# along the existing barn's west wall with the small canopy at its north wall, and the carport at the Red House.
# They are drawn as a tinted, dashed outline so they read differently from the enclosed buildings.
_oh = [[(z.real, z.imag) for z in (M_SP * complex(it[1].x, it[1].y) + T_SP, M_SP * complex(it[2].x, it[2].y) + T_SP)]
       for d in cadpdf.export(SURVEY, ["BUILDING OH"]).get("BUILDING OH", []) for it in d["items"] if it[0] == "l"]
def _oh_pts(x0, y0, x1, y1):
    return [q for sg in _oh for q in sg if x0 < q[0] < x1 and y0 < q[1] < y1]
def _near(pts, x, y):
    return min(pts, key=lambda q: (q[0] - x) ** 2 + (q[1] - y) ** 2)
CANOPIES = []
_pp = _oh_pts(1136, 296, 1168, 339)
if len(_pp) >= 8:
    # pens: the dashed overhang line runs down the west side; the barn's west wall closes the east side
    CANOPIES.append({"id": "cattle-pens-canopy", "label": "Cattle pens", "pts": [_near(_pp, *q) for q in
                     ((1150.8, 299.0), (1155.4, 300.4), (1153.9, 305.3), (1156.9, 306.2), (1147.8, 336.0), (1140.2, 333.7))]})
    CANOPIES.append({"id": "barn-canopy", "label": "", "pts": [_near(_pp, *q) for q in ((1156.9, 306.2), (1158.5, 300.9), (1165.0, 302.8), (1163.4, 308.1))]})
if UNFINISHED_BARN:
    CANOPIES.append({"id": "unfinished-barn", "label": "Unfinished barn", "pts": UNFINISHED_BARN[:-1]})
for st_ in (EDITS["structures"] if EDITS else []):
    if OPEN_SHED(st_):
        CANOPIES.append({"id": "pens-shed", "label": "", "pts": st_["pts"]})
_cp = _oh_pts(1220, 376, 1243, 399)
if len(_cp) >= 4:
    CANOPIES.append({"id": "carport", "label": "Carport", "pts": list(_MP(_cp).minimum_rotated_rectangle.exterior.coords)[:-1]})
_canopies = ('<g id="canopies" fill="{}" fill-opacity=".9" stroke="{}" stroke-width="1" data-w="1.6" stroke-dasharray="3 2" data-dash="5 3" stroke-linejoin="round">'.format(P["education"]["tint"], P["education"]["base"])
             + "".join(f'<polygon id="{c_["id"]}" points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in c_["pts"])}"/>' for c_ in CANOPIES) + "</g>")
print("canopies:", [(c_["id"], round(Polygon(c_["pts"]).area * (FT_PER_PT / abs(M_FP)) ** 2)) for c_ in CANOPIES], "sf")
_road_area = ""
if os.path.exists(_fp) and FENCES.get("road_area"):
    _rd = " ".join("M" + " L".join(f"{x},{y}" for x, y in ring) + "Z" for g_ in FENCES["road_area"] for ring in [g_["outer"]] + g_["holes"])
    _road_area = (f'<path id="road-area" d="{_rd}" fill-rule="evenodd" fill="{P["circulation"]["tint"]}" stroke="{P["circulation"]["base"]}" '
                  f'stroke-width="1" data-w="1.2" stroke-linejoin="round"/>')
campus = (_road_area + _camp0 + _canopies
          + ("" if _road_area else f'<g id="roads" fill="none" stroke="{P["circulation"]["base"]}" stroke-width="1.4" data-w="1.4" stroke-linejoin="round" stroke-linecap="round">'
             + "".join(f'<polyline points="{" ".join(f"{x},{y}" for x, y in r_["map"])}"/>' for r_ in FENCES.get("roads", [])) + "</g>"
             if os.path.exists(_fp) and FENCES.get("roads") else
             g_paths(sv.get("EDGE OF PAVEMENT", []), M_SP, T_SP, f'fill="none" stroke="{P["circulation"]["base"]}" stroke-width="{1.4/abs(M_SP):.3f}"')))
# Red House: centroid of the survey buildings, used for the campus callout
rh = pt(M_SP, T_SP, 1358, 1137)

# ---------------------------------------------------------------- barnyard diagram, placed on the site to scale
# The diagram (tools/build_ag_area.py, feet, square to the existing barn) is pinned to the survey by its
# existing pens: the middle of their north edge sits on the middle of the surveyed pen fence line on the
# study plan (P-RAILING, 80.9' long), and the diagram is turned to that line's bearing (17.3 degrees).
import cmath, math
_src = open(os.path.join(SLIDES, "data", "ag-area.js")).read()
AG = json.loads(_src[_src.index("{"):_src.rindex("}") + 1])
FENCE_ST = (complex(1599, 745), complex(1772, 799))      # surveyed pen fence line, study-plan points
ST_FT = FT_PER_PT * abs(M_TF)                            # study plan: feet per point
_pens = next(e for e in AG["elements"] if e["id"] == "existing-pens")
_m = cmath.rect(1 / ST_FT, cmath.phase(FENCE_ST[1] - FENCE_ST[0]))
_t = (FENCE_ST[0] + FENCE_ST[1]) / 2 - _m * complex(_pens["x"] + _pens["w"] / 2, _pens["y"])
M_DP, T_DP = M_TP * _m, M_TP * _t + T_TP                 # diagram feet -> presentation frame


def ag_poly(e):
    pts = e.get("outline") or [[e["x"], e["y"]], [e["x"] + e["w"], e["y"]], [e["x"] + e["w"], e["y"] + e["h"]], [e["x"], e["y"] + e["h"]]]
    return [pt(M_DP, T_DP, px, py) for px, py in pts]


by = []
for e in AG["elements"]:
    use3 = e["use"]
    for k in ("2", "3"):
        use3 = e.get("becomes", {}).get(k, {}).get("use", use3)
    inner = ""
    if e.get("rows"):
        sw, sd = e["stall"]
        inner += '<g fill="#fff" fill-opacity=".55" stroke="{}" stroke-width=".5">'.format(P["circulation"]["base"]) + "".join(
            f'<rect x="{r[0] + k * sw}" y="{r[1]}" width="{sw}" height="{sd}"/>' for r in e["rows"] for k in range(r[2])) + "</g>"
        isl = e.get("island")
        if isl:
            inner += f'<rect x="{isl["x"]}" y="{isl["y"]}" width="{isl["w"]}" height="{isl["h"]}" rx="3" fill="{P["water"]["tint"]}" stroke="{P["water"]["base"]}" stroke-width=".5"/>'
    for z in e.get("zones", []):
        if "poly" in z:
            inner += '<polygon points="' + " ".join(f'{e["x"] + px},{e["y"] + py}' for px, py in z["poly"]) + f'" fill="{P["arena"]["tint"]}" stroke="{P["cattle"]["base"]}" stroke-width=".5"/>'
        else:
            inner += f'<rect x="{e["x"] + z["x"]}" y="{e["y"] + z["y"]}" width="{z["w"]}" height="{z["h"]}" fill="{P["cattle"]["tint"] if z.get("fill") else "none"}" stroke="{P["cattle"]["base"]}" stroke-width=".5"/>'
    shape = ('<polygon class="shape" points="' + " ".join(f"{px},{py}" for px, py in e["outline"]) + '"' if e.get("outline")
             else f'<rect class="shape" x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}"')
    yard = e["kind"] == "yard"
    shape += (f' fill="{"none" if yard else P[use3]["tint"]}" stroke="{P[use3]["base"]}" stroke-width="1.6"' + (' stroke-dasharray="4 3"' if yard else "") + "/>")
    by.append(f'<g class="by" data-id="{e["id"]}" data-level="{e["level"]}" data-kind="{e["kind"]}" data-use="{e["use"]}" '
              f'data-use2="{e.get("becomes", {}).get("2", {}).get("use", "")}">{shape}{inner}</g>')
barnyard = f'<g transform="{mat(M_DP, T_DP)}">' + "".join(by) + "</g>"
BY_LABELS = {"cattle-a": "Cattle barn A", "cattle-b": "Cattle barn B", "small-a": "Small animal barn A", "small-b": "Extension",
             "arena": "Arena", "parking": "Parking", "handling": "Handling", "existing-barn": "Existing barn", "existing-pens": "Existing pens"}
by_labels = ""
for e in AG["elements"]:
    if e["id"] in BY_LABELS:
        lx, ly = pt(M_DP, T_DP, e["x"] + e["w"] / 2, e["y"] + e["h"] / 2)
        by_labels += (f'<text data-level="{e["level"]}" x="{lx:.1f}" y="{ly + 1.4:.1f}" text-anchor="middle" font-size="4.2" font-weight="700" fill="{N["ink"]}" '
                      f'stroke="#fff" stroke-width="1.1" paint-order="stroke">{BY_LABELS[e["id"]]}</text>')

# fit checks against the survey (presentation frame; reported in feet)
from shapely.geometry import MultiPoint
unit_ft = FT_PER_PT / abs(M_FP)
NAMES = {e["id"]: e["label"] for e in AG["elements"]}
polys = {e["id"]: Polygon(ag_poly(e)) for e in AG["elements"]}
new_ids = [e["id"] for e in AG["elements"] if not e["id"].startswith("existing")]
tree_pts = [Point(*pt(M_FP, T_FP, x, y)) for _, x, y, _s in trees]
checks = {"trees_in": {}, "wet_soil_pct": {}, "existing_structures_in": []}
for k in new_ids:
    n = sum(1 for tp in tree_pts if polys[k].contains(tp))
    if n and not k.startswith("turnout"):
        checks["trees_in"][NAMES[k]] = n
checks["trees_in_turnouts"] = sum(1 for tp in tree_pts if any(polys[k].contains(tp) for k in new_ids if k.startswith("turnout")))
wet = soil_by_class.get("very poorly")
if wet is not None:
    for e in AG["elements"]:
        if e["kind"] in ("building", "container") and not e["id"].startswith("existing"):
            pct = round(100 * polys[e["id"]].intersection(wet).area / polys[e["id"]].area)
            if pct:
                checks["wet_soil_pct"][e["label"]] = pct
# surveyed structures (BUILDING layer, grouped by proximity) that fall inside new elements
_groups = []
for d in sv.get("BUILDING", []):
    r = d["rect"]
    c = ((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
    for g_ in _groups:
        if any(abs(c[0] - o[0]) < 14 and abs(c[1] - o[1]) < 14 for o in g_["c"]):
            g_["c"].append(c); g_["r"].append(r); break
    else:
        _groups.append({"c": [c], "r": [r]})
red_house = None
for g_ in _groups:
    hull = MultiPoint([pt(M_SP, T_SP, x, y) for r in g_["r"] for x, y in ((r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1))]).minimum_rotated_rectangle
    if hull.geom_type != "Polygon":
        continue
    cs = list(hull.exterior.coords)
    size = sorted([round(math.dist(cs[0], cs[1]) * unit_ft), round(math.dist(cs[1], cs[2]) * unit_ft)], reverse=True)
    if hull.contains(Point(*rh)) or hull.distance(Point(*rh)) * unit_ft < 30:
        red_house = hull if red_house is None else red_house.union(hull)
        continue
    hit = [NAMES[k] for k in new_ids if not k.startswith("turnout") and polys[k].intersection(hull).area > 0.15 * hull.area]
    lane = None
    q = (complex(hull.centroid.x, hull.centroid.y) - T_DP) / M_DP          # centre in diagram feet
    _cd = AG["cross_drive_box"]
    if not hit and _cd[0] < q.real < _cd[2] and _cd[1] <= q.imag <= _cd[3]:
        lane = "cross drive"
    if hit or lane:
        checks["existing_structures_in"].append({"size_ft": size, "in": hit or [lane]})
# clearance from the stall rows to the nearest surveyed building line south of them (the Red House)
from shapely.geometry import LineString
_dg = lambda q_: ((M_SP * complex(q_.x, q_.y) + T_SP - T_DP) / M_DP)
_stalls = box(*AG["stalls_box"])                                  # diagram feet
_d = []
for d in sv.get("BUILDING", []):
    for it in d["items"]:
        if it[0] == "l":
            a_, b_ = _dg(it[1]), _dg(it[2])
            if min(a_.imag, b_.imag) > AG["stalls_box"][1] + 100:
                _d.append(LineString([(a_.real, a_.imag), (b_.real, b_.imag)]).distance(_stalls))
if _d:
    checks["stalls_to_red_house_ft"] = round(min(_d))
def _to_diagram(g_):
    mi = 1 / M_DP; ti = -T_DP / M_DP
    return sp_shape(g_, mi, ti)
wet_dg = {cls: _to_diagram(g_) for cls, g_ in soil_by_class.items()}
import shapely
json.dump({cls: shapely.geometry.mapping(g_.simplify(0.5)) for cls, g_ in wet_dg.items()},
          open(os.path.join(OUT, "data", "soils-in-barnyard-frame.json"), "w"))
_tz = [(complex(tp.x, tp.y) - T_DP) / M_DP for tp in tree_pts]
json.dump([[round(z.real, 1), round(z.imag, 1)] for z in _tz], open(os.path.join(OUT, "data", "trees-in-barnyard-frame.json"), "w"))
_bl = []
for d in sv.get("BUILDING", []):
    for it in d["items"]:
        if it[0] == "l":
            a_, b_ = _dg(it[1]), _dg(it[2])
            _bl.append([round(a_.real, 1), round(a_.imag, 1), round(b_.real, 1), round(b_.imag, 1)])
json.dump(_bl, open(os.path.join(OUT, "data", "buildings-in-barnyard-frame.json"), "w"))
checks["overlaps_existing"] = [[NAMES[k], NAMES[x], round(polys[k].intersection(polys[x]).area * unit_ft ** 2)] for k in new_ids
                               for x in ("existing-barn", "existing-pens") if polys[k].intersection(polys[x]).area * unit_ft ** 2 > 1]
checks["parking_to_existing_barn_ft"] = round(polys["parking"].distance(polys["existing-barn"]) * unit_ft)
checks["wet_soil_pct_turnouts"] = {e["id"]: round(100 * polys[e["id"]].intersection(wet).area / polys[e["id"]].area)
                                   for e in AG["elements"] if e["id"].startswith("turnout") and wet is not None}
ext = unary_union(list(polys.values())).bounds
checks["barnyard_box"] = [round(v, 1) for v in ext]

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
          f'transform="{aerial_matrix()}" preserveAspectRatio="none"/>')

W, H = x1 - x0, y1 - y0
font = "font-family=\"'Avenir Next','Segoe UI','Helvetica Neue',Arial,sans-serif\""
if AD:
    # label the redrawn slough about a third of the way along it, turned to follow the channel
    _sc = AD["slough_centre"]; _k = int(len(_sc) * 0.3)
    _ang = math.degrees(math.atan2(_sc[_k + 2][1] - _sc[_k - 2][1], _sc[_k + 2][0] - _sc[_k - 2][0]))
    slough_lbl = (f'<g transform="translate({_sc[_k][0]:.0f} {_sc[_k][1]:.0f}) rotate({_ang:.1f})"><text data-fixed="1" y="-14" text-anchor="middle" font-size="30" font-style="italic" font-weight="600" '
                  f'fill="{P["water"]["base"]}" stroke="#fff" stroke-width="5" paint-order="stroke">Cowpen Slough</text></g>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
       f'viewBox="{x0} {y0} {W} {H}" {font}>'
       f'<title>Clark Farm site layers (north to the left)</title>'
       f'<defs><clipPath id="frame"><rect x="{x0}" y="{y0}" width="{W}" height="{H}"/></clipPath></defs>'
       f'<rect x="{x0 - 4000}" y="{y0 - 4000}" width="{W + 8000}" height="{H + 8000}" fill="{N["paper"]}"/>'
       f'<g id="map-content">'
       + layer("aerial", "Aerial (Sarasota County PA)", aerial)
       + layer("ground", "Site ground (used when the aerial is off)", f'<path d="{poly_d(footprint)}" fill="#F2F5EA" stroke="{N["ink"]}" stroke-width="2.5" data-w="2.5"/>')
       + layer("veil", "Outside the site (veil)", f'<path d="{poly_d(box(x0 - 4000, y0 - 4000, x1 + 4000, y1 + 4000).difference(footprint))}" fill="{N["paper"]}" fill-opacity="0.72"/>'
               f'<path d="{poly_d(footprint)}" fill="none" stroke="{N["paper"]}" stroke-width="3"/>')
       + (layer("canopy", "Tree canopy (from the aerial trace)", f'<path d="{AD["canopy"]}" fill="{P["woodland"]["base"]}" fill-opacity=".3" fill-rule="evenodd"/>') if AD else "")
       # the trace's drives are not drawn: they are fragmentary and fall inside pasture enclosures (architect, 2026-10-13)
       + (layer("property", "Surveyed property lines (fencing plan)", f'<g fill="none" stroke="{N["ink"]}" stroke-width="1.6" data-w="1.6" stroke-dasharray="10 4 2 4" data-dash="10 4 2 4" stroke-opacity=".75">'
                + "".join(f'<polyline id="{r_["id"]}" points="{" ".join(f"{x},{y}" for x, y in r_["map"])}"/>' for r_ in FENCES.get("property_lines", [])) + "</g>") if os.path.exists(_fp) else "")
       + layer("soils", "Soils by drainage class", "".join(soil_layer), opacity="0.82")
       + layer("water", "Water: slough, ponds, flood zone line", water)
       + layer("trees", "Existing trees and woodland edge", trees_layer)
       + layer("land", "The land: site and bonus pasture areas", land)
       + layer("paddocks", "Proposed paddocks", paddocks)
       + layer("campus", "Campus", campus)
       + layer("barnyard", "Proposed barnyard (Level 3 shown), to scale", barnyard + f'<g id="barnyard-labels">{by_labels}</g>')
       + layer("labels", "Labels", slough_lbl)
       + "</g></svg>")

open(os.path.join(OUT, "site-layers.svg"), "w").write(svg)
os.makedirs(os.path.join(SLIDES, "data"), exist_ok=True)
_cb = [c for st_ in (EDITS["structures"] if EDITS else []) for c in st_["pts"]] + [list(q) for q in UNFINISHED_BARN]
CAMPUS_BOX = [min(c[0] for c in _cb), min(c[1] for c in _cb), max(c[0] for c in _cb), max(c[1] for c in _cb)] if _cb else [rh[0] - 80, rh[1] - 80, rh[0] + 80, rh[1] + 80]
meta = {"canopy_acres": AD["canopy_acres"] if AD else None, "campus_box": [round(v, 1) for v in CAMPUS_BOX], "barnyard": {"checks": checks, "diagram_to_presentation": {"m": [M_DP.real, M_DP.imag], "t": [T_DP.real, T_DP.imag]},
                     "bearing_deg": math.degrees(cmath.phase(FENCE_ST[1] - FENCE_ST[0]))},
        "view": VIEW, "site_acres_footprint": round(footprint.area * ft2_per_pt2 / 43560, 1), "site_acres_footprint_previous": round(footprint_auto.area * ft2_per_pt2 / 43560, 1), "red_house": [round(rh[0], 1), round(rh[1], 1)], "trees": len(trees),
        "soils": soil_json, "ft_per_unit": FT_PER_PT}
with open(os.path.join(SLIDES, "data", "site-map.js"), "w") as fh:
    fh.write("// Generated by tools/build_site_map.py. Do not edit by hand.\n")
    fh.write("window.SITE_MAP = " + json.dumps({"svg": svg, **meta}) + ";\n")
json.dump(soil_json, open(os.path.join(OUT, "data", "soils.json"), "w"), indent=2)
print("soil units:", [(s["codes"], s["drainage"], s["acres_in_map"]) for s in soil_json])
print("barnyard fit:", checks)
print("site boundary acres:", round(footprint.area * ft2_per_pt2 / 43560, 1), "(fence-derived:", round(footprint_auto.area * ft2_per_pt2 / 43560, 1), ")")
print("slough labels:", sl[:2], "red house:", rh, "svg KB:", len(svg) // 1024)
