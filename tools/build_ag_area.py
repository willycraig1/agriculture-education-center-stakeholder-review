"""Build the primary ag-area diagram: a to-scale layout of the barns, by Level and by use.

This is a diagram, not a survey drawing. Units are feet, drawn square to the existing barn (which sits
about 17 degrees off true north, measured from the study plan). The existing barn is the anchor in the
bottom-right corner; everything new is placed from it using the dimensions below.

Given by the architect:
  cattle barn       14 pens = 2 rows of 7 x (12' x 24') on a 14' aisle  ->  84' x 62'; two barns in a run
  small animal barn 36' wide, same length as the cattle barn (84'); two barns in a run
  arena             50' wide, one barn module long (84'), between the runs
  feed storage      between the runs, next to the parking
  existing barn     80.4' wide with 7 existing 12' x 24' cattle pens on its north side (survey)
Assumed here (flagged "assumed" in the data, to confirm):
  gap between the two barns of a run, lanes between runs and the centre strip, feed storage size,
  small-animal pen layout, turnout yard depth, parking outline, handling area location, and the
  Level at which the feed storage and each second barn are built.

Writes
  slides/data/ag-area.js          elements for slides/ag-area.html
  drawings/ag-area-diagram.svg    editable master (Level 3 state, one layer per Level)

Run:  python tools/build_ag_area.py
"""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
pal = json.load(open(os.path.join(ROOT, "design", "palette.json")))
P, N = pal["program"], pal["neutral"]

# ---------------------------------------------------------------- dimensions (feet)
PEN_W, PEN_D, AISLE = 12, 24, 14
MOD = 7 * PEN_W                       # 84' barn module length
CATTLE_W = 2 * PEN_D + AISLE          # 62'
SMALL_W = 36
ARENA_W = 50
SA_PEN_W, SA_PEN_D = 6, 10            # small-animal pen module
SA_AISLE = SMALL_W - 2 * SA_PEN_D     # 16' aisle (assumed layout)
EX_W, EX_D = 80.4, 50                 # existing barn (depth approximate)
# assumed
LANE = 24                             # between each run and the centre strip
BARN_GAP = 20                         # between the two barns of a run
YARD = 24                             # existing pens to the first new barns
STORE_D = 40                          # feed storage depth (50' wide strip)
TURNOUT = 48                          # turnout yard depth beside each run

# ---------------------------------------------------------------- layout (x right, y up from the south edge)
x_small = 0
x_mid = x_small + SMALL_W + LANE
x_cattle = x_mid + ARENA_W + LANE
RIGHT = x_cattle + CATTLE_W           # east edge, shared with the existing barn
y_ex_pens = EX_D
y1 = EX_D + PEN_D + YARD              # south end of the first barns
y2 = y1 + MOD + BARN_GAP              # south end of the second barns
TOP = y2 + MOD

E = []
def add(id_, label, x, y, w, h, use, level, kind="building", note="", assumed=False, **extra):
    E.append(dict(id=id_, label=label, x=x, y=y, w=w, h=h, use=use, level=level, kind=kind, note=note, assumed=assumed, **extra))

# existing (Level 1)
add("existing-barn", "Existing barn", RIGHT - EX_W, 0, EX_W, EX_D, "swine", 1, note="Hog pens inside", becomes={"2": {"use": "circulation", "note": "Storage"}})
add("existing-pens", "7 existing cattle pens", RIGHT - MOD, y_ex_pens, MOD, PEN_D, "cattle", 1, pens={"n": 7, "w": PEN_W, "rows": [[0, PEN_D]]})
add("handling", "New corral, chute and scale", RIGHT + 14, 8, 56, 60, "cattle", 1, kind="yard", note="Location to confirm", assumed=True)
add("parking", "Parking", x_small, 4, RIGHT - EX_W - 22, 62, "circulation", 1, kind="parking", note="Existing lot, shown schematically", assumed=True)
# Level 2
add("cattle-a", "Cattle barn A", x_cattle, y1, CATTLE_W, MOD, "cattle", 2, note="14 pens", pens={"n": 7, "w": PEN_W, "rows": [[0, PEN_D], [PEN_D + AISLE, PEN_D]], "vertical": True})
add("small-a", "Small animal & swine barn A", x_small, y1, SMALL_W, MOD, "small_animal", 2, note="Sheep, goats, poultry, swine",
    pens={"n": MOD // SA_PEN_W, "w": SA_PEN_W, "rows": [[0, SA_PEN_D], [SA_PEN_D + SA_AISLE, SA_PEN_D]], "vertical": True}, assumed_pens=True)
add("feed", "Feed storage", x_mid, y1, ARENA_W, STORE_D, "circulation", 2, note="Next to the parking", assumed=True)
add("turnout-cattle-a", "Turnout", RIGHT + 4, y1, TURNOUT, MOD, "arena", 2, kind="yard", assumed=True)
add("turnout-small-a", "Turnout", x_small - TURNOUT - 4, y1, TURNOUT, MOD, "arena", 2, kind="yard", assumed=True)
# Level 3
add("cattle-b", "Cattle barn B", x_cattle, y2, CATTLE_W, MOD, "cattle", 3, note="14 pens", pens={"n": 7, "w": PEN_W, "rows": [[0, PEN_D], [PEN_D + AISLE, PEN_D]], "vertical": True})
add("small-b", "Small animal barn B", x_small, y2, SMALL_W, MOD, "small_animal", 3,
    pens={"n": MOD // SA_PEN_W, "w": SA_PEN_W, "rows": [[0, SA_PEN_D], [SA_PEN_D + SA_AISLE, SA_PEN_D]], "vertical": True}, assumed_pens=True)
add("arena", "Arena", x_mid, y2, ARENA_W, MOD, "arena", 3, note="50' x 84'")
add("turnout-cattle-b", "Turnout", RIGHT + 4, y2, TURNOUT, MOD, "arena", 3, kind="yard", assumed=True)
add("turnout-small-b", "Turnout", x_small - TURNOUT - 4, y2, TURNOUT, MOD, "arena", 3, kind="yard", assumed=True)

# flip y so the SVG reads with the existing barn at the bottom
for e in E:
    e["y"] = TOP - (e["y"] + e["h"])

pad = 40
view = [x_small - TURNOUT - 4 - pad, -pad, RIGHT + 14 + 56 + pad - (x_small - TURNOUT - 4 - pad), TOP + 2 * pad]
dims = [
    {"label": f"{MOD}' barn module", "x1": RIGHT + TURNOUT + 16, "y1": TOP - (y2 + MOD), "x2": RIGHT + TURNOUT + 16, "y2": TOP - y2},
    {"label": f"{CATTLE_W}'", "x1": x_cattle, "y1": -14, "x2": RIGHT, "y2": -14},
    {"label": f"{ARENA_W}'", "x1": x_mid, "y1": -14, "x2": x_mid + ARENA_W, "y2": -14},
    {"label": f"{SMALL_W}'", "x1": x_small, "y1": -14, "x2": x_small + SMALL_W, "y2": -14},
]
data = {
    "units": "feet", "view": view, "north_cw_from_up": -17, "elements": E, "dims": dims,
    "counts": {"cattle_pens": {"1": 7, "2": 21, "3": 35},
               "small_animal_pens_per_barn": 2 * (MOD // SA_PEN_W)},
    "assumptions": {"lane_ft": LANE, "barn_gap_ft": BARN_GAP, "yard_ft": YARD, "feed_storage_ft": [ARENA_W, STORE_D],
                    "small_animal_aisle_ft": SA_AISLE, "turnout_depth_ft": TURNOUT, "existing_barn_depth_ft": EX_D},
}
os.makedirs(os.path.join(ROOT, "slides", "data"), exist_ok=True)
with open(os.path.join(ROOT, "slides", "data", "ag-area.js"), "w") as fh:
    fh.write("// Generated by tools/build_ag_area.py. Edit the dimensions there, not here.\n")
    fh.write("window.AG_AREA = " + json.dumps(data, indent=1) + ";\n")


# ---------------------------------------------------------------- editable master (Level 3 state)
def pens_svg(e):
    p = e.get("pens")
    if not p:
        return ""
    out = []
    for off, depth in p["rows"]:
        for i in range(p["n"]):
            if p.get("vertical"):
                out.append(f'<rect x="{e["x"] + off}" y="{e["y"] + i * p["w"]}" width="{depth}" height="{p["w"]}"/>')
            else:
                out.append(f'<rect x="{e["x"] + i * p["w"]}" y="{e["y"] + off}" width="{p["w"]}" height="{depth}"/>')
    return f'<g fill="none" stroke="{N["ink"]}" stroke-width=".35" opacity=".45">{"".join(out)}</g>'


svg = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
       f'viewBox="{view[0]} {view[1]} {view[2]} {view[3]}" font-family="Avenir Next,Helvetica,Arial,sans-serif">'
       f'<title>Primary ag area, Level 3 (feet)</title><rect x="{view[0]}" y="{view[1]}" width="{view[2]}" height="{view[3]}" fill="{N["paper"]}"/>']
for lv in (1, 2, 3):
    svg.append(f'<g id="level-{lv}" inkscape:groupmode="layer" inkscape:label="Level {lv}">')
    for e in [e for e in E if e["level"] == lv]:
        use = e.get("becomes", {}).get("2", {}).get("use", e["use"])
        c = P[use]
        dash = ' stroke-dasharray="3 2"' if e["kind"] == "yard" else ""
        fill = c["tint"] if e["kind"] != "yard" else "none"
        svg.append(f'<g id="{e["id"]}"><rect x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}" fill="{fill}" stroke="{c["base"]}" stroke-width="1"{dash}/>'
                   f'{pens_svg(e)}<text x="{e["x"] + e["w"] / 2}" y="{e["y"] + e["h"] / 2}" text-anchor="middle" font-size="5" font-weight="700" fill="{N["ink"]}">{e["label"].replace("&", "&amp;")}</text></g>')
    svg.append("</g>")
svg.append("</svg>")
open(os.path.join(ROOT, "drawings", "ag-area-diagram.svg"), "w").write("".join(svg))
print("extent (ft):", round(view[2]), "x", round(view[3]), "| elements:", len(E), "| small-animal pens per barn:", data["counts"]["small_animal_pens_per_barn"])
