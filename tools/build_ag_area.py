"""Build the primary ag-area diagram: a to-scale layout of the barnyard, by Level and by use.

This is a diagram, not a survey drawing. Units are feet, drawn square to the existing barn (which sits
about 17 degrees off true north, measured from the study plan). x runs east, y runs south from the
north end of the barn runs. Everything sits on a 12' module with 24' lanes.

Layout (architect's markup of 2026-10-12, snapped to the module):
  east column   existing barn in the bottom-right corner, its 7 existing pens above it across an 8' aisle, and the two
                cattle turnouts stacked above those
  cattle run    two 14-pen barns (2 rows of 7 x 12' x 24' on a 14' aisle = 84' x 62'), west of the turnouts
  centre strip  arena (50' x 84') beside the second barns; feed storage in shipping containers
                (2 x 8' x 40', side by side, doors at alternate ends, AC at the other end) at the parking end
  small run     two small animal barns, 84' x 36' (6' x 10' pens both sides of a 16' aisle)
  west          small animal turnouts; new corral, chute and scale below them
  south         one bay of the main parking lot: 10' x 20' stalls on a 24' aisle, between two 24' driveways

Writes
  slides/data/ag-area.js          elements, circulation and dimensions for slides/ag-area.html
  drawings/ag-area-diagram.svg    editable master (Level 3 state, one layer per Level + circulation)
The master keeps one <g id="..."> per element. If it is edited in Illustrator, the ids survive, and the
moved rectangles can be read back into the numbers below.

Run:  python tools/build_ag_area.py
"""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
pal = json.load(open(os.path.join(ROOT, "design", "palette.json")))
P, N = pal["program"], pal["neutral"]

# ---------------------------------------------------------------- dimensions (feet)
M = 12                                # planning module
PEN_W, PEN_D, AISLE = 12, 24, 14
MOD = 7 * PEN_W                       # 84' barn module
CATTLE_W = 2 * PEN_D + AISLE          # 62'
SMALL_W = 36
SA_PEN_W, SA_PEN_D = 6, 10
SA_AISLE = SMALL_W - 2 * SA_PEN_D     # 16'
ARENA_W = 50
LANE = 24                             # every lane and gap: two modules
EX_W, EX_D = 80.4, 50                 # existing barn (depth approximate, from the survey)
EX_AISLE = 8                          # aisle between the existing pens and the barn (exists on site; not on the survey)
BOX_W, BOX_L = 8, 40                  # shipping container
STALL_W, STALL_D, PARK_AISLE = 10, 20, 24   # large stalls for trucks and SUVs, as on the source plan
PARK_N = 9                            # stalls per row shown here (the main lot continues beyond this diagram)
TURNOUT_SMALL = 48

# ---------------------------------------------------------------- layout (x east, y south)
x_small = 0
x_west_lane = x_small + SMALL_W               # 36..60
x_mid = x_west_lane + LANE                    # 60..110
x_east_lane = x_mid + ARENA_W                 # 110..134
x_cattle = x_east_lane + LANE                 # 134..196
x_col = x_cattle + CATTLE_W                   # east column 196..280
EAST = x_col + MOD
yB = 0                                        # second barns (Level 3)
yA = yB + MOD + LANE                          # first barns (Level 2): 108..192
y_drive = yA + MOD                            # main cross drive: 192..216
y_pens = y_drive + LANE                       # existing pens: 216..240
y_barn = y_pens + PEN_D + EX_AISLE            # existing barn: 248..298
SOUTH = y_barn + EX_D

E = []
def add(id_, label, x, y, w, h, use, level, kind="building", note="", assumed=False, **extra):
    E.append(dict(id=id_, label=label, x=x, y=y, w=w, h=h, use=use, level=level, kind=kind, note=note, assumed=assumed, **extra))

cattle_pens = {"n": 7, "w": PEN_W, "rows": [[0, PEN_D], [PEN_D + AISLE, PEN_D]], "vertical": True}
small_pens = {"n": MOD // SA_PEN_W, "w": SA_PEN_W, "rows": [[0, SA_PEN_D], [SA_PEN_D + SA_AISLE, SA_PEN_D]], "vertical": True}

# Level 1
add("existing-barn", "Existing barn", EAST - EX_W, y_barn, EX_W, EX_D, "swine", 1, note="Hog pens inside",
    becomes={"2": {"use": "circulation", "note": "Storage"}})
add("existing-pens", "7 existing cattle pens", x_col, y_pens, MOD, PEN_D, "cattle", 1, pens={"n": 7, "w": PEN_W, "rows": [[0, PEN_D]]})
add("handling", "New corral, chute and scale", x_small - 6 * M, y_pens, 6 * M, 6 * M, "cattle", 1, kind="yard", note="Bud Box layout to come")
# Parking: one bay of the main lot, between two 24' driveways. The west driveway continues the west lane;
# the east driveway lines up with the cattle barns' tractor aisle, for equipment and material drop-off.
park_w = PARK_N * STALL_W + 3
y_park = y_pens + M                            # a 12' strip south of the cross drive
x_drive_e = x_mid + park_w                     # east driveway 153..177, centred on the tractor aisle (x = 165)
add("parking", "Main parking lot", x_mid, y_park, park_w, 2 * STALL_D + PARK_AISLE, "circulation", 1, kind="parking",
    note="continues south", stalls={"n": PARK_N, "w": STALL_W, "d": STALL_D, "aisle": PARK_AISLE, "inset": 1.5})
DRIVES = [dict(id="drive-west", x=x_west_lane, y=y_pens, w=LANE, h=y_park + 2 * STALL_D + PARK_AISLE - y_pens),
          dict(id="drive-east", x=x_drive_e, y=y_pens, w=LANE, h=y_park + 2 * STALL_D + PARK_AISLE - y_pens)]
# Level 2
add("cattle-a", "Cattle barn A", x_cattle, yA, CATTLE_W, MOD, "cattle", 2, note="14 pens", pens=cattle_pens)
add("small-a", "Small animal & swine barn A", x_small, yA, SMALL_W, MOD, "small_animal", 2, pens=small_pens)
add("feed-1", "Feed storage 1", x_mid + 5, y_drive - BOX_W - 4, BOX_L, BOX_W, "circulation", 2, kind="container", note="8' x 40' container", doors="w")
add("turnout-cattle-a", "Turnout", x_col, yA, MOD, y_pens - yA, "arena", 2, kind="yard")
add("turnout-small-a", "Turnout", x_small - TURNOUT_SMALL, yA, TURNOUT_SMALL, MOD, "arena", 2, kind="yard")
# Level 3
add("cattle-b", "Cattle barn B", x_cattle, yB, CATTLE_W, MOD, "cattle", 3, note="14 pens", pens=cattle_pens)
add("small-b", "Small animal barn B", x_small, yB, SMALL_W, MOD, "small_animal", 3, pens=small_pens)
add("arena", "Arena", x_mid, yB, ARENA_W, MOD, "arena", 3, note="50' x 84'")
add("feed-2", "Feed storage 2", x_mid + 5, y_drive - 2 * BOX_W - 4, BOX_L, BOX_W, "circulation", 3, kind="container", note="second container", doors="e")
add("turnout-cattle-b", "Turnout", x_col, yB, MOD, MOD, "arena", 3, kind="yard")
add("turnout-small-b", "Turnout", x_small - TURNOUT_SMALL, yB, TURNOUT_SMALL, MOD, "arena", 3, kind="yard")

# ---------------------------------------------------------------- circulation: straight runs only
# kind "service" = vehicles, tractors, deliveries; kind "animal" = stock moving between barn, turnout and handling
xw, xe = x_west_lane + LANE / 2, x_east_lane + LANE / 2
x_ta = x_cattle + PEN_D + AISLE / 2            # cattle tractor aisle
y_cross = y_drive + LANE / 2
y_end = y_pens + 7                             # datum: every north-south run ends just past the cross drive
y_bay = y_park + STALL_D + PARK_AISLE / 2      # parking drive aisle
C = [
    dict(id="lane-west", kind="service", label="West lane", pts=[[xw, yB - 14], [xw, y_end]]),
    dict(id="lane-east", kind="service", label="East lane", pts=[[xe, yB - 14], [xe, y_end]]),
    dict(id="drive-cross", kind="service", label="Cross drive", pts=[[x_small - 6 * M, y_cross], [x_col, y_cross]]),
    dict(id="lane-mid", kind="service", label="", pts=[[x_small - TURNOUT_SMALL, yB + MOD + LANE / 2], [EAST, yB + MOD + LANE / 2]]),
    dict(id="aisle-cattle", kind="service", label="Tractor aisle", pts=[[x_ta, yB - 14], [x_ta, y_end]]),
    dict(id="aisle-small", kind="service", label="", pts=[[x_small + SMALL_W / 2, yB - 14], [x_small + SMALL_W / 2, y_end]]),
    dict(id="loop-parking", kind="loop", label="", pts=[[xw, y_end + 10], [xw, y_bay], [x_drive_e + LANE / 2, y_bay], [x_drive_e + LANE / 2, y_end + 10]]),
    dict(id="an-cattle-a", kind="animal", label="", pts=[[x_col - 8, yA + MOD / 2], [x_col + 30, yA + MOD / 2]]),
    dict(id="an-cattle-b", kind="animal", label="", pts=[[x_col - 8, yB + MOD / 2], [x_col + 30, yB + MOD / 2]]),
    dict(id="an-small-a", kind="animal", label="", pts=[[x_small + 8, yA + MOD / 2], [x_small - 30, yA + MOD / 2]]),
    dict(id="an-small-b", kind="animal", label="", pts=[[x_small + 8, yB + MOD / 2], [x_small - 30, yB + MOD / 2]]),
    dict(id="an-pens", kind="animal", label="", pts=[[x_col + MOD / 2, y_pens + 8], [x_col + MOD / 2, y_pens - 30]]),
]

pad = 34
left = x_small - 6 * M - 26
view = [left - pad, yB - 14 - pad, EAST - left + 2 * pad + 20, SOUTH - yB + 14 + 2 * pad]
dims = [
    {"label": f"{MOD}'", "x1": EAST + 12, "y1": yB, "x2": EAST + 12, "y2": yB + MOD},
    {"label": f"{LANE}'", "x1": EAST + 12, "y1": yB + MOD, "x2": EAST + 12, "y2": yA},
    {"label": f"{SMALL_W}'", "x1": x_small, "y1": yB - 24, "x2": x_small + SMALL_W, "y2": yB - 24},
    {"label": f"{LANE}'", "x1": x_west_lane, "y1": yB - 24, "x2": x_mid, "y2": yB - 24},
    {"label": f"{ARENA_W}'", "x1": x_mid, "y1": yB - 24, "x2": x_east_lane, "y2": yB - 24},
    {"label": f"{LANE}'", "x1": x_east_lane, "y1": yB - 24, "x2": x_cattle, "y2": yB - 24},
    {"label": f"{CATTLE_W}'", "x1": x_cattle, "y1": yB - 24, "x2": x_col, "y2": yB - 24},
    {"label": f"{MOD}'", "x1": x_col, "y1": yB - 24, "x2": EAST, "y2": yB - 24},
]
data = {
    "units": "feet", "view": view, "north_cw_from_up": -17, "elements": E, "drives": DRIVES, "circulation": C, "dims": dims,
    "counts": {"cattle_pens": {"1": 7, "2": 21, "3": 35}, "small_animal_pens_per_barn": 2 * (MOD // SA_PEN_W), "parking": 2 * PARK_N},
    "module_ft": M, "lane_ft": LANE,
}
os.makedirs(os.path.join(ROOT, "slides", "data"), exist_ok=True)
with open(os.path.join(ROOT, "slides", "data", "ag-area.js"), "w") as fh:
    fh.write("// Generated by tools/build_ag_area.py. Edit the dimensions there, not here.\n")
    fh.write("window.AG_AREA = " + json.dumps(data, indent=1) + ";\n")


# ---------------------------------------------------------------- editable master (Level 3 state)
def pens_svg(e):
    p = e.get("pens")
    out = []
    if p:
        for off, depth in p["rows"]:
            for i in range(p["n"]):
                if p.get("vertical"):
                    out.append(f'<rect x="{e["x"] + off}" y="{e["y"] + i * p["w"]}" width="{depth}" height="{p["w"]}"/>')
                else:
                    out.append(f'<rect x="{e["x"] + i * p["w"]}" y="{e["y"] + off}" width="{p["w"]}" height="{depth}"/>')
    s = e.get("stalls")
    if s:
        for i in range(s["n"] + 1):
            x = e["x"] + s["inset"] + i * s["w"]
            out.append(f'<path d="M{x} {e["y"]}v{s["d"]}M{x} {e["y"] + s["d"] + s["aisle"]}v{s["d"]}"/>')
    return f'<g fill="none" stroke="{N["ink"]}" stroke-width=".35" opacity=".45">{"".join(out)}</g>' if out else ""


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
svg.append('<g id="drives" inkscape:groupmode="layer" inkscape:label="Driveways">' + "".join(
    f'<rect id="{d["id"]}" x="{d["x"]}" y="{d["y"]}" width="{d["w"]}" height="{d["h"]}" fill="{P["circulation"]["tint"]}" opacity=".6"/>' for d in DRIVES) + "</g>")
svg.append('<g id="circulation" inkscape:groupmode="layer" inkscape:label="Circulation">')
for c in C:
    col = P["cattle"]["base"] if c["kind"] == "animal" else N["ink"]
    pts = " ".join(f"{x},{y}" for x, y in c["pts"])
    svg.append(f'<polyline id="{c["id"]}" points="{pts}" fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
svg.append("</g></svg>")
open(os.path.join(ROOT, "drawings", "ag-area-diagram.svg"), "w").write("".join(svg))
print("extent (ft):", round(view[2]), "x", round(view[3]), "| elements:", len(E), "| circulation runs:", len(C), "| parking:", 2 * PARK_N)
