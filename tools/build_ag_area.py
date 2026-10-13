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
  south         the main parking lot, after the architect's simplified plan: north row, centre island, south row
                backing onto the bioswale island, a column at the east end; 10' x 20' stalls, 24' aisles.
                One-way loop, counter-clockwise: in from the Red House side at the south-east, west along the
                north aisle, south down the west leg, out to the entry drive. The loop's two legs line up
                with the tractor aisles of the two barn runs.
  west          trailer stop: its own 24' x 60' lane with a gate at each end, west of the loop's west leg. Beside
                it, the cattle handling yard (72' x 84'): lead-up alley and Bud Box along the north, 16' single-
                file alley south to the chute on the scale, holding pen with chamfered corners around the chute

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
# ---- parking and handling, after the architect's simplified plan of 2026-10-12 ----
# One-way loop, counter-clockwise: traffic comes up from the Red House side into the east end of the lot,
# runs west along the north aisle, turns south down the west leg and leaves toward the entry drive.
# The loop's two north-south legs line up with the barns' tractor aisles (west leg = small animal barns,
# east leg = cattle barns), so a tractor runs straight from the lot through both barns of a run.
X_WLEG = x_small + SMALL_W / 2                 # centreline of the west leg = small animal barn aisle (x = 18)
X_ELEG = x_cattle + PEN_D + AISLE / 2          # centreline of the east leg = cattle tractor aisle (x = 165)
XW0, XW1 = X_WLEG - LANE / 2, X_WLEG + LANE / 2            # west leg 6..30
XE0, XE1 = X_ELEG - LANE / 2, X_ELEG + LANE / 2            # east leg 153..177
y_park = y_pens + M                            # north stall row, 12' south of the cross drive
y_n_aisle = y_park + STALL_D                   # north aisle (westbound)
y_island = y_n_aisle + PARK_AISLE              # centre island: two rows nose to nose
y_m_aisle = y_island + 2 * STALL_D             # middle aisle
y_s_row = y_m_aisle + PARK_AISLE               # south row, backing onto the bioswale island
x_row = XW1 + (XE0 - XW1 - 12 * STALL_W) / 2   # 12 stalls centred between the two legs
ROWS = [  # x, y, number of stalls, optional "v" for a column of stalls facing east
    [x_row, y_park, 12],
    [x_row, y_island, 12], [x_row, y_island + STALL_D, 12],
    [x_row, y_s_row, 12],
    [XE1, y_n_aisle, 7, "v"],
]
n_stalls = sum(r[2] for r in ROWS)

# Handling yard, 72' x 84' (the layout on the study plan, after the Priefert Bud Box): lead-up alley and Bud Box
# along the north side, a 16' single-file alley dropping south beside the box gate to the chute on the scale
# (four cattle at most), and a holding pen with chamfered corners that wraps around the chute.
# The trailer stop is its own lane, 24' x 60' with a gate at each end, between the yard and the loop's west
# leg. Its north end lines up with the north end of the lead-up alley, just south of the north aisle, so a
# trailer turns in off the aisle, unloads, and rejoins the loop heading out.
TR_X, TR_W, TR_L = XW0 - 6 - LANE, LANE, 60    # trailer lane, 6' clear of the west leg
HW, HH = 6 * M, 7 * M
HX, HY = TR_X - HW, y_island                   # yard top = south edge of the north aisle
LOT_S = max(y_s_row + STALL_D + 36, HY + HH + 14)   # diagram stops here; both legs of the loop continue south
LOT_X0, LOT_X1 = 0, XE1 + STALL_D              # architect's edit: the lot is a plain rectangle, 197' wide
add("parking", "Main parking lot", LOT_X0, y_park, LOT_X1 - LOT_X0, LOT_S - y_park, "circulation", 1, kind="parking", note=f"{n_stalls} spaces",
    rows=ROWS, stall=[STALL_W, STALL_D],
    outline=[[LOT_X0, y_park], [LOT_X1, y_park], [LOT_X1, LOT_S], [LOT_X0, LOT_S]],
    island=dict(label="Bioswale island", x=XW1 + 2, y=y_s_row + STALL_D, w=XE0 - XW1 - 4, h=LOT_S - y_s_row - STALL_D))
add("trailer-stop", "Trailer stop", TR_X, HY, TR_W, TR_L, "circulation", 1, kind="yard", note="gate at each end")
DRIVES = []
ALLEY_L = 16                                   # single-file alley; with the chute it holds four cattle
YARD = [[0, 0], [72, 0], [72, 68], [56, 84], [16, 84], [0, 64]]
ay = 12 + ALLEY_L
add("handling", "Cattle handling", HX, HY, HW, HH, "cattle", 1, kind="yard", note="",
    outline=[[HX + px, HY + py] for px, py in YARD], zones=[
    dict(label="Holding pen", poly=[[0, 12], [16, 12], [16, ay], [15.3, ay], [15.3, ay + 9], [19.3, ay + 9], [19.3, ay], [18.6, ay], [18.6, 12], [72, 12], [72, 68], [56, 84], [16, 84], [0, 64]], at=[44, 50]),
    dict(label="Lead-up alley", x=20, y=0, w=52, h=12),
    dict(label="Bud Box", x=0, y=0, w=20, h=12, fill=True),
    dict(label="", x=16, y=12, w=2.6, h=ALLEY_L),
    dict(label="Chute", x=15.3, y=ay, w=4, h=9, fill=True, side=True),
])
# Level 2. Turnouts (architect's edit of 2026-10-12): each pair meets halfway across the 24' gap between the barn rows.
y_split = yB + MOD + LANE / 2
add("cattle-a", "Cattle barn A", x_cattle, yA, CATTLE_W, MOD, "cattle", 2, note="14 pens", pens=cattle_pens)
add("small-a", "Small animal barn A", x_small, yA, SMALL_W, MOD, "small_animal", 2, pens=small_pens)
add("feed-1", "Feed storage 1", x_mid + 5, y_drive - BOX_W - 4, BOX_L, BOX_W, "circulation", 2, kind="container", note="8' x 40' container", doors="w")
add("turnout-cattle-a", "Turnout", x_col, y_split, MOD, y_pens - y_split, "arena", 2, kind="yard")
add("turnout-small-a", "Turnout", x_small - TURNOUT_SMALL, y_split, TURNOUT_SMALL, yA + MOD - y_split, "arena", 2, kind="yard")
# Level 3
add("cattle-b", "Cattle barn B", x_cattle, yB, CATTLE_W, MOD, "cattle", 3, note="14 pens", pens=cattle_pens)
add("small-b", "Small animal barn B", x_small, yB, SMALL_W, MOD, "small_animal", 3, pens=small_pens)
add("arena", "Arena", x_mid, yB, ARENA_W, MOD, "arena", 3, note="50' x 84'")
add("feed-2", "Feed storage 2", x_mid + 5, y_drive - 2 * BOX_W - 4, BOX_L, BOX_W, "circulation", 3, kind="container", note="second container", doors="e")
add("turnout-cattle-b", "Turnout", x_col, yB, MOD, y_split - yB, "arena", 3, kind="yard")
add("turnout-small-b", "Turnout", x_small - TURNOUT_SMALL, yB, TURNOUT_SMALL, y_split - yB, "arena", 3, kind="yard")

# ---------------------------------------------------------------- circulation: straight runs only
# kind "service" = vehicles, tractors, deliveries; kind "animal" = stock moving between barn, turnout and handling
xw, xe = x_west_lane + LANE / 2, x_east_lane + LANE / 2
y_cross = y_drive + LANE / 2
y_end = y_drive + 3                            # datum: the lanes between the runs end just inside the cross drive
C = [
    dict(id="lane-west", kind="service", label="West lane", pts=[[xw, yB - 14], [xw, y_end]]),
    dict(id="lane-east", kind="service", label="East lane", pts=[[xe, yB - 14], [xe, y_end]]),
    dict(id="drive-cross", kind="service", label="Cross drive", pts=[[x_small - TURNOUT_SMALL, y_cross], [x_col - 3, y_cross]]),
    dict(id="lane-mid", kind="service", label="", pts=[[x_small + 5, y_split], [x_col - 12, y_split]]),   # between the runs only; the turnouts close both ends
    # tractor aisles: straight through both barns of a run and on into the legs of the parking loop
    dict(id="aisle-cattle", kind="service", label="Tractor aisle", pts=[[X_ELEG, yB - 14], [X_ELEG, y_n_aisle - 4]]),
    dict(id="aisle-small", kind="service", label="Tractor aisle", pts=[[X_WLEG, yB - 14], [X_WLEG, y_n_aisle - 4]]),
    # counter-clockwise loop: north up the east leg, west along the north aisle, south down the west leg
    dict(id="loop-parking", kind="loop", label="One-way loop",
         pts=[[X_ELEG, LOT_S + 16], [X_ELEG, y_n_aisle + 12], [X_WLEG, y_n_aisle + 12], [X_WLEG, LOT_S + 16]]),
    dict(id="loop-mid", kind="loop", label="", pts=[[XE0 - 2, y_m_aisle + 12], [XW1 + 2, y_m_aisle + 12]]),
    dict(id="trailers", kind="loop", label="", pts=[[XW0 - 2, y_n_aisle + 12], [TR_X + TR_W / 2, y_n_aisle + 12], [TR_X + TR_W / 2, HY + TR_L + 14], [XW0 + 6, HY + TR_L + 34]]),
    dict(id="an-cattle-a", kind="animal", label="", pts=[[x_col - 8, yA + MOD / 2], [x_col + 30, yA + MOD / 2]]),
    dict(id="an-cattle-b", kind="animal", label="", pts=[[x_col - 8, yB + MOD / 2], [x_col + 30, yB + MOD / 2]]),
    dict(id="an-small-a", kind="animal", label="", pts=[[x_small + 8, yA + MOD / 2], [x_small - 30, yA + MOD / 2]]),
    dict(id="an-small-b", kind="animal", label="", pts=[[x_small + 8, yB + MOD / 2], [x_small - 30, yB + MOD / 2]]),
    dict(id="an-pens", kind="animal", label="", pts=[[x_col + MOD / 2, y_pens + 8], [x_col + MOD / 2, y_pens - 30]]),
]

pad = 34
left = HX - 8
view = [left - pad, yB - 14 - pad, EAST - left + 2 * pad + 20, LOT_S + 34 - yB + 14 + 2 * pad]
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
    "notes": [dict(x=X_ELEG, y=LOT_S + 26, text="In, from the Red House side"), dict(x=X_WLEG, y=LOT_S + 26, text="Out, to the entry drive")],
    "counts": {"cattle_pens": {"1": 7, "2": 21, "3": 35}, "small_animal_pens_per_barn": 2 * (MOD // SA_PEN_W), "parking": n_stalls},
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
    for row in e.get("rows", []):
        rx, ry, n = row[:3]
        sw, sd = e["stall"]
        for i in range(n):
            if len(row) > 3:
                out.append(f'<rect x="{rx}" y="{ry + i * sw}" width="{sd}" height="{sw}"/>')
            else:
                out.append(f'<rect x="{rx + i * sw}" y="{ry}" width="{sw}" height="{sd}"/>')
    for z in e.get("zones", []):
        if "poly" in z:
            out.append('<polygon points="' + " ".join(f'{e["x"] + px},{e["y"] + py}' for px, py in z["poly"]) + '"/>')
        else:
            out.append(f'<rect x="{e["x"] + z["x"]}" y="{e["y"] + z["y"]}" width="{z["w"]}" height="{z["h"]}"/>')
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
        if e.get("outline"):
            shape = '<polygon points="' + " ".join(f"{px},{py}" for px, py in e["outline"]) + f'" fill="{fill}" stroke="{c["base"]}" stroke-width="1"{dash}/>'
        else:
            shape = f'<rect x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}" fill="{fill}" stroke="{c["base"]}" stroke-width="1"{dash}/>'
        svg.append(f'<g id="{e["id"]}">{shape}'
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
print("extent (ft):", round(view[2]), "x", round(view[3]), "| elements:", len(E), "| circulation runs:", len(C), "| parking:", n_stalls)
