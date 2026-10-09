"""Build drawings/fencing-plan-trees.svg: the proposed pasture fencing plan with existing trees.

Sources (all in source/):
  Clark Farm Proposed Fencing Plan.pdf   fence lines, ponds, drive, acreage labels (base frame)
  Clark Farm Study Plan-A0.1 (3)1.pdf    surveyed trees around the campus (most detailed)
  Survey + Soils Map Info.pdf            surveyed trees outside the study-plan sheet, tree line,
                                         existing building footprints
  Clark_Farm_Pasture_Calculations.xlsx   canopy class per paddock (labels)
Colors come from design/palette.json. Sheet-to-sheet transforms come from tools/registration.json
(run tools/register.py to regenerate). Output SVG has one named layer per content type, so it opens
with editable layers in Illustrator or Inkscape. Also writes drawings/data/trees.csv.

Run:  python tools/build_fencing_trees.py   (needs pymupdf, numpy, scipy, openpyxl)
"""
import csv, json, os, sys
import numpy as np
import openpyxl
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import cadpdf
from trees import tree_marks

SRC = os.path.join(ROOT, "source")
FENCE = os.path.join(SRC, "Clark Farm Proposed Fencing Plan.pdf")
STUDY = os.path.join(SRC, "Clark Farm Study Plan-A0.1 (3)1.pdf")
SURVEY = os.path.join(SRC, "Survey + Soils Map Info.pdf")
XLSX = os.path.join(SRC, "Clark_Farm_Pasture_Calculations.xlsx")
OUT = os.path.join(ROOT, "drawings")

pal = json.load(open(os.path.join(ROOT, "design", "palette.json")))
P = {k: v for k, v in pal["program"].items()}
N = pal["neutral"]
reg = json.load(open(os.path.join(HERE, "registration.json")))
cz = lambda v: complex(*v)
M_SF, T_SF = cz(reg["survey_to_fence"]["m"]), cz(reg["survey_to_fence"]["t"])
M_SS, T_SS = cz(reg["survey_to_study"]["m"]), cz(reg["survey_to_study"]["t"])
M_TF = M_SF / M_SS                      # study -> fence
T_TF = T_SF - M_SF * T_SS / M_SS
FT_PER_PT = reg["fence_ft_per_pt"]

VIEW = (40, 110, 2400, 1610)            # crop of the fencing sheet (PDF points)
ARROW_BOXES = [(700, 300, 1400, 700), (1000, 560, 1300, 1070)]  # SITE/BONUS arrow graphic (replaced by legend)
WATER_BOXES = [(225, 215, 350, 335),    # 13.0 AC pond
               (1150, 1150, 1275, 1290),  # retention area beside campus (in the 2.1 AC paddock)
               (1700, 1350, 1800, 1420)]  # existing pond in the 12.4 AC paddock
STUDY_SHEET = (530, 32, 2372, 1697)     # drawing area of the study-plan sheet (its own coords)
# Presentation orientation: north to the LEFT, so the campus entry is approached from the bottom.
# On the fencing sheet survey north points to +x, so every map layer is turned 180 degrees about the
# view centre. Text (tags, legend) is placed at rotated positions but stays upright.
CX, CY = (VIEW[0] + VIEW[2]) / 2, (VIEW[1] + VIEW[3]) / 2
ROT = f"rotate(180 {CX} {CY})"
rot = lambda x, y: (2 * CX - x, 2 * CY - y)


def inside(r, box):
    x0, y0, x1, y1 = box
    return r.x0 >= x0 and r.y0 >= y0 and r.x1 <= x1 and r.y1 <= y1


def mat(m, t):
    return f"matrix({m.real:.6f} {m.imag:.6f} {-m.imag:.6f} {m.real:.6f} {t.real:.3f} {t.imag:.3f})"


def paths(ds):
    return "".join(f'<path d="{cadpdf.path_d(d)}"/>' for d in ds if cadpdf.path_d(d))


def layer(id_, label, body, transform=None, **attrs):
    a = " ".join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    if transform:
        a += f' transform="{transform}"'
    return (f'<g id="{id_}" inkscape:groupmode="layer" inkscape:label="{label}" {a}>{body}</g>')


# ---------------------------------------------------------------- fencing sheet content
fg = cadpdf.export(FENCE, ["FENCE", "(none)", "P-BELOW-LIGHT", "P-WALL"])
fence_ds, water_ds, drive_ds, bldg_ds = [], [], [], []
for L, ds in fg.items():
    for d in ds:
        r = d["rect"]
        if any(inside(r, b) for b in ARROW_BOXES):
            continue
        if L == "P-WALL":
            bldg_ds.append(d)
        n, ln = len(d["items"]), max(r.width, r.height)
        dash = n == 1 and 14 < ln < 21
        if L != "FENCE" and not dash and any(inside(r, b) for b in WATER_BOXES):
            water_ds.append(d)
        elif L in ("(none)", "P-BELOW-LIGHT") and not dash and ln >= 25:
            drive_ds.append(d)          # solid polylines: drives, loop road, solid site edges
        else:
            fence_ds.append(d)          # fence dashes, gate and corner marks

# ---------------------------------------------------------------- trees
def to_fence(x, y, m, t):
    z = m * complex(x, y) + t
    return z.real, z.imag

trees = []
T_st, _ = tree_marks(STUDY)
for x, y, s, n in T_st:
    fx, fy = to_fence(x, y, M_TF, T_TF)
    trees.append(("study plan A0.2", fx, fy, s * abs(M_TF) * FT_PER_PT))
T_sv, _ = tree_marks(SURVEY, split_parts=15)
for x, y, s, n in T_sv:
    sx, sy = to_fence(x, y, M_SS, T_SS)          # where it falls on the study sheet
    x0, y0, x1, y1 = STUDY_SHEET
    if x0 <= sx <= x1 and y0 <= sy <= y1:
        continue                                  # already shown by the study plan
    fx, fy = to_fence(x, y, M_SF, T_SF)
    trees.append(("survey A0.1", fx, fy, s * abs(M_SF) * FT_PER_PT))

os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
with open(os.path.join(OUT, "data", "trees.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["source_sheet", "x_pt_fencing_sheet", "y_pt_fencing_sheet", "symbol_size_ft"])
    for src, x, y, s in trees:
        w.writerow([src, f"{x:.2f}", f"{y:.2f}", f"{s:.1f}"])

sv = cadpdf.export(SURVEY, ["TREE LINE", "BUILDING"])

# ---------------------------------------------------------------- paddock labels + canopy class
wb = openpyxl.load_workbook(XLSX)
canopy = {}
for row in wb["Paddock Detail"].iter_rows(min_row=5, max_row=20, values_only=True):
    area, ac, dense, light = row[0], row[1], row[2] or 0, row[3] or 0
    if area is None or ac is None:
        continue
    if dense >= 0.99:
        cls = "dense woods"
    elif dense > 0:
        cls = f"{round(dense * 100)}% dense woods"
    elif light > 0:
        cls = f"~{round(light * 100)}% pine / palm"
    else:
        cls = "open"
    canopy[round(float(ac), 1)] = (area, cls)

labels = []
page = pymupdf.open(FENCE)[0]
for b in page.get_text("dict")["blocks"]:
    for l in b.get("lines", []):
        t = "".join(s["text"] for s in l["spans"]).strip()
        if t.endswith(" AC") and t not in ("45.1 AC", "54.5 AC"):
            x0, y0, x1, y1 = l["bbox"]
            labels.append((float(t.split()[0]), (x0 + x1) / 2, (y0 + y1) / 2))


def tag(ac, x, y):
    area, cls = canopy.get(ac, ("?", "?"))
    key = "pasture" if area == "Site Pasture" else "bonus"
    c = P[key]
    w = 92
    wooded = "woods" in cls
    return (f'<g class="tag {key}" transform="translate({x:.1f} {y:.1f})">'
            f'<rect x="{-w/2}" y="-19" width="{w}" height="38" rx="5" fill="{c["tint"]}" stroke="{c["base"]}" stroke-width="1.6"/>'
            f'<text y="-1" text-anchor="middle" font-size="17" font-weight="700" fill="{N["ink"]}">{ac:g} ac</text>'
            f'<text y="13" text-anchor="middle" font-size="11" fill="{P["woodland"]["base"] if wooded else N["muted"]}">{cls}</text></g>')

# ---------------------------------------------------------------- assemble
x0, y0, x1, y1 = VIEW
W, H = x1 - x0, y1 - y0
font = "font-family=\"'Source Sans 3','Helvetica Neue',Arial,sans-serif\""
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
       f'viewBox="{x0} {y0} {W} {H}" width="{W}" height="{H}" {font}>',
       f'<title>Clark Farm: proposed pasture fencing with existing trees</title>',
       f'<rect id="paper" x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{N["paper"]}"/>']

svg.append(layer("woodland-edge", "Woodland edge (survey tree line)",
                 f'<g transform="{mat(M_SF, T_SF)}" fill="none" stroke="{P["woodland"]["base"]}" '
                 f'stroke-width="{2.2/abs(M_SF):.3f}" stroke-dasharray="{6/abs(M_SF):.2f} {3/abs(M_SF):.2f}" '
                 f'stroke-linecap="round">{paths(sv.get("TREE LINE", []))}</g>', ROT))
svg.append(layer("water", "Water / stormwater",
                 f'<g fill="{P["water"]["tint"]}" stroke="{P["water"]["base"]}" stroke-width="1.4">{paths(water_ds)}</g>', ROT))
svg.append(layer("drive", "Drives",
                 f'<g fill="none" stroke="{P["circulation"]["base"]}" stroke-width="2.4" stroke-linejoin="round">{paths(drive_ds)}</g>', ROT))
svg.append(layer("fence", "Proposed pasture fencing",
                 f'<g fill="none" stroke="{N["ink"]}" stroke-width="1.6" stroke-linecap="round">{paths(fence_ds)}</g>', ROT))
svg.append(layer("buildings", "Existing structures",
                 f'<g fill="{P["circulation"]["tint"]}" stroke="{P["circulation"]["base"]}" stroke-width="1">{paths(bldg_ds)}</g>'
                 f'<g transform="{mat(M_SF, T_SF)}" fill="{P["circulation"]["tint"]}" stroke="{P["circulation"]["base"]}" '
                 f'stroke-width="{0.8/abs(M_SF):.3f}">{paths(sv.get("BUILDING", []))}</g>', ROT))

tree_svg = []
for src, x, y, s in trees:
    r = 5.2 if s > 20 else 3.6
    tree_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>')
svg.append(layer("trees", "Existing trees (surveyed)",
                 f'<g fill="{P["woodland"]["base"]}" fill-opacity="0.78" stroke="{P["woodland"]["base"]}" stroke-width="0.6">{"".join(tree_svg)}</g>', ROT))

svg.append(layer("labels", "Paddock labels", "".join(tag(ac, *rot(x, y)) for ac, x, y in labels) +
                 f'<text x="1095" y="292" text-anchor="middle" font-size="17" font-weight="700" letter-spacing="2" '
                 f'fill="{P["cattle"]["base"]}">CAMPUS</text>'))

# legend / title block in the empty lower-left of the (rotated) sheet
lx, ly = 110, 905
site_ac = sum(a for a, (g, _) in canopy.items() if g == "Site Pasture")
bonus_ac = sum(a for a, (g, _) in canopy.items() if g == "Bonus Pasture")
bar_ft = 500
bar_pt = bar_ft / FT_PER_PT
leg = [f'<text x="{lx}" y="{ly}" font-size="34" font-weight="700" fill="{N["ink"]}">Pasture Fencing &amp; Existing Trees</text>',
       f'<text x="{lx}" y="{ly+30}" font-size="16" fill="{N["muted"]}">Clark Farm · Agriculture Education Center · stakeholder review draft</text>']
rows = [("swatch", P["pasture"], f"Site pasture · Levels 1–3 · {site_ac:.1f} ac"),
        ("swatch", P["bonus"], f"Bonus pasture · Level 3 · {bonus_ac:.1f} ac"),
        ("tree", P["woodland"], f"Existing tree, surveyed ({len(trees)} shown)"),
        ("edge", P["woodland"], "Edge of wooded area (survey tree line)"),
        ("fence", None, "Proposed pasture fence"),
        ("water", P["water"], "Pond / retention area"),
        ("drive", P["circulation"], "Drive / solid site edge")]
yy = ly + 72
for kind, c, text in rows:
    if kind == "swatch":
        leg.append(f'<rect x="{lx}" y="{yy-13}" width="34" height="18" rx="4" fill="{c["tint"]}" stroke="{c["base"]}" stroke-width="1.6"/>')
    elif kind == "tree":
        leg.append(f'<circle cx="{lx+17}" cy="{yy-4}" r="5.2" fill="{c["base"]}" fill-opacity="0.78"/>')
    elif kind == "edge":
        leg.append(f'<line x1="{lx}" y1="{yy-4}" x2="{lx+34}" y2="{yy-4}" stroke="{c["base"]}" stroke-width="2.2" stroke-dasharray="6 3"/>')
    elif kind == "fence":
        leg.append(f'<line x1="{lx}" y1="{yy-4}" x2="{lx+34}" y2="{yy-4}" stroke="{N["ink"]}" stroke-width="1.6" stroke-dasharray="14 6"/>')
    elif kind == "water":
        leg.append(f'<rect x="{lx}" y="{yy-13}" width="34" height="18" rx="7" fill="{c["tint"]}" stroke="{c["base"]}" stroke-width="1.4"/>')
    elif kind == "drive":
        leg.append(f'<line x1="{lx}" y1="{yy-4}" x2="{lx+34}" y2="{yy-4}" stroke="{c["base"]}" stroke-width="2.4"/>')
    leg.append(f'<text x="{lx+48}" y="{yy+1}" font-size="16" fill="{N["ink"]}">{text}</text>')
    yy += 30
yy += 14
leg.append(f'<g transform="translate({lx} {yy})"><rect width="{bar_pt/2:.1f}" height="7" fill="{N["ink"]}"/>'
           f'<rect x="{bar_pt/2:.1f}" width="{bar_pt/2:.1f}" height="7" fill="none" stroke="{N["ink"]}" stroke-width="1"/>'
           f'<text y="26" font-size="13" fill="{N["muted"]}">0</text>'
           f'<text x="{bar_pt/2:.1f}" y="26" font-size="13" text-anchor="middle" fill="{N["muted"]}">250</text>'
           f'<text x="{bar_pt:.1f}" y="26" font-size="13" text-anchor="middle" fill="{N["muted"]}">500 ft</text></g>')
# north arrow: survey north points left in this orientation
leg.append(f'<g transform="translate({lx + bar_pt + 90:.1f} {yy + 4})"><path d="M-22 0 L10 -11 L4 0 L10 11 Z" fill="{N["ink"]}"/>'
           f'<text x="24" y="6" font-size="17" font-weight="700" fill="{N["ink"]}">N</text></g>')
yy += 58
notes = ["Trees: Seibert study plan A0.2 (campus) and survey A0.1 (rest of parcel), overlaid by matching",
         "the CAD sheets (see tools/registration.json). Symbols are schematic, not canopy to scale.",
         "Bonus pasture woodland was not part of the tree survey; canopy notes come from the pasture worksheet.",
         "Scale calibrated to paddock acreages, approx. 1 in = 186 ft on the 36x24 sheet."]
for t in notes:
    leg.append(f'<text x="{lx}" y="{yy}" font-size="12.5" fill="{N["muted"]}">{t}</text>')
    yy += 18
svg.append(layer("legend", "Title and legend", "".join(leg)))
svg.append("</svg>")

os.makedirs(OUT, exist_ok=True)
out_svg = os.path.join(OUT, "fencing-plan-trees.svg")
open(out_svg, "w").write("\n".join(svg))
pix = pymupdf.open(out_svg)[0].get_pixmap(dpi=96)
pix.save(os.path.join(OUT, "fencing-plan-trees.png"))
print(f"trees: {len(trees)} ({sum(1 for t in trees if t[0].startswith('study'))} study plan, "
      f"{sum(1 for t in trees if t[0].startswith('survey'))} survey); labels: {len(labels)}; wrote {out_svg}")
