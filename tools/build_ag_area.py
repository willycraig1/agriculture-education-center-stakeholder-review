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
  small run     small animal barn A, 84' x 36' (6' x 10' pens both sides of a 16' aisle), extended 42' north at
                Level 3 to 126' x 36' (4,536 sf, 42 pens); the north-west corner beyond it stays pasture (wet soil)
  west          small animal turnouts; new corral, chute and scale below them
  south         the main parking lot, after the architect's simplified plan: north row, centre island, south row
                backing onto the bioswale island; 10' x 20' stalls, 24' aisles. The apron in front of the
                existing barn's four overhead doors is kept clear.
                One-way loop, counter-clockwise: in from the Red House side at the south-east, west along the
                north aisle, south down the west leg, out to the entry drive. The loop's two legs line up
                with the tractor aisles of the two barn runs.
  west          trailer stop: a 24'-deep pull-off bay with tapered ends on the loop's west leg. Beside
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
# The loop's west leg continues the west lane between the runs (20' wide, no stalls off it); its east leg
# continues the cattle barns' tractor aisle.
X_WLEG = x_west_lane + LANE / 2               # centreline of the west leg = the west lane between the runs
WLEG_W = 20                                    # no stalls open off this leg, so it is kept to 20'
X_ELEG = x_cattle + PEN_D + AISLE / 2          # centreline of the east leg = cattle tractor aisle (x = 165)
XW0, XW1 = X_WLEG - WLEG_W / 2, X_WLEG + WLEG_W / 2        # west leg
XE0, XE1 = X_ELEG - LANE / 2, X_ELEG + LANE / 2            # east leg 153..177
y_park = y_pens                                # north stall row starts 24' (the cross drive) south of cattle barn A
y_n_aisle = y_park + STALL_D                   # north aisle (westbound)
y_island = y_n_aisle + PARK_AISLE              # centre island: two rows nose to nose
y_m_aisle = y_island + 2 * STALL_D             # middle aisle
y_s_row = y_m_aisle + PARK_AISLE               # south row, backing onto the bioswale island
N_ROW = int((XE0 - XW1) // STALL_W)            # stalls that fit between the two legs
x_row = XW1 + (XE0 - XW1 - N_ROW * STALL_W) / 2
ROWS = [  # x, y, number of stalls, optional "v" for a column of stalls facing east
    [x_row, y_park, N_ROW],
    [x_row, y_island, N_ROW], [x_row, y_island + STALL_D, N_ROW],
    [x_row, y_s_row, N_ROW],
]   # no stalls in front of the existing barn: that apron stays open for its four overhead doors
n_stalls = sum(r[2] for r in ROWS)

# Handling yard, 72' x 84' (the layout on the study plan, after the Priefert Bud Box): lead-up alley and Bud Box
# along the north side, a 16' single-file alley dropping south beside the box gate to the chute on the scale
# (four cattle at most), and a holding pen with chamfered corners that wraps around the chute.
# The trailer stop is its own lane, 24' x 60' with a gate at each end, between the yard and the loop's west
# leg. Its north end lines up with the north end of the lead-up alley, just south of the north aisle, so a
# trailer turns in off the aisle, unloads, and rejoins the loop heading out.
# Architect's placement of 2026-10-13: the trailer stop is a 24'-deep pull-off bay with tapered ends on the west
# side of the loop's west leg, and the handling yard sits directly west of the bay.
TR_W = LANE
TR_X = XW0 - TR_W
HW, HH = 6 * M, 7 * M
HX, HY = TR_X - HW, y_n_aisle + 11
BAY = [[TR_X, HY], [TR_X + 10, HY], [XW0, HY + 13], [XW0, HY + 68], [TR_X + 10, HY + HH], [TR_X, HY + HH]]
ISLAND_D = 36                                   # planted bioswale island behind the south stall row
LOT_S = max(y_s_row + STALL_D + ISLAND_D, HY + HH + 14)   # diagram stops here; both legs of the loop continue south
LOT_X0, LOT_X1 = XW0, XE1                        # architect's edits: a plain rectangle ending at the east leg (177');
                                               # the stall column by the existing barn sits outside the fill
add("parking", "Main parking lot", LOT_X0, y_park, LOT_X1 - LOT_X0, LOT_S - y_park, "circulation", 1, kind="parking", note=f"{n_stalls} spaces",
    rows=ROWS, stall=[STALL_W, STALL_D],
    outline=[[LOT_X0, y_park], [LOT_X1, y_park], [LOT_X1, LOT_S], [LOT_X0, LOT_S]],
    island=dict(label="Bioswale island", x=XW1 + 2, y=y_s_row + STALL_D, w=XE0 - XW1 - 4, h=LOT_S - y_s_row - STALL_D))
add("trailer-stop", "Trailer stop", TR_X, HY, TR_W, HH, "circulation", 1, kind="yard", note="pull-off bay", outline=BAY)
DRIVES = []
ALLEY_L = 16                                   # single-file alley; with the chute it holds four cattle
# Both south corners are chamfered (architect's markup, 2026-10-13): no square corner is drawn outside either one.
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
add("small-a", "Small animal barn A", x_small, yA, SMALL_W, MOD, "swine", 2, pens=small_pens)   # hog color: the hogs move here from the existing barn
add("feed-1", "Feed storage 1", x_mid + 5, y_drive - BOX_W - 4, BOX_L, BOX_W, "circulation", 2, kind="container", note="8' x 40' container", doors="w")
add("turnout-cattle-a", "Turnout", x_col, y_split, MOD, y_pens - y_split, "arena", 2, kind="yard")
add("turnout-small-a", "Turnout", x_small - TURNOUT_SMALL, yA, TURNOUT_SMALL, MOD, "arena", 2, kind="yard")
# Level 3
add("cattle-b", "Cattle barn B", x_cattle, yB, CATTLE_W, MOD, "cattle", 3, note="14 pens", pens=cattle_pens)
# Level 3 adds a 42' extension to barn A (not a second barn): a full-length barn B would sit 62% on the very
# poorly drained soil, and that many small animal projects are unlikely. Extended, barn A is 126' x 36' = 4,536 sf.
EXT = MOD // 2
add("small-b", "Barn A extension", x_small, yA - EXT, SMALL_W, EXT, "small_animal", 3, note="14 pens",
    pens={"n": EXT // SA_PEN_W, "w": SA_PEN_W, "rows": [[0, SA_PEN_D], [SA_PEN_D + SA_AISLE, SA_PEN_D]], "vertical": True})
add("turnout-small-b", "", x_small - TURNOUT_SMALL, yA - EXT, TURNOUT_SMALL, EXT, "arena", 3, kind="yard")   # the extension's turnout, split at the barn joint
add("arena", "Arena", x_mid, yB, ARENA_W, MOD, "arena", 3, note="50' x 84'")
add("feed-2", "Feed storage 2", x_mid + 5, y_drive - 2 * BOX_W - 4, BOX_L, BOX_W, "circulation", 3, kind="container", note="second container", doors="e")
add("turnout-cattle-b", "Turnout", x_col, yB, MOD, y_split - yB, "arena", 3, kind="yard")

# ---------------------------------------------------------------- circulation: straight runs only
# kind "service" = vehicles, tractors, deliveries; kind "animal" = stock moving between barn, turnout and handling
xw, xe = x_west_lane + LANE / 2, x_east_lane + LANE / 2
y_cross = y_drive + LANE / 2
y_end = y_drive + 3                            # datum: the lanes between the runs end just inside the cross drive
C = [
    dict(id="lane-west", kind="service", label="West lane", pts=[[xw, yB - 14], [xw, y_n_aisle + 12]]),     # runs straight on into the loop's west leg
    dict(id="lane-east", kind="service", label="East lane", pts=[[xe, yB - 14], [xe, y_cross]]),
    dict(id="drive-cross", kind="service", label="Cross drive", pts=[[x_small - TURNOUT_SMALL, y_cross], [x_col - 3, y_cross]]),
    dict(id="lane-mid", kind="service", label="", pts=[[xw, y_split], [x_col - 12, y_split]]),   # between the runs only; the turnouts close both ends
    # tractor aisles: straight through both barns of a run and on into the legs of the parking loop
    dict(id="aisle-cattle", kind="service", label="Tractor aisle", pts=[[X_ELEG, yB - 14], [X_ELEG, y_n_aisle + 12]]),
    dict(id="aisle-small", kind="service", label="Tractor aisle", pts=[[x_small + SMALL_W / 2, yA - EXT - 12], [x_small + SMALL_W / 2, y_cross]]),
    # counter-clockwise loop: north up the east leg, west along the north aisle, south down the west leg
    dict(id="loop-parking", kind="loop", label="One-way loop",
         pts=[[X_ELEG, LOT_S + 16], [X_ELEG, y_n_aisle + 12], [X_WLEG, y_n_aisle + 12], [X_WLEG, LOT_S + 16]]),
    dict(id="loop-mid", kind="loop", label="", pts=[[XE0 - 2, y_m_aisle + 12], [XW1 + 2, y_m_aisle + 12]]),
    dict(id="trailers", kind="loop", label="", pts=[[XW0 - 2, HY + 1], [XW0 - 12, HY + 11], [XW0 - 12, HY + 74], [XW0 + 4, HY + 87]]),
    dict(id="an-cattle-a", kind="animal", label="", pts=[[x_col - 8, yA + MOD / 2], [x_col + 30, yA + MOD / 2]]),
    dict(id="an-cattle-b", kind="animal", label="", pts=[[x_col - 8, yB + MOD / 2], [x_col + 30, yB + MOD / 2]]),
    dict(id="an-small-a", kind="animal", label="", pts=[[x_small + 8, yA + MOD / 2], [x_small - 30, yA + MOD / 2]]),
    dict(id="an-pens", kind="animal", label="", pts=[[x_col + MOD / 2, y_pens + 8], [x_col + MOD / 2, y_pens - 30]]),
]

# ---------------------------------------------------------------- shift relative to the existing barn and pens
# Architect, 2026-10-13: everything new moves 24' west and 24' south; the existing barn and pens stay put.
# This pulls the new work off the wet soil along the north edge. The layout above is unchanged internally.
DX, DY = -24, 24
def _mv(p):
    return [p[0] + DX, p[1] + DY]
for e in E:
    if e["id"].startswith("existing"):
        continue
    e["x"] += DX; e["y"] += DY
    if "outline" in e:
        e["outline"] = [_mv(q) for q in e["outline"]]
    if "rows" in e:
        e["rows"] = [[r[0] + DX, r[1] + DY, *r[2:]] for r in e["rows"]]
    if "island" in e:
        e["island"]["x"] += DX; e["island"]["y"] += DY
for c in C:
    c["pts"] = [_mv(q) for q in c["pts"]]
NOTES_ = [dict(x=X_ELEG + DX, y=LOT_S + 26 + DY, text="In, from the Red House side"), dict(x=X_WLEG + DX, y=LOT_S + 26 + DY, text="Out, to the entry drive")]
by_id = {e["id"]: e for e in E}
# cattle turnout A would now run into the existing pens: it stops at their north edge and west end instead
ta = by_id["turnout-cattle-a"]
ta["h"] = y_pens - ta["y"]
for k in ("turnout-cattle-a", "turnout-cattle-b"):          # east edge lines up with the existing pens
    by_id[k]["w"] = EAST - by_id[k]["x"]
# Holding pens for the handling yard (architect's sketch, 2026-10-13), Level 1. Three pens run down the west side,
# their east fence on the line of the handling yard's west side, their west fence a straight line set back from
# the historical slough bed (62' deep at the north end, 118' at the south; the sketch's line trimmed about 7' to clear the bank). Pen 1 is beside the handling yard,
# where its gate to pasture opens; pen 2 runs north from there to the middle of small animal barn A; pen 3 on
# to the north end of the small animal turnouts. Pen 4 fills the gap between the small animal turnout and the
# handling yard's Bud Box. Sizes are read from the sketch, not dimensioned.
_hd, _tsa, _tsb = by_id["handling"], by_id["turnout-small-a"], by_id["turnout-small-b"]
_xe, _yn, _ys, _y1 = _hd["x"], _tsb["y"], _hd["y"] + _hd["h"], _hd["y"]
_y2 = _tsa["y"] + _tsa["h"] / 2
PEN_DEPTH_N, PEN_DEPTH_S = 62, 118        # pens' depth west of the handling line, north and south ends (ft)
_wx = lambda y: _xe - PEN_DEPTH_N - (PEN_DEPTH_S - PEN_DEPTH_N) * (y - _yn) / (_ys - _yn)
def _pen(n, pts, level=1):
    xs_, ys_ = [q[0] for q in pts], [q[1] for q in pts]
    area = abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))) / 2
    add(f"holding-{n}", f"Pen {n}", min(xs_), min(ys_), max(xs_) - min(xs_), max(ys_) - min(ys_), "cattle", level, kind="yard",
        note=f"{round(area, -1):,.0f} sf", outline=[[round(x, 1), round(y, 1)] for x, y in pts], holding=True)
    by_id[f"holding-{n}"] = E[-1]
# pen 1 follows the handling yard's south-west chamfer: its south fence runs straight on to the chamfer's end, so
# there is no fence across the little triangle at that corner
_pen(1, [[_xe, _y1], [_xe, _y1 + YARD[-1][1]], [_xe + YARD[-2][0], _ys], [_wx(_ys), _ys], [_wx(_y1), _y1]])
_pen(2, [[_xe, _y2], [_xe, _y1], [_wx(_y1), _y1], [_wx(_y2), _y2]])
_pen(3, [[_xe, _yn], [_xe, _y2], [_wx(_y2), _y2], [_wx(_yn), _yn]])
_pen(4, [[_tsa["x"], _tsa["y"] + _tsa["h"]], [_tsa["x"] + _tsa["w"], _tsa["y"] + _tsa["h"]], [_tsa["x"] + _tsa["w"], _y1], [_tsa["x"], _y1]])
print("holding pens:", [(e["id"], e["note"]) for e in E if e.get("holding")])

# The Red House footprint and the horticulture area, brought in from the site drawings so the barnyard reads in
# its setting. Both are placed by turning their surveyed outlines into this diagram's feet (the inverse of the
# transform that puts the diagram on the map, siteframe.diagram_transform).
#   Red House     the architect's outline of the existing building (drawings/data/site-edits.json)
#   Horticulture  the "HORTICULTURE AREA" rectangle on the study plan A0.2 (layer A-WALL-OTLN), 100' x 30',
#                 beside the drive south of the Red House.
#   Residence     the 20' x 30' "RESIDENCE" at the north-west end of that rectangle. A Level 3 element; at
#                 Levels 1 and 2 the same spot carries hookups for a camper or RV (architect, 2026-10-13).
import sys as _sys
_sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import siteframe as _sf
_M, _T = _sf.diagram_transform(x_col + MOD / 2, y_pens)
_to_d = lambda q: [round(v, 1) for v in (lambda z: (z.real, z.imag))((complex(*q) - _T) / _M)]
def _ext(id_, label, pts, use, kind, note, **extra):
    xs_, ys_ = [q[0] for q in pts], [q[1] for q in pts]
    add(id_, label, min(xs_), min(ys_), max(xs_) - min(xs_), max(ys_) - min(ys_), use, 1, kind=kind, note=note, outline=pts, context=True, **extra)
    by_id[id_] = E[-1]
_edits = json.load(open(os.path.join(_sf.OUT, "data", "site-edits.json")))
_rh = max(_edits["structures"], key=lambda s_: (max(q[0] for q in s_["pts"]) - min(q[0] for q in s_["pts"])) * (max(q[1] for q in s_["pts"]) - min(q[1] for q in s_["pts"])) if 1180 < s_["pts"][0][0] < 1240 and 340 < s_["pts"][0][1] < 400 else 0)
_ext("existing-red-house", "Red House", [_to_d(q) for q in _rh["pts"][:-1]], "education", "building", "")
_hl = []
for _d in _sf.cadpdf.export(_sf.STUDY, ["A-WALL-OTLN"]).get("A-WALL-OTLN", []):
    for _it in _d["items"]:
        if _it[0] == "l":
            _a, _b = (_sf.M_TP * complex(q.x, q.y) + _sf.T_TP for q in (_it[1], _it[2]))
            if abs(_b - _a) * _sf.FT_PER_PT / abs(_sf.M_FP) > 25 and abs((_a + _b) / 2 - complex(1216, 430)) < 40:     # the rectangle south of the Red House only
                _hl.append((_a, _b))
_long = sorted(_hl, key=lambda sg: -abs(sg[1] - sg[0]))[:2]                       # the two 120' sides
_lends = [z for sg in _long for z in sg]
_div = max((sg for sg in _hl if sg not in _long), key=lambda sg: min(abs(z - e_) for z in sg for e_ in _lends))   # the short line that is not an end: it cuts off the residence
_far = lambda sg, p: max(sg, key=lambda z: abs(z - p))                             # the end of a long side away from the residence
_h = [_div[0], _far(min(_long, key=lambda sg: min(abs(sg[0] - _div[0]), abs(sg[1] - _div[0]))), _div[0]),
      _far(min(_long, key=lambda sg: min(abs(sg[0] - _div[1]), abs(sg[1] - _div[1]))), _div[1]), _div[1]]
_ext("horticulture", "Horticulture area", [_to_d((z.real, z.imag)) for z in _h], "horticulture", "garden", "Raised beds and pots",
     becomes={"2": {"use": "horticulture", "note": "Beds with irrigation"}, "3": {"use": "horticulture", "note": "Shade area, planting tables"}})
_near = lambda sg, p: min(sg, key=lambda z: abs(z - p))                           # the end of a long side at the residence
_r = [_near(min(_long, key=lambda sg: min(abs(sg[0] - _div[0]), abs(sg[1] - _div[0]))), _div[0]), _div[0], _div[1],
      _near(min(_long, key=lambda sg: min(abs(sg[0] - _div[1]), abs(sg[1] - _div[1]))), _div[1])]
_ext("residence", "Residence", [_to_d((z.real, z.imag)) for z in _r], "education", "building", "Camper / RV hookups",
     becomes={"3": {"use": "education", "note": "Residence"}})
# ---- the parking lot's south loop, from the architect's CAD sketch of the lot (2026-10-12)
# The sketch (pixel coordinates read off the screenshot) is placed by the Red House carport drawn on it: its four
# corners are matched to the carport on the survey (BUILDING OH, 29' x 38'). That places the sketch to within about
# half a foot at the carport, at 4.35 px/ft and square to this diagram, with its Red House steps on the Red House.
# Only the south part is taken: the west leg carries on south and turns south-east along a row of nine angled
# stalls (backing onto the horticulture strip, as on the study plan) to the carport; the bioswale island gets
# the sketch's rounded south end. The north part of the lot stays as already laid out, so the island is cut to
# the space between the two legs, south of the south stall row, and the west edge follows this lot's west leg.
from shapely.geometry import Polygon as _Poly, MultiPoint as _MPt, Point as _Pt, box as _box
from shapely.ops import unary_union as _union
_oh = [(_sf.M_SP * complex(q.x, q.y) + _sf.T_SP) for _d in _sf.cadpdf.export(_sf.SURVEY, ["BUILDING OH"]).get("BUILDING OH", [])
       for _it in _d["items"] if _it[0] == "l" for q in (_it[1], _it[2])]
_oh = [z for z in _oh if 1220 < z.real < 1243 and 376 < z.imag < 399]
_cpm = list(_MPt([(z.real, z.imag) for z in _oh]).minimum_rotated_rectangle.exterior.coords)[:4]
_cpd = [(complex(*q) - _T) / _M for q in _cpm]
_SK_CARPORT = [complex(963, 1257), complex(1070, 1330), complex(1163, 1190), complex(1056, 1118)]
_SK_STEPS = complex(1358, 750)                                    # the Red House's wood steps on the sketch
_rhp = _Poly(by_id["existing-red-house"]["outline"])
_best = None
for _k in range(4):
    _dd = [_cpd[(_k + i) % 4] for i in range(4)]
    _m = (_dd[2] - _dd[0]) / (_SK_CARPORT[2] - _SK_CARPORT[0]); _t = _dd[0] - _m * _SK_CARPORT[0]
    _err = max(abs(_m * _SK_CARPORT[i] + _t - _dd[i]) for i in range(4))
    _w = _m * _SK_STEPS + _t
    _score = _err + _rhp.exterior.distance(_Pt(_w.real, _w.imag))      # corners fit, and the steps land on the Red House
    if _best is None or _score < _best[0]:
        _best = (_score, _m, _t, _err)
_, _MS, _TS, _sk_err = _best
_sk = lambda x, y: (lambda z: (round(z.real, 1), round(z.imag, 1)))(_MS * complex(x, y) + _TS)
_lx0, _lx1 = by_id["parking"]["x"], by_id["parking"]["x"] + by_id["parking"]["w"]          # this lot's west and east edges
_row_back = y_s_row + STALL_D + DY                                                         # back of the south stall row
_island = _Poly([_sk(*q) for q in [(596, 613), (1083, 613), (1083, 730), (1072, 772), (1060, 800), (950, 960), (920, 990), (885, 1010),
                                  (845, 1015), (805, 1010), (770, 995), (650, 912), (618, 880), (600, 840), (596, 805)]])
_island = _island.intersection(_box(XW1 + DX + 2, _row_back, XE0 + DX - 2, 9999))
_stall_front = [_sk(530, 962), _sk(862, 1183)]
_stall_back = [_sk(483, 1035), _sk(815, 1255)]
_lerp = lambda a, b, f: (round(a[0] + (b[0] - a[0]) * f, 1), round(a[1] + (b[1] - a[1]) * f, 1))
SOUTH_STALLS = [[_lerp(*_stall_front, i / 9), _lerp(*_stall_front, (i + 1) / 9), _lerp(*_stall_back, (i + 1) / 9), _lerp(*_stall_back, i / 9)] for i in range(9)]
_south = _Poly([(_lx0, _row_back), (_lx1, _row_back), _sk(1136, 787), _sk(975, 1062), _sk(1056, 1118), _sk(963, 1257), _sk(862, 1183),
                _sk(815, 1255), _sk(483, 1035), (_lx0, _sk(520, 955)[1])]).buffer(0)
_lot = _union([_box(_lx0, by_id["parking"]["y"], _lx1, _row_back), _south]).buffer(0.01).buffer(-0.01).simplify(0.3)
# The entry drive, from the same sketch: about 12' between edges, meeting the west leg with 10' curb returns. It
# lies on the existing surveyed drive (the survey's edges cross the diagram at y = 391 and 402); it is carried on
# west to the line of the handling yard's west side, where the drive continues off the diagram toward the lane.
import math as _math
def _ret(cx, cy, r, a0, a1, n=6):
    return [_sk(cx + r * _math.cos(_math.radians(a0 + (a1 - a0) * i / n)), cy + r * _math.sin(_math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
# Carried all the way to the lane, standing for the new entry apron built at Level 1: the survey's lane edge where
# the existing drive meets it (diagram x about -290 at the drive), flared 10' each side at the road.
_lane_x = lambda y: -292 + 5 * (y - 314) / 95                                 # the lane's near edge, from the surveyed road edges
_w_end = round(_lane_x(393), 1)                                            # west end of the drive: the lane
_top_l, _bot_l = _sk(270, 745), _sk(270, 800)
_ENTRY = [(_w_end, _top_l[1] + (_top_l[1] - _sk(475, 752)[1]) * (_w_end - _top_l[0]) / (_top_l[0] - _sk(475, 752)[0]))] + [_top_l, _sk(475, 752)] + \
         _ret(475, 708, 45, 90, 0) + [_sk(520, 700), _sk(530, 700), _sk(530, 860), _sk(520, 860)] + _ret(475, 850, 45, 0, -90) + \
         [_sk(478, 806), _bot_l, (_w_end, _bot_l[1] + (_bot_l[1] - _sk(478, 806)[1]) * (_w_end - _bot_l[0]) / (_bot_l[0] - _sk(478, 806)[0]))]
# the sketch's west leg sits about 5' west of this lot's: move the drive east with it so its returns meet the leg
_shift = _lx0 - _sk(520, 700)[0]
_ENTRY = [(_w_end, _ENTRY[0][1] - 10), (_w_end + 10, _ENTRY[0][1])] + _ENTRY[1:-1] + [(_w_end + 10, _ENTRY[-1][1]), (_w_end, _ENTRY[-1][1] + 10)]   # apron flares
_entry = _Poly([(x + _shift if x > _w_end + 12 else x, y) for x, y in _ENTRY]).buffer(0)
_lot = _union([_lot, _entry]).buffer(0.01).buffer(-0.01).simplify(0.3)
print("entry drive: width ft", round(abs(_sk(270, 800)[1] - _sk(270, 745)[1]), 1), "| west end x", _w_end)
# The one-way loop now follows the south loop: in past the carport, north up the east side and the east leg, west
# along the north aisle, south down the west leg, then south-east along the angled stalls back toward the carport.
for _c in C:
    if _c["id"] == "loop-parking":
        _xe_, _xw_, _yn_ = _c["pts"][0][0], _c["pts"][2][0], _c["pts"][1][1]
        _c["pts"] = [list(_sk(940, 1120)), [_xe_, _sk(1105, 830)[1]], [_xe_, _yn_], [_xw_, _yn_], [_xw_, _sk(590, 937)[1]], list(_sk(816, 1089)), list(_sk(870, 1128))]
NOTES_ = []                                       # the old "in / out" notes no longer apply
_P = by_id["parking"]
_P["outline"] = [[round(x, 1), round(y, 1)] for x, y in _lot.exterior.coords][:-1]
_P["island_poly"] = [[round(x, 1), round(y, 1)] for x, y in _island.exterior.coords][:-1]
_P["island"]["label_at"] = [round(_island.centroid.x, 1), round(_island.centroid.y, 1)]
_P["stalls_extra"] = [[list(q) for q in st] for st in SOUTH_STALLS]
n_stalls += len(SOUTH_STALLS)
_P["note"] = f"{n_stalls} spaces"
print("south loop: carport fit within", round(_sk_err, 1), "ft | scale px/ft", round(1 / abs(_MS), 2), "| rotation", round(__import__("math").degrees(__import__("cmath").phase(_MS)), 1),
      "| lot outline pts", len(_P["outline"]), "| stalls", n_stalls)

print("residence sides ft:", [round(abs(_r[i] - _r[(i + 1) % 4]) * _sf.FT_PER_PT / abs(_sf.M_FP)) for i in range(4)])
print("red house and horticulture (diagram ft):", by_id["existing-red-house"]["outline"][:3], "...", by_id["horticulture"]["outline"],
      "| horticulture sides ft:", [round(abs(_h[i] - _h[(i + 1) % 4]) * _sf.FT_PER_PT / abs(_sf.M_FP)) for i in range(4)])
E.sort(key=lambda e: 0 if e["id"].startswith("turnout") else 1)   # turnouts are drawn first, behind the barns
# the cross drive now lines up with the existing pens; its arrow stops short of them
for c in C:
    if c["id"] == "drive-cross":
        c["pts"][1][0] = min(c["pts"][1][0], x_col - 6)
    if c["id"] == "an-pens":            # existing pens (fixed) up into the shifted turnout A
        xm = (max(x_col, ta["x"]) + min(EAST, ta["x"] + ta["w"])) / 2
        c["pts"] = [[xm, y_pens + 8], [xm, y_pens - 30]]
def _on(pt_, c2):
    q = c2["pts"]
    for (ax, ay), (bx, by) in zip(q, q[1:]):
        L2 = (bx - ax) ** 2 + (by - ay) ** 2
        t_ = max(0, min(1, ((pt_[0] - ax) * (bx - ax) + (pt_[1] - ay) * (by - ay)) / L2)) if L2 else 0
        if ((ax + t_ * (bx - ax) - pt_[0]) ** 2 + (ay + t_ * (by - ay) - pt_[1]) ** 2) ** 0.5 < 1.5:
            return True
    return False
for c in C:
    if c["kind"] == "service":
        c["heads"] = [not any(_on(end, o) for o in C if o is not c and o["kind"] != "animal") for end in (c["pts"][0], c["pts"][-1])]
STALLS_BOX = [LOT_X0 + DX, y_park + DY, LOT_X1 + DX, y_s_row + STALL_D + DY]
CROSS_DRIVE_BOX = [x_small + DX, y_drive + DY, x_col + DX, y_drive + LANE + DY]

# The opening view is held tight on the barnyard (architect, 2026-10-13): from the west side of the cattle handling
# yard to the dimension strings on the north and east. The holding pens to the west and the Red House, horticulture
# and residence to the south are drawn and come into view when the viewer pans; they do not widen the frame.
pad = 8
_core = [e for e in E if not e.get("context") and not e.get("holding")]
xs = [v for e in _core for v in (e["x"], e["x"] + e["w"])] + [q[0] for c in C for q in c["pts"]]
ys = [v for e in _core for v in (e["y"], e["y"] + e["h"])] + [q[1] for c in C for q in c["pts"]]
view = None   # set once the dimension strings exist (below)

# dimension strings. North string: across the top of the new work. Small barn: at the extension's north end.
# East string: complete, from the north end of cattle barn B down to the south end of the existing barn.
def dim(label, x1, y1, x2, y2):
    return {"label": label, "x1": x1, "y1": y1, "x2": x2, "y2": y2}
yt = yB + DY - 24
xe = EAST + 12
cb, ca = by_id["cattle-b"], by_id["cattle-a"]
ext = by_id["small-b"]
dims = [
    dim(f"{SMALL_W}'", ext["x"], ext["y"] - 10, ext["x"] + ext["w"], ext["y"] - 10),
    dim(f"{LANE}'", x_west_lane + DX, yt, x_mid + DX, yt),
    dim(f"{ARENA_W}'", x_mid + DX, yt, x_east_lane + DX, yt),
    dim(f"{LANE}'", x_east_lane + DX, yt, x_cattle + DX, yt),
    dim(f"{CATTLE_W}'", x_cattle + DX, yt, x_col + DX, yt),
    dim(f"{EAST - (x_col + DX):g}'", x_col + DX, yt, EAST, yt),
]
string = [cb["y"], cb["y"] + cb["h"], ca["y"], ca["y"] + ca["h"], y_pens + PEN_D, y_barn, SOUTH]
for a_, b_ in zip(string, string[1:]):
    if b_ - a_ > 0.5:
        dims.append(dim(f"{b_ - a_:g}'", xe, a_, xe, b_))
_dxs = [v for d in dims for v in (d["x1"], d["x2"])] + xs
_dys = [v for d in dims for v in (d["y1"], d["y2"])] + ys + [n_["y"] + 2 for n_ in NOTES_]      # and the loop's in/out notes
# dimension text sits about 9' outside its line (above the north string, right of the east string)
view = [min(_dxs) - pad, min(_dys) - pad - 9, max(_dxs) - min(_dxs) + 2 * pad + 9, max(_dys) - min(_dys) + 2 * pad + 9]

data = {
    "units": "feet", "view": view, "north_cw_from_up": -17, "elements": E, "drives": DRIVES, "circulation": C, "dims": dims,
    "notes": NOTES_, "shift_ft": [DX, DY], "stalls_box": STALLS_BOX, "cross_drive_box": CROSS_DRIVE_BOX,
    "counts": {"cattle_pens": {"1": 7, "2": 21, "3": 35}, "small_animal_pens_per_barn": 2 * (MOD // SA_PEN_W), "small_animal_pens": {"2": 2 * (MOD // SA_PEN_W), "3": 2 * (MOD // SA_PEN_W) + 2 * (EXT // SA_PEN_W)}, "parking": n_stalls},
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
    for q in e.get("stalls_extra", []):
        out.append('<polygon points="' + " ".join(f"{px},{py}" for px, py in q) + '"/>')
    if e.get("island_poly"):
        out.append('<polygon points="' + " ".join(f"{px},{py}" for px, py in e["island_poly"]) + f'" fill="{P["water"]["tint"]}"/>')
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
