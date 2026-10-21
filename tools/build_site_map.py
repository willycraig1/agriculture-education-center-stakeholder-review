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
import json, math, os, re, sys
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
    footprint_drawn = Polygon(EDITS["boundary"]).buffer(0)
    footprint = Polygon(snapped_boundary(EDITS["boundary"])).buffer(0)       # west side on the property line
    print("site boundary: west side snapped to the property line; acres", round(footprint_drawn.area * (FT_PER_PT / abs(M_FP)) ** 2 / 43560, 1), "->", round(footprint.area * (FT_PER_PT / abs(M_FP)) ** 2 / 43560, 1))

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
# The top-of-bank line that runs along Cow Pen Slough itself is dropped (the slough is redrawn as a band). The
# others are kept: they trace the historical slough bed across the site.
_adp = os.path.join(OUT, "data", "aerial-derived.json")
if os.path.exists(_adp):
    _scl = LineString(json.load(open(_adp))["slough_centre"])
    def _along_slough(d):
        q = [pt(M_SP, T_SP, it[1].x, it[1].y) for it in d["items"] if it[0] in ("l", "c")]
        return len(q) > 1 and float(np.median([_scl.distance(Point(*c)) for c in q])) * FT_PER_PT / abs(M_FP) < 100
    slough = [d for d in slough if not _along_slough(d)]


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
# The historical slough bed: one transparent field from top of bank to top of bank (tools/build_slough_bed.py),
# in place of the survey's separate bank lines.
_bp = _bp_bed = os.path.join(OUT, "data", "slough-bed.json")
if os.path.exists(_bp):
    _BJ = json.load(open(_bp))
    _ring_d = lambda parts: " ".join("M" + " L".join(f"{x},{y}" for x, y in ring) + "Z" for p_ in parts for ring in [p_["outer"]] + p_["holes"])
    _bd = _ring_d(_BJ["parts"])
    # the ditch floor between the toe-of-slope lines, darker than the banks, with the toe lines drawn fine
    _floor = (f'<g id="historic-slough-floor"><path d="{_ring_d(_BJ.get("floor", []))}" fill="{P["water"]["base"]}" fill-opacity=".38" fill-rule="evenodd"/>'
              f'<g fill="none" stroke="{P["water"]["base"]}" stroke-opacity=".75" stroke-width=".7" data-w="1.1" stroke-linejoin="round">'
              + "".join(f'<polyline points="{" ".join(f"{x},{y}" for x, y in ln)}"/>' for ln in _BJ.get("toe_lines", [])) + "</g></g>") if _BJ.get("toe_lines") else ""
    # the bed bank to bank in a transparent pasture green: most of the time it is grassed pasture (architect,
    # 2026-10-14); the ditch floor stays blue
    _bed_svg = (f'<path id="historic-slough" d="{_bd}" fill="{P["pasture"]["base"]}" fill-opacity=".32" fill-rule="evenodd"/>' + _floor +
                f'<g id="historic-slough-label" transform="translate(905 437)"><text data-fixed="1" text-anchor="middle" font-size="19" font-style="italic" font-weight="600" '
                f'fill="{P["water"]["base"]}" stroke="#fff" stroke-width="4" paint-order="stroke">Historical slough bed</text></g>')
else:
    _bed_svg = g_paths(slough, M_SP, T_SP, f'fill="none" stroke="{P["water"]["base"]}" stroke-width="{(2.2 if AD else 6)/abs(M_SP):.3f}" stroke-opacity="0.9"')
# A possible floodplain compensation area, for discussion only. First traced from the architect's markup on the
# water slide (2026-10-13, about 1.1 ac east of the head pond). Widened the same day after civil's note that the
# strategy is a larger, more expansive compensation area at a shallower depth, so water stands lower between
# major storms and the area stays in grazing: it now takes the open ground of the paddock east of the head
# pond, between the flood zone line to the north and the historical bed to the south, as far as the paddock's
# east fence. Extent chosen by eye; civil's quantities are not in yet. Not designed or sized. Hidden unless a
# slide turns it on.
COMP_PTS = [(739, 326), (770, 331), (800, 336), (822, 331), (846, 317), (884, 315), (910, 314), (912, 318), (912, 413), (906, 414),
            (860, 413), (820, 409), (780, 407), (760, 405), (742, 400), (738, 394)]
_comp = Polygon(COMP_PTS).buffer(-4).buffer(4)
COMP_ACRES = round(_comp.area * (FT_PER_PT / abs(M_FP)) ** 2 / 43560, 1)
# Civil's sketches (tools/build_civil.py) replace the discussion-only area: floodplain compensation Options 1 and 2,
# and the expanded stormwater retention. All shown on the water slide's plan step only.
CIVIL = json.load(open(os.path.join(OUT, "data", "civil.json"))) if os.path.exists(os.path.join(OUT, "data", "civil.json")) else None
def _lbl(x, y, l1, l2, col):
    return (f'<g transform="translate({x:.0f} {y:.0f})"><g data-fixed="1">'
            f'<text y="-4" text-anchor="middle" font-size="18" font-weight="700" fill="{col}" stroke="#fff" stroke-width="4" paint-order="stroke">{l1}</text>'
            f'<text y="18" text-anchor="middle" font-size="15" font-style="italic" font-weight="600" fill="{col}" stroke="#fff" stroke-width="4" paint-order="stroke">{l2}</text></g></g>')
if CIVIL:
    _o1, _o2 = Polygon(CIVIL["option1"]), Polygon(CIVIL["option2"])
    _rx = [Polygon(q) for q in CIVIL["retention_expansion"]]
    _cg = P["pasture"]["base"]
    _comp_svg = ('<g id="compensation" display="none">'
                 + "".join(f'<path d="{poly_d(o_)}" fill="{P["pasture"]["base"]}" fill-opacity=".18" stroke="{_cg}" stroke-width="2" data-w="2.5" stroke-dasharray="6 4" data-dash="8 5"/>' for o_ in (_o1, _o2))
                 + "<!--SITE-RET-OPTION-->"            # civil's retention, refitted to the plan once the barnyard is placed
                 + _lbl(_o1.centroid.x, _o1.centroid.y, "Option 1", f'{CIVIL["option1_acres"]} ac, floodplain comp.', _cg)
                 + _lbl(_o2.centroid.x, _o2.centroid.y, "Option 2", f'{CIVIL["option2_acres"]} ac, floodplain comp.', _cg)
                 + "</g>")
    COMP_ACRES = None
else:
    _comp_svg = ""
# The proposed retention pond's area, labelled with the compensation area on the water slide's plan step.
RET_ACRES, _ret_lbl = None, ""
_rp_ = os.path.join(OUT, "data", "retention-markup.json")
_RM = json.load(open(_rp_)) if os.path.exists(_rp_) else None
_RET_MERGED = Polygon(_RM["site_ponds"][0]) if _RM else None       # proposed pond, merged and cleaned with the markup
for _pd in (EDITS["ponds"] if EDITS else []):
    if _pd["kind"] != "existing" and len(_pd.get("pts", [])) >= 3:
        _rp = _RET_MERGED if _RET_MERGED is not None else Polygon(_pd["pts"]).buffer(0)
        RET_ACRES = round(_rp.area * (FT_PER_PT / abs(M_FP)) ** 2 / 43560, 1)
        _ret_lbl = (f'<g id="retention-label" display="none" transform="translate({_rp.centroid.x:.0f} {_rp.centroid.y:.0f})"><g data-fixed="1">'
                    f'<text y="-4" text-anchor="middle" font-size="18" font-weight="700" fill="{P["water"]["base"]}" stroke="#fff" stroke-width="4" paint-order="stroke">Site retention pond</text>'
                    f'<text y="18" text-anchor="middle" font-size="16" font-weight="700" fill="{P["water"]["base"]}" stroke="#fff" stroke-width="4" paint-order="stroke">{RET_ACRES} ac</text></g></g>')
        print("proposed retention pond acres:", RET_ACRES, "| centroid", round(_rp.centroid.x), round(_rp.centroid.y))
# Drainage infrastructure on the historical bed (architect, 2026-10-13). The outfall is drawn from the survey. The
# entry culvert is not on the survey's storm sewer layer, so its line is diagrammatic, drawn between the surveyed
# ends of the ditch floor either side of the drive.
#   entry culvert  under the entry apron, joining the bed either side of the drive: to be replaced (sizing, maintenance)
#   outfall        from the south end of the bed to Cow Pen Slough: in good shape and sized for the plan (civil)
_infra = _infra_lbl = ""
INFRA = {}
if os.path.exists(_bp) and AD:
    _toe_ends = [tuple(q) for ln in json.load(open(_bp))["toe_lines"] for q in (ln[0], ln[-1])]
    _near = lambda x, y: min(_toe_ends, key=lambda q: (q[0] - x) ** 2 + (q[1] - y) ** 2)
    _c0, _c1 = _near(1141, 501), _near(1184, 521)                      # either side of the entry drive
    # The outfall is on the survey (layer STORM SEWER: the two walls of the pipe run, under the lane). Its line
    # here is the middle of those two. The survey sheet notes it at both ends: "(2) 36" CPP End of Pipe",
    # invert 16.47' at the bed end and 16.00' at the slough end
    # (source/260036_SPS_Draft for FE_9-4-26.pdf, sheet 10).
    _ss = [[pt(M_SP, T_SP, q.x, q.y) for q in (it[1], it[2])] for d in cadpdf.export(SURVEY, ["STORM SEWER"]).get("STORM SEWER", [])
           for it in d["items"] if it[0] == "l"]
    _ss = [sorted(sg, key=lambda q: q[1]) for sg in _ss if math.hypot(sg[1][0] - sg[0][0], sg[1][1] - sg[0][1]) > 10]
    _o0 = tuple(sum(sg[0][k] for sg in _ss) / len(_ss) for k in (0, 1))        # bed end
    _o1 = tuple(sum(sg[1][k] for sg in _ss) / len(_ss) for k in (0, 1))        # slough end
    _uf = FT_PER_PT / abs(M_FP)
    # the culvert is shown only where it passes under the driveway, carried 8 ft beyond the pavement on each side
    _fj = os.path.join(OUT, "data", "fences.json")
    _road = json.load(open(_fj)).get("road_area") if os.path.exists(_fj) else None
    if _road:
        _drive = unary_union([Polygon(g_["outer"], g_["holes"]).buffer(0) for g_ in _road])
        _cl = LineString([_c0, _c1])
        _hit = _cl.intersection(_drive)
        if not _hit.is_empty:
            _ts = [_cl.project(Point(q)) for g_ in getattr(_hit, "geoms", [_hit]) for q in g_.coords]
            _a, _b = max(0.0, min(_ts) - 8 / _uf), min(_cl.length, max(_ts) + 8 / _uf)
            _c0, _c1 = _cl.interpolate(_a).coords[0], _cl.interpolate(_b).coords[0]
            print("entry culvert: driveway crossing ft", round((max(_ts) - min(_ts)) * _uf))
    INFRA = {"entry_culvert_ft": round(math.hypot(_c1[0] - _c0[0], _c1[1] - _c0[1]) * _uf), "outfall_ft": round(math.hypot(_o1[0] - _o0[0], _o1[1] - _o0[1]) * _uf)}
    def _pipe(a, b, col, id_, l1, l2, dx, dy, anchor):
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        # the pipe line stays in the water layer, under the drives; its note goes in the top (labels) layer
        return (f'<g id="{id_}"><line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#fff" stroke-width="4" data-w="8" stroke-linecap="round"/>'
                f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="{col}" stroke-width="2.4" data-w="5" stroke-linecap="round"/></g>',
                f'<g transform="translate({mx:.1f} {my:.1f})"><g data-fixed="1">'
                f'<text x="{dx}" y="{dy}" text-anchor="{anchor}" font-size="17" font-weight="700" fill="{col}" stroke="#fff" stroke-width="4" paint-order="stroke">{l1}</text>'
                f'<text x="{dx}" y="{dy + 20}" text-anchor="{anchor}" font-size="15" font-weight="600" fill="{col}" stroke="#fff" stroke-width="4" paint-order="stroke">{l2}</text></g></g>')
    _p1 = _pipe(_c0, _c1, P["education"]["base"], "entry-culvert", "Culvert under the entry", "replace: undersized, hard to maintain", -14, 34, "end")
    _p2 = _pipe(_o0, _o1, P["woodland"]["base"], "outfall", "Outfall: two 36&#8243; pipes, inv. 16.47&#8242; to 16.00&#8242;", "keep: sound and sized for the plan", 16, -22, "start")
    if MAIN_PARCEL_ONLY:                                   # the outfall is on the Solid Waste land, past pl-04
        _p2 = ("", "")
    _infra = '<g id="infrastructure" display="none">' + _p1[0] + _p2[0] + "</g>"
    _infra_lbl = '<g id="infrastructure-labels" display="none">' + _p1[1] + _p2[1] + "</g>"
    print("infrastructure lines ft:", INFRA)
_fj_ = os.path.join(OUT, "data", "fences.json")
_mclip = MAIN_PARCEL_ONLY and os.path.exists(_fj_) and any(r_["id"] == "pl-04" for r_ in json.load(open(_fj_)).get("property_lines", []))
water = ((f'<path id="slough" d="{AD["slough"]}" fill="{P["water"]["base"]}" fill-opacity=".85"/>' if AD else "")
         + ('<g clip-path="url(#main-side)">' if _mclip else "") + _bed_svg + _comp_svg
         + (g_paths(water_ds, M_FP, T_FP, f'fill="{P["water"]["tint"]}" stroke="{P["water"]["base"]}" stroke-width="3"') if not EDITS else
            "".join((f'<path class="pond proposed" d="{poly_d(_RET_MERGED)}" ' if pd_["kind"] != "existing" and _RET_MERGED is not None else
                     f'<path class="pond {"proposed" if pd_["kind"] != "existing" else "existing"}" transform="translate({EDITS["origin"][0]} {EDITS["origin"][1]})" d="{pd_["d"]}Z" ')
                    + f'fill="{P["water"]["tint"]}" stroke="{P["water"]["base"]}" stroke-width="3" data-w="3"'
                    + (' stroke-dasharray="8 5" data-dash="8 5"' if pd_["kind"] != "existing" else "") + "/>" for pd_ in EDITS["ponds"]))
         + g_paths(sv.get("FEMA FLOOD ZONE", []), M_SP, T_SP,
                   f'fill="none" stroke="{P["water"]["base"]}" stroke-width="{5/abs(M_SP):.3f}" '
                   f'stroke-dasharray="{18/abs(M_SP):.2f} {10/abs(M_SP):.2f}"')
         + ("</g>" if _mclip else "") + _ret_lbl + _infra)

# ---------------------------------------------------------------- trees
tree_svg = "".join(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{5.2 if s > 20 else 3.8}"/>'
                   for src, x, y, s in trees for px, py in [pt(M_FP, T_FP, x, y)])
# The survey's dashed tree line is no longer drawn: the canopy traced from the aerial replaces it. Surveyed trees
# are plain discs at 70% opacity, no outline (architect, 2026-10-13).
trees_layer = f'<g fill="{P["woodland"]["base"]}" fill-opacity="0.7">{tree_svg}</g>'

# ---------------------------------------------------------------- paddocks
tags = []
tag_pts = {}
for _ti, (ac, x, y) in enumerate(labels):
    area, cls = canopy.get(ac, ("?", "?"))
    c = P["pasture"] if area == "Site Pasture" else P["bonus"]
    px, py = pt(M_FP, T_FP, x, y)
    tag_pts.setdefault(area, []).append((px, py, ac))
    tags.append(f'<g class="tag {"site" if area == "Site Pasture" else "bonus"}" data-pad="{_ti}" transform="translate({px:.1f} {py:.1f})"><g data-fixed="1"><rect x="-42" y="-17" width="84" height="34" rx="17" '
                f'fill="{c["tint"]}" stroke="{c["base"]}" stroke-width="2"/>'
                f'<text y="7" text-anchor="middle" font-size="20" font-weight="700" fill="{N["ink"]}">{ac:g} ac</text></g></g>')
# Fences: continuous polylines chained from the plan's dashes (tools/build_fences.py) when available,
# so line weight, dash pattern and colour are ours to set; otherwise the raw dashes.
import cmath, math
_src = open(os.path.join(SLIDES, "data", "ag-area.js")).read()
AG = json.loads(_src[_src.index("{"):_src.rindex("}") + 1])
_pens = next(e for e in AG["elements"] if e["id"] == "existing-pens")
M_DP, T_DP = diagram_transform(_pens["x"] + _pens["w"] / 2, _pens["y"])      # diagram feet -> presentation frame


_fp = os.path.join(OUT, "data", "fences.json")
_walk_gates = []          # gate leaves across the walk, added below with the plan's own gates
if os.path.exists(_fp):
    FENCES = json.load(open(_fp))
    _PLAN_RUNS = [LineString(r_["map"]) for r_ in FENCES["runs"]]            # the fencing plan as drawn, before the campus redraw
    # ---- campus fence, redrawn to the barnyard (architect, 2026-10-13)
    # The fencing plan's line round the north and west of the campus was drawn for an earlier layout and cut
    # through the new barns. It is replaced, between its two ends, by a line on the outer edges of the turnout
    # yards: up the east edge of the cattle turnouts, along the north face of the barnyard, round the small
    # animal turnouts, and down the west side of the handling yard to where the old line turns for the lane.
    # The first two and the last vertex of the plan's run are kept, so its gates and junctions are untouched.
    _el = {e_["id"]: e_ for e_ in AG["elements"]}
    _cf = min(FENCES["runs"], key=lambda r_: min(math.hypot(q[0] - 1087.2, q[1] - 339.6) for q in r_["map"]))      # the run through the old campus corner
    if all(k in _el for k in ("turnout-cattle-b", "arena", "turnout-small-b", "handling")) and len(_cf["map"]) >= 6:
        _to_d = lambda q: (complex(*q) - T_DP) / M_DP
        _to_m = lambda x, y: [round(v, 2) for v in pt(M_DP, T_DP, x, y)]
        _tb, _ar, _ts, _hd = _el["turnout-cattle-b"], _el["arena"], _el["turnout-small-b"], _el["handling"]
        _east, _north = _tb["x"] + _tb["w"], _tb["y"]
        _end_d = _to_d(_cf["map"][-1])
        if AG.get("counts", {}).get("option") == "B":
            # Option B: round the north side of the cattle turnouts, the west end of the small animal barns' turnout,
            # and back down to the plan's last leg at the lane; east of the turnouts it follows the holding pens' top
            _ts = _el.get("turnout-small-a", _el["turnout-small-b"]); _hp = _el["holding-3"]
            _xw_ = _ts["x"]; _ye = round(_end_d.imag, 1)
            _new_d = [(_hp["x"] + _hp["w"], _hp["y"]), (_el["turnout-cattle-a"]["x"] + _el["turnout-cattle-a"]["w"], _hp["y"]),
                      (_el["turnout-cattle-a"]["x"] + _el["turnout-cattle-a"]["w"], _tb["y"]), (_tb["x"], _tb["y"]), (_tb["x"], _ts["y"]),
                      (_xw_, _ts["y"]), (_xw_, _ye)]           # on the small animal turnout's north and west edges
        elif "holding-3" in _el and "holding-1" in _el:
            # round the outside of the holding pens: along pen 3's north side, down the pens' west fence to the
            # level of the plan's last leg, then along that leg to its gate at the lane
            (_nwx, _nwy), (_swx, _swy) = _el["holding-3"]["outline"][3], _el["holding-1"]["outline"][-2]
            _ye = round(_end_d.imag, 1)
            _xw = _nwx + (_swx - _nwx) * (_ye - _nwy) / (_swy - _nwy)
            _new_d = [(_east, _north), (_ar["x"], _north), (_ar["x"], _ts["y"]), (_ts["x"], _ts["y"]), (_nwx, _nwy), (round(_xw, 1), _ye)]
        else:
            _new_d = [(_east, _north), (_ar["x"], _north), (_ar["x"], _ts["y"]), (_ts["x"], _ts["y"]), (_ts["x"], _hd["y"]),
                      (_hd["x"], _hd["y"]), (_hd["x"], round(_end_d.imag, 1))]
        _old_ft = _cf["length_ft"]
        if AG.get("counts", {}).get("option") == "B" and "existing-barn" in _el:
            # East of the barnyard the fence runs on the existing barn's lean-to column line, the pens' front 8' off
            # the barn, which is also the walk's north edge (owner, 2026-10-19; sheet A2.0 Existing Barn): from the
            # walk gate west to the lean-to's corner column 13' past the barn, north up that line to the pens' back
            # fence, and along it to the pens' north-east corner, where it meets the line round the holding pens.
            # This replaces the plan's first two vertices (its start was 8' short of the walk).
            _eb, _epn = _el["existing-barn"], _el["existing-pens"]
            _yw, _xc = _epn["y"] + _epn["h"], _eb["x"] + _eb["w"] + 13.0
            _new_d = [(round(_to_d(_cf["map"][0]).real, 1), _yw), (_xc, _yw), (_xc, _epn["y"]), (_epn["x"] + _epn["w"], _epn["y"])] + _new_d
            if "holding-3" in _el and abs(_el["holding-3"]["x"] + _el["holding-3"]["w"] - _xc) < 1:
                # the holding pens now run out to that same column line (the dog-ear, 2026-10-20), so the fence goes
                # straight up it to their north-east corner; the jog back to the existing pens' corner cut diagonally
                # across the pens (owner, 2026-10-20)
                _new_d = _new_d[:2] + _new_d[4:]
            _cf["map"] = [_to_m(x, y) for x, y in _new_d] + _cf["map"][-1:]
        else:
            _cf["map"] = _cf["map"][:2] + [_to_m(x, y) for x, y in _new_d] + _cf["map"][-1:]
        _cf["length_ft"] = round(LineString(_cf["map"]).length * FT_PER_PT / abs(M_FP))
        _cf["redrawn"] = "campus fence aligned to the turnout yards, 2026-10-13"
        _cf.pop("sheet", None)
        json.dump({"note": "The campus fence as redrawn to the barnyard's turnout yards; replaces this run of fences.json on the map.",
                   "id": _cf["id"], "length_ft": _cf["length_ft"], "plan_length_ft": _old_ft, "diagram_ft": [list(q) for q in _new_d], "map": _cf["map"]},
                  open(os.path.join(OUT, "data", "campus-fence.json"), "w"), indent=1)
        # fences that ran to the old campus line are carried on to the new one (straight, along their last leg)
        _cfl = LineString(_cf["map"])
        for _r in FENCES["runs"]:
            if _r is _cf:
                continue
            for _k in (0, -1):
                _e = Point(_r["map"][_k]); _dd = _cfl.distance(_e) * FT_PER_PT / abs(M_FP)
                if 1 < _dd < 80 and _PLAN_RUNS and min(g_.distance(_e) for g_ in [LineString(rr_["map"]) for rr_ in FENCES["runs"] if rr_ is not _r and rr_ is not _cf] or [Point(1e9, 1e9)]) > 2:
                    _q = _r["map"][1] if _k == 0 else _r["map"][-2]
                    _dx, _dy = _e.x - _q[0], _e.y - _q[1]
                    _L = math.hypot(_dx, _dy) or 1
                    _ray = LineString([(_e.x, _e.y), (_e.x + _dx / _L * 60, _e.y + _dy / _L * 60)])
                    _hit = _ray.intersection(_cfl)
                    _hp_ = _hit if _hit.geom_type == "Point" else (min(getattr(_hit, "geoms", []), key=lambda g: g.distance(_e)) if not _hit.is_empty else None)
                    if _hp_ is not None and _hp_.geom_type == "Point":
                        if _k == 0: _r["map"].insert(0, [round(_hp_.x, 2), round(_hp_.y, 2)])
                        else: _r["map"].append([round(_hp_.x, 2), round(_hp_.y, 2)])
                        print("  fence", _r["id"], "carried", round(_dd), "ft to the campus fence")
        # where a fence meets the walk east of the existing barn it stops at the pavement edge, and a gate spans the
        # walk between it and the campus fence (owner, 2026-10-19)
        if "walk" in _el:
            from shapely.geometry import Polygon as _Pg
            _wkd = _Pg(_el["walk"]["outline"]).buffer(0)
            _gs = _to_d(_cf["map"][0])
            for _r in FENCES["runs"]:
                if _r is _cf:
                    continue
                for _k, _n in ((0, 1), (-1, -2)):
                    _e = _to_d(_r["map"][_k])
                    if _wkd.contains(Point(_e.real, _e.imag)) and abs(_e - _gs) < 20:
                        _q = _to_d(_r["map"][_n])
                        _x = LineString([(_e.real, _e.imag), (_q.real, _q.imag)]).intersection(_wkd.boundary)
                        _x = min(getattr(_x, "geoms", [_x]), key=lambda g: g.distance(Point(_e.real, _e.imag)))
                        _r["map"][_k] = _to_m(_x.x, _x.y)
                        _walk_gates.append([_cf["map"][0], _r["map"][_k]])
                        print("  fence", _r["id"], "stops at the walk; gate across it,", round(abs(complex(_x.x, _x.y) - _gs), 1), "ft")
        print("campus fence redrawn:", _cf["id"], _old_ft, "ft ->", _cf["length_ft"], "ft")
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
if os.path.exists(_fp) and FENCES.get("gates_added"):
    # data-w so the viewer counter-scales them on zoom like the other gates (g_paths adds it for those)
    gates += (f'<g id="gates-added" fill="none" stroke="{P["cattle"]["base"]}" stroke-width="3" data-w="3" stroke-linecap="round">'
              + "".join(f'<line x1="{g_["map"][0][0]}" y1="{g_["map"][0][1]}" x2="{g_["map"][1][0]}" y2="{g_["map"][1][1]}"/>' for g_ in FENCES["gates_added"]) + "</g>")
if _walk_gates:
    gates += (f'<g id="gates-walk" fill="none" stroke="{P["cattle"]["base"]}" stroke-width="3" data-w="3" stroke-linecap="round">'
              + "".join(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}"/>' for a, b in _walk_gates) + "</g>")
# ---- paddocks as closed shapes, filled by area (site pasture / bonus pasture)
# The fence lines are thickened until the gate openings close, which cuts the site into faces; each face is grown
# back to the fence line. Two fence ends that stop short of each other (the 3.8 ac paddock, open toward the lane)
# are joined first. A face is a paddock when one acreage label sits in it.
PADS, _pad_svg, _area_svg = [], "", ""
if os.path.exists(_fp) and FENCES.get("runs"):
    _G = 6.0
    _uf2 = (FT_PER_PT / abs(M_FP)) ** 2 / 43560
    def _pad_polys(_R):
        _loose = []
        for _i, _r in enumerate(_R):
            for _e in (_r.coords[0], _r.coords[-1]):
                if min(o.distance(Point(_e)) for _j, o in enumerate(_R) if _j != _i) > 9:
                    _loose.append(_e)
        _close = [LineString([a_, b_]) for _k, a_ in enumerate(_loose) for b_ in _loose[_k + 1:] if 9 < math.hypot(a_[0] - b_[0], a_[1] - b_[1]) < 80]
        _faces = footprint.buffer(-0.5).difference(unary_union(_R + _close).buffer(_G))
        _faces = list(getattr(_faces, "geoms", [_faces]))
        out_ = []
        for ac, x, y in labels:
            px, py = pt(M_FP, T_FP, x, y)
            _in = [f_ for f_ in _faces if f_.contains(Point(px, py))] or [min(_faces, key=lambda f_: f_.distance(Point(px, py)))]
            out_.append(_in[0].buffer(_G, join_style=2).intersection(footprint).simplify(0.4))
        return out_
    _now = _pad_polys([LineString(r_["map"]) for r_ in FENCES["runs"]])
    _plan = _pad_polys(_PLAN_RUNS)
    # Acres: the fencing plan's own figure for each paddock, adjusted only where the fence has since moved (the
    # campus redraw), by the change this script measures between the plan's fence and the redrawn one.
    _dense = {round(float(r_[1]), 1): float(r_[2] or 0) for r_ in wb["Paddock Detail"].iter_rows(min_row=5, max_row=20, values_only=True) if r_[0] and r_[1]}
    _dense.setdefault(10.2, 7.7 / 10.2)                      # 7.7 ac dense woods + 2.5 ac open, merged on the revised plan
    for _ti, (ac, x, y) in enumerate(labels):
        _d = (_now[_ti].area - _plan[_ti].area) * _uf2
        _site = canopy.get(ac, ("?", "?"))[0] == "Site Pasture"
        PADS.append({"i": _ti, "label_ac": ac, "measured_ac": round(_now[_ti].area * _uf2, 1), "change_ac": round(_d, 2),
                     "acres": round(ac + _d, 1) if abs(_d) >= 0.05 else ac, "site": _site, "dense": round(_dense.get(round(ac, 1), 0), 4), "poly": _now[_ti]})
    _bad = [(p_["label_ac"], p_["measured_ac"]) for p_ in PADS if abs(p_["acres"] - p_["measured_ac"]) > 0.3]
    print("paddock shapes:", len(PADS), "| acres vs measured off by more than 0.3:", _bad or "none", "| changed by the campus redraw:", [(p_["label_ac"], p_["acres"]) for p_ in PADS if p_["acres"] != p_["label_ac"]])
    json.dump({"note": "Paddock acres used for capacity: the fencing plan's figure, adjusted where the campus fence was redrawn. dense = share treated as dense woods (pasture worksheet).",
               "paddocks": [{"group": "site" if p_["site"] else "bonus", "plan_acres": p_["label_ac"], "acres": p_["acres"], "change_ac": p_["change_ac"],
                             "measured_acres": p_["measured_ac"], "dense": p_["dense"]} for p_ in PADS]},
              open(os.path.join(OUT, "data", "paddocks.json"), "w"), indent=1)
    # tags and area totals carry the adjusted acres
    tags, tag_pts = [], {}
    for p_ in PADS:
        ac0, x, y = labels[p_["i"]]
        area = "Site Pasture" if p_["site"] else "Bonus Pasture"
        c = P["pasture"] if p_["site"] else P["bonus"]
        px, py = pt(M_FP, T_FP, x, y)
        tag_pts.setdefault(area, []).append((px, py, p_["acres"]))
        tags.append(f'<g class="tag {"site" if p_["site"] else "bonus"}" data-pad="{p_["i"]}" transform="translate({px:.1f} {py:.1f})"><g data-fixed="1"><rect x="-42" y="-17" width="84" height="34" rx="17" '
                    f'fill="{c["tint"]}" stroke="{c["base"]}" stroke-width="2"/>'
                    f'<text y="7" text-anchor="middle" font-size="20" font-weight="700" fill="{N["ink"]}">{p_["acres"]:g} ac</text></g></g>')
    for p_ in PADS:
        c_ = P["pasture"] if p_["site"] else P["bonus"]
        _pad_svg += (f'<path class="pad {"site" if p_["site"] else "bonus"}" data-pad="{p_["i"]}" d="{poly_d(p_["poly"])}" fill="{c_["base"]}" fill-opacity=".3" '
                     f'stroke="{c_["base"]}" stroke-width="2.2" data-w="3.5" stroke-linejoin="round"/>')
    # the two pasture areas as plain colour fields, with no paddock lines (used where fences are not yet proposed)
    for key_, site_ in (("pasture", True), ("bonus", False)):
        _u = unary_union([p_["poly"] for p_ in PADS if p_["site"] == site_]).buffer(1.5).buffer(-1.5)
        _area_svg += f'<path class="area {"site" if site_ else "bonus"}" d="{poly_d(_u)}" fill="{P[key_]["base"]}" fill-opacity=".3" stroke="{P[key_]["base"]}" stroke-width="2.2" data-w="3.5" stroke-linejoin="round"/>'
paddocks = (f'<g id="paddock-fills">{_pad_svg}</g>' + _fence_art + f'<g id="gates">{gates}</g><g id="pinwheel-labels">{_pw}</g>'
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


land = (f'<g id="pasture-areas">{_area_svg}</g>'
        f'<path d="{poly_d(footprint)}" fill="none" stroke="#fff" stroke-width="7" data-w="7"/>'
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
    # and the 12' x 10' canopy on its own at the pasture edge west of the campus
    _OPEN_AT = {"pens-shed": (1128.8, 338.5), "pasture-canopy": (1094.1, 366.5)}
    def OPEN_SHED(st_):
        cx_, cy_ = (st_["bbox"][0] + st_["bbox"][2]) / 2, (st_["bbox"][1] + st_["bbox"][3]) / 2
        return next((k for k, (x, y) in _OPEN_AT.items() if abs(cx_ - x) < 3 and abs(cy_ - y) < 3), None)
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
        CANOPIES.append({"id": OPEN_SHED(st_), "label": "", "pts": st_["pts"]})
_cp = _oh_pts(1220, 376, 1243, 399)
if len(_cp) >= 4:
    CANOPIES.append({"id": "carport", "label": "Carport", "pts": list(_MP(_cp).minimum_rotated_rectangle.exterior.coords)[:-1]})
# The Red House porches (architect, 2026-10-14), from the survey's overhang lines (BUILDING OH) against the house
# walls (BUILDING), in survey coordinates: the porch along the north-west wall, and the one along the north-east end.
for _id, _q in (("red-house-porch-nw", [(1341.02, 1135.55), (1352.45, 1126.43), (1354.94, 1129.49), (1343.57, 1138.7)]),
                ("red-house-porch-ne", [(1363.58, 1122.5), (1365.74, 1120.76), (1374.26, 1131.29), (1372.1, 1133.03)])):
    CANOPIES.append({"id": _id, "label": "", "pts": [pt(M_SP, T_SP, x, y) for x, y in _q]})
_canopies = ('<g id="canopies" fill="{}" fill-opacity=".9" stroke="{}" stroke-width="1" data-w="1.6" stroke-dasharray="3 2" data-dash="5 3" stroke-linejoin="round">'.format(P["education"]["tint"], P["education"]["base"])
             + "".join(f'<polygon id="{c_["id"]}" points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in c_["pts"])}"/>' for c_ in CANOPIES) + "</g>")
print("canopies:", [(c_["id"], round(Polygon(c_["pts"]).area * (FT_PER_PT / abs(M_FP)) ** 2)) for c_ in CANOPIES], "sf")
_road_area = ""
unit_ft_map = FT_PER_PT / abs(M_FP)
if os.path.exists(_fp) and FENCES.get("road_area"):
    _ra = unary_union([Polygon(g_["outer"], g_["holes"]).buffer(0) for g_ in FENCES["road_area"]])
    # the unsurveyed drives south of the campus, approximated (tools/build_south_roads.py), join the same shape
    _sp = os.path.join(OUT, "data", "south-roads.json")
    if os.path.exists(_sp):
        _south = unary_union([LineString(r_["map"]).buffer(r_["width_ft"] / unit_ft_map / 2, cap_style=2, join_style=1)
                              for r_ in json.load(open(_sp))["roads"]]).intersection(footprint.buffer(2))
        _ra = unary_union([_ra, _south]).buffer(1.2).buffer(-1.2)
    _rd = " ".join("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in ring.coords) + "Z"
                   for g_ in getattr(_ra, "geoms", [_ra]) for ring in [g_.exterior] + list(g_.interiors))
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
# (the diagram-to-map transform M_DP, T_DP is set up earlier, with the fences)

def ag_poly(e):
    pts = e.get("outline") or [[e["x"], e["y"]], [e["x"] + e["w"], e["y"]], [e["x"] + e["w"], e["y"] + e["h"]], [e["x"], e["y"] + e["h"]]]
    return [pt(M_DP, T_DP, px, py) for px, py in pts]


# ---- the new entry apron where the drive meets the lane (Level 1), drawn cleanly on the map
# The barnyard diagram only knows the lane's position roughly, so here the drive is carried on to the lane's surveyed
# near edge (the survey's edge-of-pavement either side of the entry) and given 10' curb returns there. The old
# flared apron and its island, surveyed under it, are covered with ground colour on the plan views.
_apron_patch = ""
_pk = next((e_ for e_ in AG["elements"] if e_["id"] == "parking"), None)
if _pk and FENCES.get("road_area"):
    from shapely.geometry import box as _bx
    from shapely import affinity as _aff
    _inv = lambda x, y: (lambda z: (z.real, z.imag))((complex(x, y) - T_DP) / M_DP)
    _Pm = Polygon([pt(M_DP, T_DP, x, y) for x, y in _pk["outline"]]).buffer(0)
    _dbox = lambda x0, x1: Polygon([pt(M_DP, T_DP, x, y) for x, y in ((x0, -9999), (x1, -9999), (x1, 9999), (x0, 9999))])
    _core = _Pm.intersection(_dbox(-255, -160))
    _rr = list(_core.minimum_rotated_rectangle.exterior.coords)[:4]
    _sides = sorted([(math.hypot(_rr[i + 1 - 4 * (i == 3)][0] - _rr[i][0], _rr[i + 1 - 4 * (i == 3)][1] - _rr[i][1]), i) for i in range(4)])
    _w_half = _sides[0][0] / 2
    _A, _B = (1021.94, 479.5), (1255.77, 591.05)                         # lane's near edge, surveyed, either side of the entry
    _ln = LineString([(_A[0] - (_B[0] - _A[0]), _A[1] - (_B[1] - _A[1])), (_B[0] + (_B[0] - _A[0]), _B[1] + (_B[1] - _A[1]))])
    _site_side = Polygon(list(_ln.coords) + [(_ln.coords[1][0], -9999), (_ln.coords[0][0], -9999)]).buffer(0)
    _c0 = _core.centroid
    _ax = _core.minimum_rotated_rectangle
    _east, _west = pt(M_DP, T_DP, -160, 389), pt(M_DP, T_DP, -400, 389)
    _cl = LineString([_east, _west])
    _strip = _cl.buffer(_w_half, cap_style=2).intersection(_site_side)
    _band = _ln.buffer(8).difference(_site_side).intersection(_cl.buffer(60))
    _r = 10 / (FT_PER_PT / abs(M_FP))
    _apron = unary_union([_strip, _band]).buffer(_r, join_style=1).buffer(-_r, join_style=1).intersection(_site_side).intersection(_cl.buffer(_w_half + 2 * _r))
    _Pn = unary_union([_Pm.difference(_dbox(-9999, -255)), _apron]).buffer(0.05).buffer(-0.05)
    if _Pn.geom_type == "MultiPolygon":
        _Pn = max(_Pn.geoms, key=lambda g: g.area)
    _pk = dict(_pk, outline=[[round(v, 2) for v in _inv(x, y)] for x, y in _Pn.exterior.coords][:-1])
    AG["elements"] = [(_pk if e_["id"] == "parking" else e_) for e_ in AG["elements"]]
    _x_cross = _ln.intersection(_cl)
    _filled = unary_union([Polygon(g_.exterior) for g_ in getattr(_ra, "geoms", [_ra])])
    _old = _filled.buffer(1.2).intersection(_site_side.buffer(-1.6)).intersection(Point(_x_cross.x, _x_cross.y).buffer(40)) if not _x_cross.is_empty else None
    if _old is not None and not _old.is_empty:
        _apron_patch = f'<path d="{" ".join(poly_d(g_) for g_ in getattr(_old, "geoms", [_old]))}" fill="#F2F5EA" stroke="none"/>'
        # the entry culvert runs under this spot: redrawn over the patch, still under the new drive
        _m_ec = re.search(r'<g id="entry-culvert">(.*?)</g>', _infra) if _infra else None
        if _m_ec:
            _apron_patch += f'<g class="infra-copy" display="none">{_m_ec.group(1)}</g>'
    print("entry apron: drive half-width ft", round(_w_half * FT_PER_PT / abs(M_FP), 1), "| return radius ft 10")
by = []
for e in AG["elements"]:
    if e["id"] in ("existing-red-house", "existing-poultry") or e["kind"] == "canopy":
        continue                                  # already on the map as surveyed structures
    use3 = e["use"]
    for k in ("2", "3"):
        use3 = e.get("becomes", {}).get(k, {}).get("use", use3)
    inner = ""
    if e.get("rows") is not None and (e.get("rows") or e.get("stalls_extra")):
        sw, sd = e["stall"]
        inner += '<g fill="#fff" fill-opacity=".55" stroke="{}" stroke-width=".5">'.format(P["circulation"]["base"]) + "".join(
            (f'<rect x="{r[0]}" y="{r[1] + k * sw}" width="{sd}" height="{sw}"/>' if len(r) > 3 else f'<rect x="{r[0] + k * sw}" y="{r[1]}" width="{sw}" height="{sd}"/>')
            for r in e["rows"] for k in range(r[2])) + "</g>"
        inner = inner[:-4] + "".join(f'<polygon points="{" ".join(f"{px},{py}" for px, py in q)}"/>' for q in e.get("stalls_extra", [])) + "</g>"
        isl = e.get("island")
        if e.get("grass"):
            inner += '<polygon points="' + " ".join(f"{px},{py}" for px, py in e["grass"]) + f'" fill="{P["pasture"]["tint"]}" fill-opacity=".6" stroke="{P["pasture"]["base"]}" stroke-width=".6" stroke-dasharray="3 2"/>'
        if e.get("island_poly"):
            # the island is planted ground: it hides the existing drive surveyed under it, then the swale sits inside
            inner += "".join('<polygon points="' + " ".join(f"{px},{py}" for px, py in h_) + '" fill="#F2F5EA" stroke="none"/>' for h_ in e.get("holes", []))
            inner += '<polygon class="bioswale" points="' + " ".join(f"{px},{py}" for px, py in e["island_poly"]) + f'" fill="{P["water"]["tint"]}" stroke="{P["water"]["base"]}" stroke-width=".5"/>'
        elif isl:
            inner += f'<rect x="{isl["x"]}" y="{isl["y"]}" width="{isl["w"]}" height="{isl["h"]}" rx="3" fill="{P["water"]["tint"]}" stroke="{P["water"]["base"]}" stroke-width=".5"/>'
    for z in e.get("zones", []):
        if "poly" in z:
            inner += '<polygon points="' + " ".join(f'{e["x"] + px},{e["y"] + py}' for px, py in z["poly"]) + f'" fill="{P["arena"]["tint"]}" stroke="{P["cattle"]["base"]}" stroke-width=".5"/>'
        else:
            inner += f'<rect x="{e["x"] + z["x"]}" y="{e["y"] + z["y"]}" width="{z["w"]}" height="{z["h"]}" fill="{P["cattle"]["tint"] if z.get("fill") else "none"}" stroke="{P["cattle"]["base"]}" stroke-width=".5"/>'
    shape = ('<path class="shape" fill-rule="evenodd" d="' + " ".join("M" + " L".join(f"{px},{py}" for px, py in r_) + "Z" for r_ in [e["outline"]] + e["holes"]) + '"' if e.get("holes")
             else '<polygon class="shape" points="' + " ".join(f"{px},{py}" for px, py in e["outline"]) + '"' if e.get("outline")
             else f'<rect class="shape" x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}"')
    yard = e["kind"] == "yard"
    walk = e["kind"] == "walk"
    shape += (f' fill="{"none" if yard else "#fff" if walk else P[use3]["tint"]}" stroke="{P[use3]["base"]}" stroke-width="{0.6 if walk else 1.6}"' + (' stroke-dasharray="4 3"' if yard else "") + "/>")
    by.append(f'<g class="by" data-id="{e["id"]}" data-level="{e["level"]}" data-kind="{e["kind"]}" data-use="{e["use"]}" '
              f'data-use2="{e.get("becomes", {}).get("2", {}).get("use", "")}">{shape}{inner}</g>')
barnyard = _apron_patch + f'<g transform="{mat(M_DP, T_DP)}">' + "".join(by) + "</g>"
# Surveyed trees inside the parking lot's swale island are drawn again above the barnyard, so the swale sits behind
# them (the lot's paving is cut out around the island, so nothing else covers them there).
_isl_d = [e_ for e_ in AG["elements"] if e_.get("holes")]
if _isl_d:
    _isl_m = unary_union([Polygon([pt(M_DP, T_DP, x, y) for x, y in h_]) for e_ in _isl_d for h_ in e_["holes"]])
    _isl_trees = [(px, py, s_) for _src, x, y, s_ in trees for px, py in [pt(M_FP, T_FP, x, y)] if _isl_m.contains(Point(px, py))]
    barnyard += (f'<g id="swale-trees" fill="{P["woodland"]["base"]}" fill-opacity="0.7">'
                 + "".join(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{5.2 if s_ > 20 else 3.8}"/>' for px, py, s_ in _isl_trees) + "</g>")
    print("trees in the swale island, drawn over it:", len(_isl_trees))
BY_LABELS = {"cattle-a": "Cattle barn A", "cattle-b": "Cattle barn B", "small-a": "Small animal barn A", "small-b": "Small animal barn B", "feed": "Feed storage", "bedding": "Bedding", "compost": "Compost", "dumpster": "Dumpsters", "holding-5": "Pen 5",
             "arena": "Arena", "parking": "Parking", "handling": "Handling", "horticulture": "Horticulture", "residence": "RV / residence", "holding-1": "Pen 1", "holding-2": "Pen 2", "holding-3": "Pen 3", "holding-4": "Pen 4", "existing-barn": "Existing barn", "existing-pens": "Existing pens",
             "red-house-addition": "Classroom / event"}
by_labels = ""
for e in AG["elements"]:
    if e["id"] in BY_LABELS:
        lx, ly = pt(M_DP, T_DP, e["x"] + e["w"] / 2, e["y"] + e["h"] / 2)
        by_labels += (f'<text data-level="{e["level"]}" x="{lx:.1f}" y="{ly + 1.4:.1f}" text-anchor="middle" font-size="4.2" font-weight="700" fill="{N["ink"]}" '
                      f'stroke="#fff" stroke-width="1.1" paint-order="stroke">{BY_LABELS[e["id"]]}</text>')

# the parking lot's bioswale, labelled on the water slide's plan steps (architect, 2026-10-14); hidden elsewhere
_bsw = ""
for e in AG["elements"]:
    if e.get("island_poly"):
        _bc = Polygon([pt(M_DP, T_DP, x, y) for x, y in e["island_poly"]]).representative_point()
        _bsw = (f'<g id="bioswale-label" display="none" transform="translate({_bc.x:.1f} {_bc.y:.1f})"><g data-fixed="1">'
                f'<text y="5" text-anchor="middle" font-size="16" font-weight="700" fill="{P["water"]["base"]}" stroke="#fff" stroke-width="4" paint-order="stroke">Bioswale</text></g></g>')
# the unfinished barn houses poultry from Level 1 on, at every Level; labelled with the barnyard on the site plan slide
if UNFINISHED_BARN:
    _ubx, _uby = sum(q[0] for q in UNFINISHED_BARN[:-1]) / 4, sum(q[1] for q in UNFINISHED_BARN[:-1]) / 4
    by_labels += (f'<text data-level="1" x="{_ubx:.1f}" y="{_uby + 1.4:.1f}" text-anchor="middle" font-size="4.2" font-weight="700" fill="{N["ink"]}" '
                  f'stroke="#fff" stroke-width="1.1" paint-order="stroke">Poultry</text>')

# fit checks against the survey (presentation frame; reported in feet)
from shapely.geometry import MultiPoint
unit_ft = FT_PER_PT / abs(M_FP)
NAMES = {e["id"]: e["label"] for e in AG["elements"]}
polys = {e["id"]: Polygon(ag_poly(e)) for e in AG["elements"]}
new_ids = [e["id"] for e in AG["elements"] if not e["id"].startswith("existing") and not e.get("context")]
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

# The 1948 aerial (tools/register_aerial_1948.py), clipped to the site and a margin so the web map's search box
# and street labels around it stay out of view.
aerial48 = ""
if "aerial_1948" in reg:
    (_a, _c, _e), (_b, _d, _f) = reg["aerial_1948"]["to_map"]
    _w48, _h48 = reg["aerial_1948"]["image_size"]
    _clip = footprint.buffer(150).simplify(2)
    aerial48 = (f'<clipPath id="clip48"><path d="M{" L".join(f"{x:.0f},{y:.0f}" for x, y in _clip.exterior.coords)}Z"/></clipPath>'
                f'<g clip-path="url(#clip48)"><image href="../source/1948%20Aerial%20of%20historic%20Slough%20Bed.jpg" x="0" y="0" width="{_w48}" height="{_h48}" '
                f'transform="matrix({_a:.8f} {_b:.8f} {_c:.8f} {_d:.8f} {_e:.4f} {_f:.4f})" preserveAspectRatio="none"/></g>')

# where the historical slough bed meets the proposed barnyard (reported on the water site-plan slide)
bed_meta = {}
if os.path.exists(_bp):
    _B = json.load(open(_bp))
    _bedg = unary_union([Polygon(p_["outer"], p_["holes"]).buffer(0) for p_ in _B["parts"]])
    bed_meta = {"acres": _B["acres"], "crosses": [{"name": NAMES[k], "sf": round(polys[k].intersection(_bedg).area * unit_ft ** 2, -1)}
                                                   for k in new_ids if polys[k].intersection(_bedg).area * unit_ft ** 2 > 50]}
    print("slough bed crosses:", bed_meta["crosses"])

# Retention from the architect's markup (tools/build_retention_markup.py): a new pond on the site between the
# historical bed and the lane, and "bonus retention" on the Solid Waste land beyond the parcel line, extending this
# pond and the proposed retention pond south, plus two more ponds past the outfall drive. The County's Solid Waste
# department controls the property and drew the site line somewhat arbitrarily; it is open to IFAS using more of
# its land (hence the bonus pasture), and the same could apply to stormwater. Replaces the earlier wildcard zone,
# which was too far south to use without underground equalization pipes.
_wild_svg, WILD = "", None
if _RM:
    WILD = {"site_acres": round(sum(_RM["site_ponds_acres"][1:]), 1), "bonus_acres": _RM["bonus_acres"], "bonus_ponds_acres": _RM["bonus_ponds_acres"]}
    _sp = [Polygon(q) for q in _RM["site_ponds"][1:]]; _bp = [Polygon(q) for q in _RM["bonus_ponds"]]
    _small = lambda g, l1, l2: (f'<g transform="translate({g.representative_point().x:.0f} {g.representative_point().y:.0f})"><g data-fixed="1">'
                               f'<text y="-3" text-anchor="middle" font-size="14" font-weight="700" fill="{P["water"]["base"]}" stroke="#fff" stroke-width="3.5" paint-order="stroke">{l1}</text>'
                               f'<text y="13" text-anchor="middle" font-size="13" font-weight="700" fill="{P["water"]["base"]}" stroke="#fff" stroke-width="3.5" paint-order="stroke">{l2}</text></g></g>')
    # the second site pond belongs with the site retention pond (shown on every plan step); bonus ponds only with the
    # compensation step
    _wild_svg = ('<g id="site-retention" display="none">'
                 + "".join(f'<path d="{poly_d(g_)}" fill="{P["water"]["tint"]}" stroke="{P["water"]["base"]}" stroke-width="2" data-w="2.5" stroke-dasharray="8 5" data-dash="8 5"/>' for g_ in _sp)
                 + "".join(_small(g_, "Site retention pond", f"{a_} ac") for g_, a_ in zip(_sp, _RM["site_ponds_acres"][1:]))
                 + "</g>"
                 + ("" if MAIN_PARCEL_ONLY else '<g id="wildcard" display="none">'      # bonus retention: Solid Waste land
                    + "".join(f'<path d="{poly_d(g_)}" fill="{P["water"]["base"]}" fill-opacity=".14" stroke="{P["water"]["base"]}" stroke-width="2.5" data-w="3" stroke-dasharray="2 6" data-dash="2 7" stroke-linecap="round"/>' for g_ in _bp)
                    + "".join(_small(g_, "Bonus retention", f"{a_} ac") for g_, a_ in zip(_bp, _RM["bonus_ponds_acres"]))
                    + "</g>"))
    print("retention markup: site ponds ac", _RM["site_ponds_acres"], "| bonus ponds ac", _RM["bonus_ponds_acres"])

# ---- main parcel only (siteframe.MAIN_PARCEL_ONLY): the side of parcel line pl-04 the campus is on
MAIN, MAIN_SIDE = None, None
_pl04 = [r_["map"] for r_ in (FENCES.get("property_lines", []) if os.path.exists(_fp) else []) if r_["id"] == "pl-04"]
if MAIN_PARCEL_ONLY and _pl04:
    (_ax, _ay), (_bx, _by) = _pl04[0][0], _pl04[0][-1]
    _L = math.hypot(_bx - _ax, _by - _ay); _ux, _uy = (_bx - _ax) / _L, (_by - _ay) / _L
    _pa, _pb = (_ax - _ux * 6000, _ay - _uy * 6000), (_bx + _ux * 6000, _by + _uy * 6000)
    _nx, _ny = -_uy, _ux                                   # a normal; flip it to the campus side
    if (rh[0] - _ax) * _nx + (rh[1] - _ay) * _ny < 0:
        _nx, _ny = -_nx, -_ny
    MAIN_SIDE = Polygon([_pa, _pb, (_pb[0] + _nx * 9000, _pb[1] + _ny * 9000), (_pa[0] + _nx * 9000, _pa[1] + _ny * 9000)])
    MAIN = footprint.intersection(MAIN_SIDE).buffer(0)
    MAIN = max(getattr(MAIN, "geoms", [MAIN]), key=lambda g: g.area)
    print("main parcel only: acres", round(MAIN.area * (FT_PER_PT / abs(M_FP)) ** 2 / 43560, 1), "of", round(footprint.area * (FT_PER_PT / abs(M_FP)) ** 2 / 43560, 1))
_shown = MAIN if MAIN is not None else footprint           # the site as drawn (ground, veil)
_clip = ' clip-path="url(#main-side)"' if MAIN is not None else ""
_ckw = {"clip_path": "url(#main-side)"} if MAIN is not None else {}
W, H = x1 - x0, y1 - y0
font = "font-family=\"'Avenir Next','Segoe UI','Helvetica Neue',Arial,sans-serif\""
if AD:
    # label the redrawn slough about a third of the way along it, turned to follow the channel
    # label the redrawn slough at the middle of its longest straight reach (beside the site pasture), turned to
    # follow the channel but never upside down, and set on the off-site bank where the paper is clear
    _sc = AD["slough_centre"]
    _k = max(range(len(_sc) - 1), key=lambda i: math.hypot(_sc[i + 1][0] - _sc[i][0], _sc[i + 1][1] - _sc[i][1]))
    _lx, _ly = (_sc[_k][0] + _sc[_k + 1][0]) / 2, (_sc[_k][1] + _sc[_k + 1][1]) / 2
    _ang = math.degrees(math.atan2(_sc[_k + 1][1] - _sc[_k][1], _sc[_k + 1][0] - _sc[_k][0]))
    _ang = (_ang + 90) % 180 - 90
    _nx, _ny = -math.sin(math.radians(_ang)), math.cos(math.radians(_ang))          # the label's "down"
    _dy = 40 if not footprint.contains(Point(_lx + _nx * 30, _ly + _ny * 30)) else -18
    slough_lbl = (f'<g transform="translate({_lx:.0f} {_ly:.0f}) rotate({_ang:.1f})"><text data-fixed="1" y="{_dy}" text-anchor="middle" font-size="30" font-style="italic" font-weight="600" '
                  f'fill="{P["water"]["base"]}" stroke="#fff" stroke-width="5" paint-order="stroke">Cowpen Slough</text></g>')
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
       f'viewBox="{x0} {y0} {W} {H}" {font}>'
       f'<title>Clark Farm site layers (north to the left)</title>'
       f'<defs><clipPath id="frame"><rect x="{x0}" y="{y0}" width="{W}" height="{H}"/></clipPath>'
       + (f'<clipPath id="main-side"><path d="{poly_d(MAIN_SIDE.intersection(box(x0 - 4000, y0 - 4000, x1 + 4000, y1 + 4000)))}"/></clipPath>' if MAIN is not None else "")
       + '</defs>'
       f'<rect x="{x0 - 4000}" y="{y0 - 4000}" width="{W + 8000}" height="{H + 8000}" fill="{N["paper"]}"/>'
       f'<g id="map-content">'
       + layer("aerial", "Aerial (Sarasota County PA)", aerial)
       + (layer("aerial1948", "1948 aerial (Sarasota County PA)", aerial48, display="none") if aerial48 else "")
       + layer("ground", "Site ground (used when the aerial is off)", f'<path d="{poly_d(_shown)}" fill="#F2F5EA" stroke="{N["ink"]}" stroke-width="2.5" data-w="2.5"/>')
       + layer("veil", "Outside the site (veil)", f'<path d="{poly_d(box(x0 - 4000, y0 - 4000, x1 + 4000, y1 + 4000).difference(_shown))}" fill="{N["paper"]}" fill-opacity="{0.8 if MAIN is not None else 0.72}"/>'
               f'<path d="{poly_d(_shown)}" fill="none" stroke="{N["paper"]}" stroke-width="3"/>')
       + (layer("canopy", "Tree canopy (from the aerial trace)", f'<path d="{AD["canopy"]}" fill="{P["woodland"]["base"]}" fill-opacity=".3" fill-rule="evenodd"/>', **_ckw) if AD else "")
       # the trace's drives are not drawn: they are fragmentary and fall inside pasture enclosures (architect, 2026-10-13)
       + (layer("property", "Surveyed property lines (fencing plan)", f'<g fill="none" stroke="{N["ink"]}" stroke-width="1.6" data-w="1.6" stroke-dasharray="10 4 2 4" data-dash="10 4 2 4" stroke-opacity=".75">'
                + "".join(f'<polyline id="{r_["id"]}" points="{" ".join(f"{x},{y}" for x, y in r_["map"])}"/>' for r_ in FENCES.get("property_lines", [])) + "</g>", **_ckw) if os.path.exists(_fp) else "")
       + layer("soils", "Soils by drainage class", "".join(soil_layer), opacity="0.82", **_ckw)
       + layer("water", "Water: slough, ponds, flood zone line", water)
       + layer("trees", "Existing trees and woodland edge", trees_layer, **_ckw)
       + layer("land", "The land: site and bonus pasture areas", land, **_ckw)
       + layer("paddocks", "Proposed paddocks", paddocks, **_ckw)
       + layer("campus", "Campus", campus, **_ckw)
       + layer("barnyard", "Proposed barnyard (Level 3 shown), to scale", barnyard + f'<g id="barnyard-labels">{by_labels}</g>')
       + layer("labels", "Labels", slough_lbl + _infra_lbl + _wild_svg + _bsw)
       + "</g></svg>")

# Civil's expanded retention (2026-10-14) was sketched on Option A and runs under the Option B turnouts. Refitted to
# the plan as a site retention option (architect's markup on the water slide, 2026-10-14): a west pond in the
# paddock between fence-19, the campus fence and the old bed, and a south pond between the small animal turnout's
# fence, the campus's east fence and the old bed. Each is the open ground in its zone, kept 4 units (about 11 ft)
# clear of every new element, fence line and top of bank, then simplified to a few straight sides with corners
# rounded to a 4-unit radius: a clean diagrammatic shape, not civil's sketch line. Not designed or sized.
SRO_ACRES = None
if CIVIL:
    _block = unary_union([unary_union([polys[k].buffer(0) for k in new_ids if k not in ("parking", "horticulture", "residence")]),
                          unary_union([LineString(r_["map"]) for r_ in FENCES["runs"]]) if os.path.exists(_fp) else Polygon(),
                          unary_union([Polygon(p_["outer"]).buffer(0) for p_ in _BJ["parts"]]) if os.path.exists(_bp_bed) else Polygon()]).buffer(4)
    def _pond(region, seed, tol=2.5, r=4):
        a_ = Polygon(region).difference(_block)
        g_ = next(h for h in getattr(a_, "geoms", [a_]) if h.contains(Point(seed))).simplify(tol)
        return g_.buffer(r).buffer(-r).buffer(-r).buffer(r).simplify(0.2)           # round concave, then convex corners
    _sro = [_pond([(1015, 315), (1075, 315), (1055, 400), (1015, 400)], (1040, 360)),
            _pond([(1040, 398), (1100, 398), (1170, 440), (1150, 500), (1040, 470)], (1100, 460))]
    SRO_ACRES = [round(g.area * unit_ft ** 2 / 43560, 1) for g in _sro]
    _sro_svg = ("".join(f'<path d="{poly_d(g)}" fill="{P["water"]["base"]}" fill-opacity=".45" stroke="{P["water"]["base"]}" stroke-width="1.5" data-w="2"/>' for g in _sro)
                + "".join(_lbl(g.representative_point().x, g.representative_point().y, "Site retention option", f"{a_} ac", P["water"]["base"]) for g, a_ in zip(_sro, SRO_ACRES)))
    svg = svg.replace("<!--SITE-RET-OPTION-->", _sro_svg)
    print("site retention option acres (civil's sketch, refitted):", SRO_ACRES)
open(os.path.join(OUT, "site-layers.svg"), "w").write(svg)
os.makedirs(os.path.join(SLIDES, "data"), exist_ok=True)
_cb = [c for st_ in (EDITS["structures"] if EDITS else []) for c in st_["pts"]] + [list(q) for q in UNFINISHED_BARN]
CAMPUS_BOX = [min(c[0] for c in _cb), min(c[1] for c in _cb), max(c[0] for c in _cb), max(c[1] for c in _cb)] if _cb else [rh[0] - 80, rh[1] - 80, rh[0] + 80, rh[1] + 80]
# main parcel only: the site's figures (acres, soils, canopy) are counted on the front parcel
_main_view, _site_ac, _canopy_ac = VIEW, footprint.area * ft2_per_pt2 / 43560, (AD["canopy_acres"] if AD else None)
if MAIN is not None:
    _bx0, _by0, _bx1, _by1 = MAIN.buffer(60).bounds
    _main_view = [round(_bx0, 1), round(_by0, 1), round(_bx1, 1), round(_by1, 1)]
    _site_ac = MAIN.area * ft2_per_pt2 / 43560
    for k_, sj_ in zip(units.keys(), soil_json):
        sj_["acres_in_map"] = round(sp_shape(soil_polys[k_], M_SP, T_SP).intersection(MAIN).area * ft2_per_pt2 / 43560, 1)
    if AD:
        _rings = [[(float(a_), float(b_)) for a_, b_ in re.findall(r"(-?[\d.]+)[ ,](-?[\d.]+)", seg)] for seg in re.split(r"(?=M)", AD["canopy"]) if seg.strip()]
        _can = Polygon()
        for r_ in _rings:
            if len(r_) >= 3:
                _can = _can.symmetric_difference(Polygon(r_).buffer(0))         # evenodd, as drawn
        _canopy_ac = round(_can.intersection(MAIN).area * ft2_per_pt2 / 43560, 1)
    if bed_meta:
        bed_meta["acres"] = round(_bedg.intersection(MAIN).area * ft2_per_pt2 / 43560, 1)
    print("main parcel figures: acres", round(_site_ac, 1), "| canopy ac", _canopy_ac, "| view", _main_view)
meta = {"canopy_acres": _canopy_ac, "main_parcel_only": MAIN is not None, "campus_box": [round(v, 1) for v in CAMPUS_BOX], "barnyard": {"checks": checks, "diagram_to_presentation": {"m": [M_DP.real, M_DP.imag], "t": [T_DP.real, T_DP.imag]},
                     "bearing_deg": math.degrees(cmath.phase(M_DP / M_TP))},
        "view": _main_view, "site_acres_footprint": round(_site_ac, 1), "site_acres_footprint_previous": round(footprint_auto.area * ft2_per_pt2 / 43560, 1), "red_house": [round(rh[0], 1), round(rh[1], 1)], "trees": len(trees),
        "soils": soil_json, "ft_per_unit": FT_PER_PT, "slough_bed": bed_meta, "compensation_acres": COMP_ACRES, "wildcard": WILD, "civil": {**{k: CIVIL[k] for k in ("option1_acres", "option2_acres", "retention_expansion_acres")}, "site_retention_option_acres": SRO_ACRES} if CIVIL else None, "retention_acres": RET_ACRES, "infrastructure": INFRA}
with open(os.path.join(SLIDES, "data", "site-map.js"), "w") as fh:
    fh.write("// Generated by tools/build_site_map.py. Do not edit by hand.\n")
    fh.write("window.SITE_MAP = " + json.dumps({"svg": svg, **meta}) + ";\n")
json.dump(soil_json, open(os.path.join(OUT, "data", "soils.json"), "w"), indent=2)
print("soil units:", [(s["codes"], s["drainage"], s["acres_in_map"]) for s in soil_json])
print("barnyard fit:", checks)
print("site boundary acres:", round(footprint.area * ft2_per_pt2 / 43560, 1), "(fence-derived:", round(footprint_auto.area * ft2_per_pt2 / 43560, 1), ")")
print("slough labels:", sl[:2], "red house:", rh, "svg KB:", len(svg) // 1024)
