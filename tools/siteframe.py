"""Shared site geometry for every map graphic, in one frame.

Base frame: the fencing sheet (PDF points). The presentation frame turns it 180 degrees so north
points LEFT and the campus entry is approached from the bottom. This module loads the CAD layers,
classifies the fencing-sheet linework, extracts surveyed trees, and reads paddock labels and canopy
classes. Sheet transforms come from tools/registration.json (tools/register.py).
"""
import json, os, sys
import numpy as np
import openpyxl
import pymupdf
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import cadpdf
from trees import tree_marks

SRC = os.path.join(ROOT, "source")
# Revised fencing plan of 2026-10-13: same sheet frame as the first one, with the surveyed property lines added
# (layer SECTION LINE) and the 7.7 and 2.5 ac bonus paddocks merged into one of 10.2 ac.
FENCE = os.path.join(SRC, "Revised fencing plan with PL.pdf")
FENCE_V1 = os.path.join(SRC, "Clark Farm Proposed Fencing Plan.pdf")
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
canopy.setdefault(10.2, ("Bonus Pasture", "75% dense woods"))      # 7.7 ac dense woods + 2.5 ac open, merged on the revised plan

labels = []
page = pymupdf.open(FENCE)[0]
for b in page.get_text("dict")["blocks"]:
    for l in b.get("lines", []):
        t = "".join(s["text"] for s in l["spans"]).strip()
        if t.endswith(" AC") and t not in ("45.1 AC", "54.5 AC"):
            x0, y0, x1, y1 = l["bbox"]
            labels.append((float(t.split()[0]), (x0 + x1) / 2, (y0 + y1) / 2))


# ---------------------------------------------------------------- presentation frame (north left)
M_FP, T_FP = -1, complex(2 * CX, 2 * CY)                      # fence -> presentation
M_SP, T_SP = M_FP * M_SF, M_FP * T_SF + T_FP                  # survey -> presentation
M_TP, T_TP = M_FP * M_TF, M_FP * T_TF + T_FP                  # study plan -> presentation
M_SA, T_SA = cz(reg["survey_to_aerial"]["m"]), cz(reg["survey_to_aerial"]["t"])
M_AP = M_SP / M_SA                                            # aerial px -> presentation
T_AP = T_SP - M_SP * T_SA / M_SA
# Aerial placement as an SVG matrix (aerial px -> map). Prefer the affine fit to the surveyed property lines
# (tools/register_aerial.py); otherwise the survey-based scale-and-rotate registration above.
def aerial_matrix(scale=1.0):
    """SVG transform for the aerial (scale=1) or for artwork drawn at 1/scale of its pixels (the trace: scale=2)."""
    if "map_to_aerial_affine" in reg:
        (a, c, e), (b, d, f) = reg["map_to_aerial_affine"]["aerial_to_map"]
        return f"matrix({a * scale:.8f} {b * scale:.8f} {c * scale:.8f} {d * scale:.8f} {e:.4f} {f:.4f})"
    return mat(M_AP * scale, T_AP)
AERIAL = os.path.join(SRC, "Site Aerial from SCPA.jpg")
AERIAL_SIZE = tuple(reg["survey_to_aerial"]["image_size"])
