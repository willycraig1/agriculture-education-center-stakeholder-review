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
CATTLE_W = 2 * PEN_D + AISLE          # 62' (the original layout's barn; it also sets the survey-fixed east column)
# Option B cattle barns: a 16' tractor aisle (owner, 2026-10-19), 64' deep, as the McIntosh Ag Center cattle barn
# (source/Clark Farm Study Plan-A2.0 Cattle Barn Reference.pdf)
CATTLE_AISLE = 16
CATTLE_W_B = 2 * PEN_D + CATTLE_AISLE
SMALL_W = 36
SA_PEN_W, SA_PEN_D = 6, 10
SA_AISLE = 8                          # 8' aisle (owner, 2026-10-19; was the 16' left between the pen rows)
SA_EDGE = (SMALL_W - 2 * SA_PEN_D - SA_AISLE) / 2   # 4' strip between the pens and the curtain line, as the reference barn
SA_ROWS = [[SA_EDGE, SA_PEN_D], [SA_EDGE + SA_PEN_D + SA_AISLE, SA_PEN_D]]
SA_DOG = 12                           # dogtrot, one 12' bay (owner, 2026-10-19; was 15')
SA_B_L = 48                           # small animal barn B, four 12' bays (owner, 2026-10-19)
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
small_pens = {"n": MOD // SA_PEN_W, "w": SA_PEN_W, "rows": SA_ROWS, "vertical": True}

# Level 1
add("existing-barn", "Existing barn", EAST - EX_W, y_barn, EX_W, EX_D, "swine", 1, note="About 32 hog pens",
    becomes={"2": {"use": "circulation", "note": "Storage"}})
# The 7 existing pens run the barn's length, flush with its west face (survey; architect's sheet A2.0 Existing Barn,
# 2026-10-19): 80.4' in all, about 11.5' a pen. Earlier drawings had them on the 84' module, 3.6' proud of the barn.
add("existing-pens", "7 existing cattle pens", EAST - EX_W, y_pens, EX_W, PEN_D, "cattle", 1, pens={"n": 7, "w": round(EX_W / 7, 3), "rows": [[0, PEN_D]]})
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
    pens={"n": EXT // SA_PEN_W, "w": SA_PEN_W, "rows": SA_ROWS, "vertical": True})
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
    dict(id="an-pens", kind="animal", label="", pts=[[EAST - EX_W / 2, y_pens + 8], [EAST - EX_W / 2, y_pens - 30]]),
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
_M, _T = _sf.diagram_transform(EAST - EX_W / 2, y_pens)      # pinned at the middle of the existing pens' north edge
_to_d = lambda q: [round(v, 1) for v in (lambda z: (z.real, z.imag))((complex(*q) - _T) / _M)]
def _ext(id_, label, pts, use, kind, note, **extra):
    xs_, ys_ = [q[0] for q in pts], [q[1] for q in pts]
    add(id_, label, min(xs_), min(ys_), max(xs_) - min(xs_), max(ys_) - min(ys_), use, 1, kind=kind, note=note, outline=pts, context=True, **extra)
    by_id[id_] = E[-1]
_edits = json.load(open(os.path.join(_sf.OUT, "data", "site-edits.json")))
_rh = max(_edits["structures"], key=lambda s_: (max(q[0] for q in s_["pts"]) - min(q[0] for q in s_["pts"])) * (max(q[1] for q in s_["pts"]) - min(q[1] for q in s_["pts"])) if 1180 < s_["pts"][0][0] < 1240 and 340 < s_["pts"][0][1] < 400 else 0)
_ext("existing-red-house", "Red House", [_to_d(q) for q in _rh["pts"][:-1]], "education", "building", "")
# The Red House's open canopies, as on the site map (architect, 2026-10-14): the carport and the two porches, from the
# survey's overhang lines (BUILDING OH). The carport is the overhang rectangle south-west of the house; the porches
# are closed against the house walls (survey coordinates). Drawn tinted with a dashed outline, like the site map.
from shapely.geometry import MultiPoint as _MPt
_sp = lambda x, y: (lambda z: (z.real, z.imag))(_sf.M_SP * complex(x, y) + _sf.T_SP)
_ohp = [_sp(q.x, q.y) for d_ in _sf.cadpdf.export(_sf.SURVEY, ["BUILDING OH"]).get("BUILDING OH", []) for it_ in d_["items"] if it_[0] == "l" for q in it_[1:3]]
_cpp = [q for q in _ohp if 1220 < q[0] < 1243 and 376 < q[1] < 399]
if len(_cpp) >= 4:
    _ext("existing-carport", "Carport", [_to_d(q) for q in list(_MPt(_cpp).minimum_rotated_rectangle.exterior.coords)[:-1]], "education", "canopy", "")
for _id, _q in (("existing-porch-nw", [(1341.02, 1135.55), (1352.45, 1126.43), (1354.94, 1129.49), (1343.57, 1138.7)]),
                ("existing-porch-ne", [(1363.58, 1122.5), (1365.74, 1120.76), (1374.26, 1131.29), (1372.1, 1133.03)])):
    _ext(_id, "", [_to_d(_sp(x, y)) for x, y in _q], "education", "canopy", "")
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
# The Red House's Level 3 addition (owner, 2026-10-20): the instructional classroom / event space with its restroom and
# storage core, east of the house, square to true north, as placed on the study plan (sheet A0.1: the core's walls,
# P-WALL, and the classroom's open-sided outline, P-BELOW-LIGHT; study-plan points), with the entry canopy on its west
# side facing the house (P-ABOVE). The patio and walkway between them are not drawn.
_stp = lambda x, y: _to_d((lambda z: (z.real, z.imag))(_sf.M_TP * complex(x, y) + _sf.T_TP))
_add_o = [_stp(x, y) for x, y in ((1521.2, 1185.6), (1679.3, 1185.6), (1679.3, 1259.2), (1521.2, 1259.2))]
_xs_a, _ys_a = [q[0] for q in _add_o], [q[1] for q in _add_o]
add("red-house-addition", "Red House addition", min(_xs_a), min(_ys_a), max(_xs_a) - min(_xs_a), max(_ys_a) - min(_ys_a), "education", 3,
    note="Classroom / event space", outline=_add_o)
by_id["red-house-addition"] = E[-1]
_cn_o = [_stp(x, y) for x, y in ((1503.5, 1212.8), (1521.2, 1212.8), (1521.2, 1233.1), (1503.5, 1233.1))]
add("red-house-addition-canopy", "", min(q[0] for q in _cn_o), min(q[1] for q in _cn_o), max(q[0] for q in _cn_o) - min(q[0] for q in _cn_o),
    max(q[1] for q in _cn_o) - min(q[1] for q in _cn_o), "education", 3, kind="canopy", note="", outline=_cn_o, context=True)
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
# Laid out on the Red House's own grid (architect, 2026-10-14: edges parallel, registered to the Red House): the
# Red House, its carport, the angled stall row and the horticulture strip are all square to one another, about 34
# degrees off this diagram's grid. u runs along the stall row (south-east), n across it (south-west); the origin is
# on the stall fronts. The sketch only sets where the stall fronts lie.
_f0, _f1 = complex(*_sk(530, 962)), complex(*_sk(862, 1183))
_U = (_f1 - _f0) / abs(_f1 - _f0)
# The grid's angle comes from the Red House itself, not the sketch (owner, 2026-10-20: the south loop parallel and
# perpendicular to the front of the house): the length-weighted mean direction of its walls, folded onto one quarter
# turn. The sketch read about 0.7 degrees off. The origin stays on the sketch's stall fronts.
import cmath as _cm, math as _mt
_rh_o = by_id["existing-red-house"]["outline"]
_vec = sum(_mt.hypot(b_[0] - a_[0], b_[1] - a_[1]) * _cm.exp(4j * _cm.phase(complex(b_[0] - a_[0], b_[1] - a_[1])))
           for a_, b_ in zip(_rh_o, _rh_o[1:] + _rh_o[:1]))
_Uh = _cm.exp(1j * _cm.phase(_vec) / 4)                                   # one of the four wall directions
_Uh = max((_Uh * 1j ** k for k in range(4)), key=lambda z: (z * _U.conjugate()).real)   # the one nearest the sketch's u
print("south loop grid: sketch", round(_mt.degrees(_cm.phase(_U)), 2), "deg -> Red House walls", round(_mt.degrees(_cm.phase(_Uh)), 2), "deg")
_U = _Uh; _N = _U * 1j                                                    # n points south-west, away from the island
_xy = lambda u, n: (lambda z: (round(z.real, 1), round(z.imag, 1)))(_f0 + _U * u + _N * n)
_uv = lambda x, y: (lambda d: ((d * _U.conjugate()).real, (d * _N.conjugate()).real))(complex(x, y) - _f0)
# The drive past the Red House is the one stretch of the loop that is one-way: 13' wide, 5' off the building to
# leave room for an accessible sidewalk (architect, 2026-10-14). There is no turn-out to the carport.
AISLE_S, CURB, RH_SETBACK, DIAG_W = 24, 2, 5, 13
_u_cp = min(_uv(z.real, z.imag)[0] for z in _cpd)                          # carport's west face: the drive runs into it
_u_rh = min(_uv(*q)[0] for q in by_id["existing-red-house"]["outline"])      # Red House's westernmost face
_ue = _u_rh - RH_SETBACK                                                   # east edge of the one-way drive, 5' off the Red House
_ui = _ue - DIAG_W                                                         # its west edge
def _y_at(x, u):                                                           # y where the vertical x = const reaches the given u
    return round((u - _uv(x, 0)[0]) / _U.imag, 1)
def _y_at_n(x, n):
    n0 = _uv(x, 0)[1]; return round((n - n0) / _N.imag, 1)
_u0 = _ue - 90                                                             # nine 10' stalls, the row ending at the one-way drive
SOUTH_STALLS = [[_xy(_u0 + 10 * i, 0), _xy(_u0 + 10 * (i + 1), 0), _xy(_u0 + 10 * (i + 1), STALL_D), _xy(_u0 + 10 * i, STALL_D)] for i in range(9)]
_u9 = _u0 + 90
_south = _Poly([(_lx0, _row_back), (_lx1, _row_back), (_lx1, _y_at(_lx1, _ue)), _xy(_ue, STALL_D), _xy(_u0, STALL_D), _xy(_u0, 0),
                (_lx0, _y_at_n(_lx0, 0))]).buffer(0)
# island: between the legs, south of the stall rows, inside the curb of the diagonal drive and the south aisle
_island = _Poly([_xy(_ui - CURB, -AISLE_S - CURB), _xy(_ui - CURB, -400), _xy(-400, -400), _xy(-400, -AISLE_S - CURB)]).intersection(
    _box(XW1 + DX + CURB, _row_back, XE0 + DX - CURB, 9999))
_island_r20 = _island.buffer(-20, join_style=1).buffer(20, join_style=1)
_island = _island.buffer(-4, join_style=1).buffer(4, join_style=1)
# the south corner is the inside of the turn from the stall aisle up the one-way drive: a 20' radius there
_cS = _Pt(*_xy(_ui - CURB, -AISLE_S - CURB))
_island = _island.difference(_cS.buffer(40).difference(_island_r20))
# A bank of five stalls between the existing barn and the Red House (architect, 2026-10-14), bringing the lot to
# 50. They are on the Red House grid, square to the one-way drive and opening off its line carried north: the drive
# is widened there to a 24' aisle in front of them. They start 12' north of the Red House's north-west corner so
# the accessible walk can pass between.
BANK_N0 = -150
BANK_STALLS = [[_xy(_ue, BANK_N0 - 10 * i), _xy(_ue, BANK_N0 - 10 * (i + 1)), _xy(_ue + STALL_D, BANK_N0 - 10 * (i + 1)), _xy(_ue + STALL_D, BANK_N0 - 10 * i)] for i in range(5)]
_bank_aisle = _Poly([_xy(_ue - AISLE_S, BANK_N0 + 30), _xy(_ue, BANK_N0 + 30), _xy(_ue, BANK_N0 - 50), _xy(_ue - AISLE_S, BANK_N0 - 50)])
# paving: the aisle and stalls, filled back to the east leg's edge so no slivers are left between the two grids
_bank_paving = _MPt(list(_bank_aisle.exterior.coords) + [BANK_STALLS[0][0], BANK_STALLS[-1][1], BANK_STALLS[-1][2], BANK_STALLS[0][3],
                        (_lx1, _y_at_n(_lx1, BANK_N0 - 50)), (_lx1, _y_at_n(_lx1, BANK_N0 + 30))]).convex_hull
_lot = _union([_box(_lx0, by_id["parking"]["y"], _lx1, _row_back), _south, _bank_paving]).buffer(0.01).buffer(-0.01).simplify(0.3)
_uc = _ue - DIAG_W / 2
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
        # west along the north aisle, south down the west leg, south-east along the stalls, north up the one-way
        # drive past the Red House and on up the east leg
        _c["pts"] = [[_xe_ - 14, _yn_], [_xw_, _yn_], [_xw_, _y_at_n(_xw_, -AISLE_S / 2)], list(_xy(_uc, -AISLE_S / 2)),
                     [_xe_, _y_at(_xe_, _uc)], [_xe_, _yn_ + 16]]
NOTES_ = []                                       # the old "in / out" notes no longer apply
_P = by_id["parking"]
_P["outline"] = [[round(x, 1), round(y, 1)] for x, y in _lot.exterior.coords][:-1]
# The island is cut out of the lot's paving (its edge is the curb), and the swale itself is drawn inside it, set
# back 5' from the curb (architect, 2026-10-14: 4' to 6').
SWALE_SETBACK = 5
_P["holes"] = [[[round(x, 1), round(y, 1)] for x, y in _island.exterior.coords][:-1]]
_swale = _island.buffer(-SWALE_SETBACK, join_style=1)
# kept clear of the surveyed trees in the island (architect, 2026-10-14): each tree's drawn canopy plus 3'
_uft = _sf.FT_PER_PT / abs(_sf.M_FP)
_tr = []
for _src_, _x_, _y_, _s_ in _sf.trees:
    _z = (_sf.M_FP * complex(_x_, _y_) + _sf.T_FP - _T) / _M
    if _island.buffer(15).contains(_Pt(_z.real, _z.imag)):
        _tr.append(_Pt(_z.real, _z.imag).buffer((5.2 if _s_ > 20 else 3.8) * _uft + 3))
if _tr:
    _swale = _swale.difference(_union(_tr)).buffer(-2, join_style=1).buffer(2, join_style=1)
    _swale = max(getattr(_swale, "geoms", [_swale]), key=lambda g: g.area)
print("swale kept clear of", len(_tr), "trees | swale sf", round(_swale.area))
_swale = _swale.simplify(0.3)
_P["island_poly"] = [[round(x, 1), round(y, 1)] for x, y in _swale.exterior.coords][:-1]
_P["island"]["label_at"] = [round(_island.centroid.x, 1), round(_island.centroid.y, 1)]
_P["stalls_extra"] = [[list(q) for q in st] for st in SOUTH_STALLS]
_P["stalls_extra"] = _P["stalls_extra"] + [[list(q) for q in st] for st in BANK_STALLS]
n_stalls += len(SOUTH_STALLS) + len(BANK_STALLS)
# ---- accessible walk, Red House to cattle barn A: first pass (architect, 2026-10-14). 5' wide. It runs in the 5'
# strip between the Red House and the one-way drive, crosses between the Red House's north-west corner and the
# parking bank, passes behind the bank, then turns square to the barnyard grid: west of the existing barn and
# its pens, and along the north edge of the cross drive to the south-east corner of cattle barn A.
_ab = by_id["cattle-a"]
_wD = _xy(_ue + STALL_D + 2.5, BANK_N0 - 55)
_x_wpens = min(by_id["existing-barn"]["x"], by_id["existing-pens"]["x"]) - 8.5
WALK = [_xy(_ue + 2.5, -45), _xy(_ue + 2.5, BANK_N0 + 5.5), _xy(_ue + STALL_D + 2.5, BANK_N0 + 5.5), _wD,
        (_x_wpens, _wD[1]), (_x_wpens, _ab["y"] + _ab["h"] + 2.5), (_ab["x"] + _ab["w"] - 2, _ab["y"] + _ab["h"] + 2.5)]
from shapely.geometry import LineString as _LS
_walk = _LS(WALK).buffer(2.5, cap_style=2, join_style=2).simplify(0.2)
_wx_, _wy_ = [q[0] for q in WALK], [q[1] for q in WALK]
add("walk", "", min(_wx_), min(_wy_), max(_wx_) - min(_wx_), max(_wy_) - min(_wy_), "circulation", 1, kind="walk", note="",
    outline=[[round(x, 1), round(y, 1)] for x, y in _walk.exterior.coords][:-1], context=True)
by_id["walk"] = E[-1]
print("accessible walk ft:", round(_LS(WALK).length))

# =============================================================================================================
# OPTION B (2026-10-14), after the ag expert's feedback: source/NEW SITE PLAN OPTION 10-14 SKETCH.jpg.
# Option A (everything above, as it stood) is archived: git tag option-a-2026-10-14, archive/option-a-2026-10-14/.
# The parking lot, Red House, horticulture, residence and walk carry over from Option A (to be fitted to this scheme
# later); the barnyard itself is replaced. Coordinates here are final (no shift). Architect's rules for Option B:
#   - cattle barns A (Level 2) and B (Level 3) side by side in one row along the north, long sides east-west, pens
#     on both sides of an east-west tractor aisle; turnouts 36' deep off their north sides
#   - holding pens 1 to 5 east of cattle barn A, down to the existing pens; the Bud Box and chute in the south-west
#     corner of that block with a working alley on its west side
#   - second row: small animal barns B (Level 3) and A (Level 2) (also called the hog barns; either use), feed
#     storage, and the arena below cattle barn A; a turnout 36' deep west of small animal barn B
#   - 24' clear between all buildings
# Sizes are this deck's standard ones (cattle barn 84' x 62', arena 84' x 50', small animal barn 36' wide); the
# sketch is freehand, so positions follow its arrangement, not its proportions. The holding pens are sized from
# the sketch against the existing pens it shows beside them.
OPTION = "B"
_drop = {"cattle-a", "cattle-b", "small-a", "small-b", "arena", "feed-1", "feed-2", "turnout-cattle-a", "turnout-cattle-b",
         "turnout-small-a", "turnout-small-b", "handling", "trailer-stop", "holding-1", "holding-2", "holding-3", "holding-4", "walk"}
E[:] = [e for e in E if e["id"] not in _drop]
by_id = {e["id"]: e for e in E}
GAP, TURN_D = LANE, 36
_ep = by_id["existing-pens"]                                     # 199.6..280, 216..240 (fixed, on the survey)
Y_ROW1 = _ep["y"] - ARENA_W - GAP - CATTLE_W_B                     # = 78
X_HOLD = 170                                                     # holding block's west edge = cattle barn A's east wall
XA = X_HOLD - MOD                                                # cattle barn A 86..170
XB = XA - GAP - MOD                                              # cattle barn B -22..62
Y_ROW2 = Y_ROW1 + CATTLE_W_B + GAP                               # arena row top: 166
cattle_pens_h = {"n": 7, "w": PEN_W, "rows": [[0, PEN_D], [PEN_D + CATTLE_AISLE, PEN_D]], "vertical": False}
add("cattle-a", "Cattle barn A", XA, Y_ROW1, MOD, CATTLE_W_B, "cattle", 2, note="14 pens", pens=cattle_pens_h)
add("cattle-b", "Cattle barn B", XB, Y_ROW1, MOD, CATTLE_W_B, "cattle", 3, note="14 pens", pens=cattle_pens_h)
add("turnout-cattle-a", "Turnout", XA, Y_ROW1 - TURN_D, MOD, TURN_D, "arena", 2, kind="yard")
add("turnout-cattle-b", "Turnout", XB, Y_ROW1 - TURN_D, MOD, TURN_D, "arena", 3, kind="yard")
# two 4-row x 24' fixed aluminium bleachers along the north side, inside the columns (owner, 2026-10-19; as the
# McIntosh Ag Center pavilion), 12' in from each end with 12' between them
add("arena", "Arena", XA, Y_ROW2, MOD, ARENA_W, "arena", 3, note="84' x 50'",
    zones=[dict(label="Bleachers", x=12, y=0.5, w=24, h=7, fill=True), dict(label="Bleachers", x=48, y=0.5, w=24, h=7, fill=True)])
SA_L = 48                                                        # small animal barns 36' x 48', bottoms in line with the arena
y_sa = _ep["y"] - SA_L
sa_pens = {"n": SA_L // SA_PEN_W, "w": SA_PEN_W, "rows": SA_ROWS, "vertical": True}
FS_W, FS_L = 16, 40                                              # feed storage: two 8' x 40' containers side by side
x_fs = XA - GAP - FS_W
x_sa_a = x_fs - GAP - SMALL_W
x_sa_b = x_sa_a - GAP - SMALL_W
add("feed", "Feed storage", x_fs, _ep["y"] - FS_L, FS_W, FS_L, "circulation", 2, note="two 8' x 40' containers")
add("small-a", "Small animal barn A", x_sa_a, y_sa, SMALL_W, SA_L, "swine", 2, note=f"{2 * (SA_L // SA_PEN_W)} pens", pens=sa_pens)
add("small-b", "Small animal barn B", x_sa_b, y_sa, SMALL_W, SA_L, "small_animal", 3, note=f"{2 * (SA_L // SA_PEN_W)} pens", pens=sa_pens)
add("turnout-small-b", "Turnout", x_sa_b - TURN_D, y_sa, TURN_D, SA_L, "arena", 3, kind="yard")
# Handling yard (architect, 2026-10-14): the Bud Box slide's yard, mirrored east-west so the trailer bay is on its
# west side, in the lane east of the arena where the sketch's arrow runs north. Same geometry as that slide (72' x
# 84' yard: Bud Box and lead-up alley along the north, single-file alley and chute on the scale, the holding pen
# wrapping the chute with chamfered corners; 24'-deep tapered trailer bay). The yard's holding pen is pen 1; pens
# 2 to 5 sit north of the yard in two columns either side of an 8' alley, as in the sketch. All Level 1.
_ex = _ep["x"] + _ep["w"]                                        # 280: east edge, in line with the existing pens
# Sized for four cattle (architect, 2026-10-14): half the slide's 72' x 84' in each direction, 36' x 42', with the
# corner chamfers as single 12' panels (8.5' each way). Bud Box 20' x 12' and the 16' single-file alley and chute
# are kept; the lead-up alley is the 16' left beside the Bud Box. The bay matches the yard's depth.
HY_W, HY_D, BAY_W, CH = 36, 42, 24, 8.5
_hx0, _hy0 = X_HOLD + BAY_W, _ep["y"] - HY_D                      # yard 194..230, 174..216
mx = lambda x: HY_W - x                                          # mirror within the yard
_yard = [[0, 0], [HY_W, 0], [HY_W, HY_D - CH], [HY_W - CH, HY_D], [CH, HY_D], [0, HY_D - CH]]
_pen = [[0, 12], [16, 12], [16, 28], [15.3, 28], [15.3, 37], [19.3, 37], [19.3, 28], [18.6, 28], [18.6, 12], [HY_W, 12],
        [HY_W, HY_D - CH], [HY_W - CH, HY_D], [CH, HY_D], [0, HY_D - CH]]
_bay = [[HY_W, 0], [HY_W + 10, 0], [HY_W + 24, 13], [HY_W + 24, HY_D - 13], [HY_W + 10, HY_D], [HY_W, HY_D]]
add("handling", "Handling", _hx0, _hy0, HY_W, HY_D, "cattle", 1, kind="yard", note="Bud Box, chute, scale",
    outline=[[_hx0 + mx(x), _hy0 + y] for x, y in _yard], zones=[
    dict(label="Holding pen", poly=[[mx(x), y] for x, y in _pen], at=[mx(27), 33]),
    dict(label="Lead-up", x=mx(HY_W), y=0, w=HY_W - 20, h=12),
    dict(label="Bud Box", x=mx(20), y=0, w=20, h=12, fill=True),
    dict(label="", x=mx(18.6), y=12, w=2.6, h=16),
    dict(label="Chute", x=mx(19.3), y=28, w=4, h=9, fill=True, side=True)])
add("trailer-stop", "Trailer bay", X_HOLD, _hy0, BAY_W, HY_D, "circulation", 1, kind="yard", note="pull-through, gate at each end",
    outline=[[_hx0 + mx(x), _hy0 + y] for x, y in _bay])
# pens 1 to 5 as in the sketch: 5 and 3 along the top, 4 and 2 below them, 1 beside the yard; two columns either
# side of an 8' alley in line with the yard's east side
_c1, _c2 = _hx0 + HY_W, _hx0 + HY_W + 8
_rm = (Y_ROW1 + _hy0) / 2
for n_, (x0_, y0_, x1_, y1_) in {5: (X_HOLD, Y_ROW1, _c1, _rm), 4: (X_HOLD, _rm, _c1, _hy0), 3: (_c2, Y_ROW1, _ex, _rm), 2: (_c2, _rm, _ex, _hy0),
                                 1: (_c2, _hy0, _ex, _ep["y"])}.items():
    add(f"holding-{n_}", f"Pen {n_}", x0_, y0_, x1_ - x0_, y1_ - y0_, "cattle", 1, kind="yard", note=f"{round((x1_ - x0_) * (y1_ - y0_)):,} sf")
by_id = {e["id"]: e for e in E}
# circulation: keep the parking loop; the rest follows the sketch
C[:] = [c for c in C if c["id"] in ("loop-parking", "loop-mid")]
_ya = Y_ROW1 + PEN_D + CATTLE_AISLE / 2
C += [
    dict(id="aisle-cattle", kind="service", label="Tractor aisle", pts=[[XB - 12, _ya], [X_HOLD + 6, _ya]]),
    dict(id="drive-loop", kind="loop", label="Service drive", pts=[[X_HOLD + 12, _ep["y"] + 20], [X_HOLD + 12, Y_ROW1 + CATTLE_W_B + GAP / 2],
                                                                     [XA - GAP / 2, Y_ROW1 + CATTLE_W_B + GAP / 2], [XA - GAP / 2, _ep["y"] + 18]]),
    dict(id="aisle-small-a", kind="service", label="", pts=[[x_sa_a + SMALL_W / 2, y_sa - 10], [x_sa_a + SMALL_W / 2, _ep["y"] + 10]]),
    dict(id="aisle-small-b", kind="service", label="", pts=[[x_sa_b + SMALL_W / 2, y_sa - 10], [x_sa_b + SMALL_W / 2, _ep["y"] + 10]]),
    dict(id="an-cattle-a", kind="animal", label="", pts=[[XA + MOD / 2, Y_ROW1 + 8], [XA + MOD / 2, Y_ROW1 - 30]]),
    dict(id="an-cattle-b", kind="animal", label="", pts=[[XB + MOD / 2, Y_ROW1 + 8], [XB + MOD / 2, Y_ROW1 - 30]]),
    dict(id="an-small-b", kind="animal", label="", pts=[[x_sa_b + 8, y_sa + SA_L / 2], [x_sa_b - 30, y_sa + SA_L / 2]]),
    dict(id="an-pens", kind="animal", label="", pts=[[_ep["x"] + 63, _ep["y"] + 8], [_ep["x"] + 63, _ep["y"] - 30]]),
]
NOTES_ = []
# the accessible walk carries over, its last leg re-aimed at cattle barn A: north between the arena and the
# handling alley, to the barn's south-east corner
_ab = by_id["cattle-a"]
_xw2 = X_HOLD + 6
_xw2 = XA - 2.5                                                   # just west of the arena, at the service drive's edge
WALK = WALK[:5] + [(_x_wpens, _ep["y"] + 12), (_xw2, _ep["y"] + 12), (_xw2, _ab["y"] + _ab["h"] + 2.5), (_ab["x"] + 20, _ab["y"] + _ab["h"] + 2.5)]
_walk = _LS(WALK).buffer(2.5, cap_style=2, join_style=2).simplify(0.2)
_wx_, _wy_ = [q[0] for q in WALK], [q[1] for q in WALK]
add("walk", "", min(_wx_), min(_wy_), max(_wx_) - min(_wx_), max(_wy_) - min(_wy_), "circulation", 1, kind="walk", note="",
    outline=[[round(x, 1), round(y, 1)] for x, y in _walk.exterior.coords][:-1], context=True)
by_id = {e["id"]: e for e in E}
E.sort(key=lambda e: 0 if e["id"].startswith("turnout") else 1)
print("option B: cattle row y", Y_ROW1, "| arena row y", Y_ROW2, "| west edge", x_sa_b - TURN_D, "| small animal pens per barn", 2 * (SA_L // SA_PEN_W))
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
# =============================================================================================================
# OPTION B, architect's edits (2026-10-14): drawings/ag-area-diagram2.svg, edited in Illustrator from this script's
# own diagram. Its geometry replaces the computed layout element by element. The file was exported with the
# diagram's view origin at (-118, 13), so diagram feet = svg + (-118, 13). Changes it carries: a two-way loop
# (service drive round the arena joined to the parking loop); no trailer enclosure; new bedding storage, compost
# area and dumpster enclosure; a grooming area in the arena; one small animal barn with a dogtrot between it and
# its Level 3 extension to the south; the parking bank removed; the turnouts widened; a walkway network.
import re as _re
AG_EDIT = os.path.join(ROOT, "drawings", "ag-area-diagram2.svg")
_EO = (-118, 13)
def _svg_rects(g):
    return [tuple(float(v) for v in m) for m in _re.findall(r'<rect class="[^"]*" x="([-\d.]+)" y="([-\d.]+)" width="([-\d.]+)" height="([-\d.]+)"', g)]
def _svg_pts(txt):
    v = [float(x) for x in txt.replace(",", " ").split()]
    return [[round(v[i] + _EO[0], 1), round(v[i + 1] + _EO[1], 1)] for i in range(0, len(v), 2)]
def _svg_path(d):
    toks = _re.findall(r"[MmLlHhVvZz]|-?\d*\.?\d+", d); rings, cur, x, y, cmd, i = [], [], 0.0, 0.0, None, 0
    while i < len(toks):
        t = toks[i]
        if t in "MmLlHhVvZz":
            cmd = t; i += 1
            if t in "Zz":
                rings.append(cur); cur = []
            continue
        if cmd in "Mm":
            a, b = float(toks[i]), float(toks[i + 1]); i += 2; x, y = (a, b) if cmd == "M" else (x + a, y + b); cur = [(x, y)]; cmd = "L" if cmd == "M" else "l"
        elif cmd in "Ll":
            a, b = float(toks[i]), float(toks[i + 1]); i += 2; x, y = (a, b) if cmd == "L" else (x + a, y + b); cur.append((x, y))
        elif cmd in "Hh":
            a = float(toks[i]); i += 1; x = a if cmd == "H" else x + a; cur.append((x, y))
        elif cmd in "Vv":
            a = float(toks[i]); i += 1; y = a if cmd == "V" else y + a; cur.append((x, y))
    return [[[round(px + _EO[0], 1), round(py + _EO[1], 1)] for px, py in r[:-1] if True] for r in rings]
if OPTION == "B" and os.path.exists(AG_EDIT):
    _sv = open(AG_EDIT).read()
    _grp = lambda gid: (_re.search(r'<g id="%s">(.*?)\n    </g>' % gid, _sv, _re.S) or [None, ""])[1] if _re.search(r'<g id="%s">' % gid, _sv) else ""
    def _set(id_, x, y, w, h, **kw):
        e = by_id[id_]; e.update(x=round(x + _EO[0], 1), y=round(y + _EO[1], 1), w=w, h=h, **kw)
        e.pop("outline", None) if "outline" not in kw else None
    for id_ in ("cattle-a", "cattle-b", "arena", "small-a", "turnout-cattle-a", "holding-1", "holding-2", "holding-3", "holding-4", "holding-5", "turnout-small-b"):
        r_ = _svg_rects(_grp(id_))
        if r_:
            _set(id_, *r_[0])
    _tb_ = _svg_pts(_re.search(r'<g id="turnout-cattle-b">\s*<polygon class="[^"]*" points="([^"]+)"', _sv).group(1))
    _set("turnout-cattle-b", min(q[0] for q in _tb_) - _EO[0], min(q[1] for q in _tb_) - _EO[1], max(q[0] for q in _tb_) - min(q[0] for q in _tb_), 36)
    # The cattle barns are 64' deep (24' pen rows either side of a 16' tractor aisle; owner, 2026-10-19), where the
    # architect's file has 62'. The 2' goes north, keeping 24' clear to the arena row; the turnouts move north with them.
    for id_ in ("cattle-a", "cattle-b"):
        _grow = CATTLE_W_B - by_id[id_]["h"]
        by_id[id_].update(y=round(by_id[id_]["y"] - _grow, 1), h=CATTLE_W_B)
    for id_ in ("turnout-cattle-a", "turnout-cattle-b"):
        by_id[id_]["y"] = round(by_id[id_]["y"] - _grow, 1)
    for id_ in ("holding-5", "holding-3"):                     # their north edge stays flush with the barns' north wall
        if abs(by_id[id_]["y"] - (by_id["cattle-a"]["y"] + _grow)) < 0.5:
            by_id[id_].update(y=by_id["cattle-a"]["y"], h=round(by_id[id_]["h"] + _grow, 1))
    _fd = _svg_rects(_grp("feed"))                                   # feed storage, then bedding storage
    _set("feed", *_fd[0])
    add("bedding", "Bedding storage", round(_fd[1][0] + _EO[0], 1), round(_fd[1][1] + _EO[1], 1), _fd[1][2], round(_fd[1][3]), "circulation", 2, note="")
    # Small animal barn A (Level 2) is both wings in the file, either side of a dogtrot. Small animal barn B (Level 3)
    # extends it south as far as the building code allows (architect, 2026-10-14): a Group U utility building of
    # Type VB construction is limited to 5,500 sf per story (IBC Table 506.2, no sprinklers or frontage increase).
    # The dogtrot is taken as roofed, so it counts toward the area.
    _sb = _svg_rects(_grp("small-b"))[0]
    _a1, _a2 = by_id["small-a"], by_id["small-b"]
    _set("small-b", *_sb)
    # the dogtrot is one 12' bay: barn A's north end holds, its south wing moves north (owner, 2026-10-19)
    _a2["y"] = round(_a1["y"] + _a1["h"] + SA_DOG, 1)
    _a2.update(id="small-a2", label="", use="swine", level=2, note=f"{2 * (SA_L // SA_PEN_W)} pens")
    _a1.update(label="Small animal barn A", note=f"{4 * (SA_L // SA_PEN_W)} pens, two wings")
    _dog = _a2["y"] - (_a1["y"] + _a1["h"])
    add("dogtrot", "", _a1["x"], _a1["y"] + _a1["h"], SMALL_W, _dog, "circulation", 2, kind="yard", note="")
    U_VB_MAX = 5500
    _used = SMALL_W * (_a1["h"] + _dog + _a2["h"])
    # Barn B: four 12' bays (owner, 2026-10-19). Barns A and B together pass the 5,500 sf one-storey base limit for
    # Group U, Type VB (IBC Table 506.2); the frontage increase (IBC 506.3) covers it (owner, 2026-10-19).
    B_L = SA_B_L
    _pb = {"n": B_L // SA_PEN_W, "w": SA_PEN_W, "rows": SA_ROWS, "vertical": True}
    add("small-b", "Small animal barn B", _a2["x"], _a2["y"] + _a2["h"], SMALL_W, B_L, "small_animal", 3,
        note=f"{2 * (B_L // SA_PEN_W)} pens; {round(_used + SMALL_W * B_L):,} sf in all", pens=_pb)
    _ts_ = by_id["turnout-small-b"]
    _ts_.update(id="turnout-small-a", level=2, h=round(_a2["y"] + _a2["h"] - _ts_["y"], 1))   # barn A's length
    add("turnout-small-b", "", _ts_["x"], _ts_["y"] + _ts_["h"], _ts_["w"], B_L, "arena", 3, kind="yard")
    # barn A's turnout divided in two by a fence on the dogtrot's centre line (owner, 2026-10-19)
    _yc = round(_a1["y"] + _a1["h"] + _dog / 2, 1)
    add("turnout-small-a2", "", _ts_["x"], _yc, _ts_["w"], round(_ts_["y"] + _ts_["h"] - _yc, 1), "arena", 2, kind="yard")
    _ts_["h"] = round(_yc - _ts_["y"], 1)
    SA_PENS = {"2": 4 * (SA_L // SA_PEN_W), "3": 4 * (SA_L // SA_PEN_W) + 2 * (B_L // SA_PEN_W)}
    print("small animal barn: A", _used, "sf (two wings and a", _dog, "ft dogtrot) | B", SMALL_W, "x", B_L, "| total", _used + SMALL_W * B_L, "sf of", U_VB_MAX)
    # handling yard as drawn (no trailer enclosure)
    by_id["handling"].update(label="", note="")                      # its zones name its parts; no overall label on the slide
    by_id["handling"]["outline"] = _svg_pts(_re.search(r'<g id="handling">\s*<polygon class="[^"]*" points="([^"]+)"', _sv).group(1))
    E[:] = [e for e in E if e["id"] != "trailer-stop"]
    # The holding block's west edge lines up with the existing barn's front (west face) (owner, 2026-10-19): the west
    # column (handling yard and Bud Box, pens 4 and 5) and the 8' alley move east. The east column (pens 1 to 3) runs
    # out to the end of the existing pens' lean-to roof, the "dog-ear" that carries on 13' past the barn's east wall
    # (93.4' from the barn front in all; architect's sheet A2.0 Existing Barn) (owner, 2026-10-20).
    _front = by_id["existing-barn"]["x"]
    _dx = round(_front - by_id["handling"]["x"], 1)
    HOLD_E = round(_front + 93.4, 1)                                  # the dog-ear's east end
    for id_ in ("handling", "holding-4", "holding-5"):
        e = by_id[id_]; e["x"] = round(e["x"] + _dx, 1)
        if e.get("outline"): e["outline"] = [[round(px + _dx, 1), py] for px, py in e["outline"]]
    # the 8' alley sits centred in the block (owner, 2026-10-20): two equal columns either side of it. The west column
    # (pens 4 and 5, the handling yard) widens to the alley; the Bud Box, lead-up, and chute keep their size and place.
    _col = round((HOLD_E - _front - 8) / 2, 1)
    _aw, _ae = round(_front + _col, 1), round(_front + _col + 8, 1)
    _hx_e = by_id["handling"]["x"] + by_id["handling"]["w"]            # handling yard's east edge, after the move
    for id_ in ("holding-4", "holding-5"):
        by_id[id_]["w"] = _col
    _hd = by_id["handling"]
    if _hd.get("outline"):
        _ymax = max(py for _, py in _hd["outline"]); _xmid = _hd["x"] + 18
        _hd["outline"] = [[_aw if abs(px - _hx_e) < 0.6 else (round(px + _aw - _hx_e, 1) if abs(py - _ymax) < 0.1 and px > _xmid else px), py]
                          for px, py in _hd["outline"]]      # the east wall and the south-east chamfer's corner move together
    _hd["w"] = _col
    for id_ in ("holding-1", "holding-2", "holding-3"):
        e = by_id[id_]; e["x"] = _ae; e["w"] = round(HOLD_E - _ae, 1)
        if e.get("outline"): e["outline"] = [[min(max(px, _ae), HOLD_E), py] for px, py in e["outline"]]
    # the dog-ear itself, drawn as an open canopy so the line reads: the lean-to's roof over the pens' front 12.5'
    # (it covers the 8' aisle and 12.5' of the pens, 20.5' off the barn's north wall), past the barn's east wall
    _eb = by_id["existing-barn"]; _yd0, _yd1 = _eb["y"] - 20.5, _eb["y"] - 8.0
    add("existing-dogear", "", _eb["x"] + _eb["w"], _yd0, round(HOLD_E - (_eb["x"] + _eb["w"]), 1), 12.5, "cattle", 1, kind="canopy", note="",
        outline=[[_eb["x"] + _eb["w"], _yd0], [HOLD_E, _yd0], [HOLD_E, _yd1], [_eb["x"] + _eb["w"], _yd1]], context=True)
    # cattle turnout A's east edge and the bedding storage follow the holding block to the barn front line: the bedding
    # fills the north end of the lane between cattle barn A and the holding pens, flush with the barns' north wall
    by_id["turnout-cattle-a"]["w"] = round(_front - by_id["turnout-cattle-a"]["x"], 1)
    _ca = by_id["cattle-a"]
    next(e for e in E if e["id"] == "bedding").update(x=round(_ca["x"] + _ca["w"], 1), y=_ca["y"], w=round(_front - (_ca["x"] + _ca["w"]), 1), h=12.0)
    for id_ in ("holding-1", "holding-2", "holding-3", "holding-4", "holding-5"):   # areas as drawn
        by_id[id_]["note"] = f'{round(by_id[id_]["w"] * by_id[id_]["h"]):,} sf'
    # grooming area inside the arena; compost and dumpster by the existing barn
    _gm = _re.search(r'Grooming Area.*?<rect class="[^"]*" x="([-\d.]+)" y="([-\d.]+)" width="([-\d.]+)" height="([-\d.]+)"', _sv, _re.S).groups()
    # the grooming area comes first, at Level 2, under a roof that the arena (Level 3) later grows from
    add("grooming", "Grooming", round(float(_gm[0]) + _EO[0], 1), round(float(_gm[1]) + _EO[1], 1), round(float(_gm[2]), 1), float(_gm[3]), "arena", 2, note="")
    _cp = _re.search(r'Compost Area.*?<rect class="[^"]*" x="([-\d.]+)" y="([-\d.]+)" width="([-\d.]+)" height="([-\d.]+)"', _sv, _re.S).groups()
    # compost and the dumpster enclosure line up on the existing barn's front (owner, 2026-10-19); one dumpster in a
    # 12' x 12' C-shaped enclosure open to the west, toward the drive
    add("compost", "Compost", by_id["existing-barn"]["x"], round(float(_cp[1]) + _EO[1], 1), round(float(_cp[2]), 1), float(_cp[3]), "circulation", 1, kind="yard", note="")
    add("dumpster", "Dumpster", by_id["existing-barn"]["x"], 324.0, 12.0, 12.0, "circulation", 1, note="enclosure")
    # parking: outline, island and stalls as drawn (the bank of five is gone)
    _pr = _svg_path(_re.search(r'<g id="parking">\s*<path class="[^"]*" d="([^"]+)"', _sv).group(1))
    _pkg = _grp("parking")
    # every 10' x 20' stall in the file, wherever it sits (the added stalls ended up in the circulation layer)
    _all_st = [r_ for r_ in _svg_rects(_sv) if abs(r_[2] - 10) < 0.2 and abs(r_[3] - 20) < 0.2]
    _stl = [[[round(x + _EO[0], 1), round(y + _EO[1], 1)] for x, y in ((r_[0], r_[1]), (r_[0] + r_[2], r_[1]), (r_[0] + r_[2], r_[1] + r_[3]), (r_[0], r_[1] + r_[3]))] for r_ in _all_st]
    # the central double row is carried one stall further east on each side, to match the north row (architect,
    # 2026-10-14; added here, not in the architect's file): skipped if the file already has them
    _have = {(q[0][0], q[0][1]) for q in _stl}
    _ne = max(q[1][0] for q in _stl if abs(q[0][1] - by_id["parking"]["y"]) < 0.5)        # north row's east end
    for _yr in sorted({q[0][1] for q in _stl if q[0][1] > by_id["parking"]["y"] + 30 and q[0][1] < 330}):
        _xe = max(q[1][0] for q in _stl if q[0][1] == _yr)
        while _xe + 10 <= _ne + 0.1 and (_xe, _yr) not in _have:
            _stl.append([[_xe, _yr], [_xe + 10, _yr], [_xe + 10, _yr + 20], [_xe, _yr + 20]]); _xe += 10
    _ang = [_svg_pts(m) for m in _re.findall(r'<polygon class="st3" points="([^"]+)"', _pkg)]
    _swl = _re.search(r'<polygon class="st2" points="([^"]+)"', _pkg)
    _pk = by_id["parking"]
    _pk.update(outline=_pr[0], holes=_pr[1:], rows=[], stalls_extra=_stl + _ang)
    if _swl:
        _pk["island_poly"] = _svg_pts(_swl.group(1))
    n_stalls = len(_stl) + len(_ang)
    # the dumpster enclosure is centred on the drive aisle it opens onto (owner, 2026-10-20): the aisle between the back of
    # the double stall row and the front of the row along the swale
    _dm = next(e for e in E if e["id"] == "dumpster")
    _backs = sorted({q[2][1] for q in _stl}); _fronts = sorted({q[0][1] for q in _stl})
    _a0_ = max((b for b in _backs if b <= _dm["y"] + _dm["h"] / 2 + 12), default=None)
    _a1_ = min((f for f in _fronts if _a0_ is not None and f > _a0_ + 1), default=None)
    if _a0_ is not None and _a1_ is not None:
        _dm["y"] = round((_a0_ + _a1_) / 2 - _dm["h"] / 2, 1)
        print("dumpster centred on its aisle:", _a0_, "to", _a1_, "-> y", _dm["y"])
    # Square the south loop to the front of the Red House, with the sidewalk flush against it (owner, 2026-10-20). The
    # front is the line of the house's westernmost wall and the front porch's outer edge (they are one line), about
    # 0.4 degrees off the walls' average; the loop takes its angle from it (_Uf along the stall row, _Nf across). The
    # one-way drive's outer edge sits 5' off the front, so the 5' sidewalk between them is flush with the house. The
    # stall row turns about its north-west front corner (its joint with the west leg); the drive edge's north end slides
    # along the edge it meets (its joint with the east leg); their corner is where the two lines meet. The nine angled
    # stalls are redrawn on the row; the swale island's two diagonal sides follow the side they face. The horticulture
    # area and the residence are set flush to the sidewalk's south corner.
    _near = lambda q: min(range(len(_pk["outline"])), key=lambda k: (_pk["outline"][k][0] - q[0]) ** 2 + (_pk["outline"][k][1] - q[1]) ** 2)
    _a0 = sorted(_ang, key=lambda q: q[0][0])
    if _a0:
        _r1 = lambda z: [round(z.real, 1), round(z.imag, 1)]
        _cand = [complex(*q) for q in by_id["existing-red-house"]["outline"] + (by_id.get("existing-porch-nw") or {}).get("outline", [])]
        _umin = min((z - _f0).real * _U.real + (z - _f0).imag * _U.imag for z in _cand)
        _fr = sorted([z for z in _cand if (z - _f0).real * _U.real + (z - _f0).imag * _U.imag < _umin + 1.0],
                     key=lambda z: (z - _f0).real * _N.real + (z - _f0).imag * _N.imag)
        _Nf = (_fr[-1] - _fr[0]) / abs(_fr[-1] - _fr[0])
        if (_Nf * _N.conjugate()).real < 0: _Nf = -_Nf
        _Uf = _Nf * -1j                                                    # along the row, so that _Nf = _Uf * 1j
        _F = complex(*_a0[0][0])                                           # stall row's north-west front corner
        _drot = _cm.phase(_Uf) - _cm.phase(complex(*_a0[0][1]) - _F)
        _kbw, _kce = _near(_a0[0][3]), _near(_a0[-1][2])
        _kdn = (_kce + 1) % len(_pk["outline"]); _knx = (_kdn + 1) % len(_pk["outline"])
        _D0, _DX = complex(*_pk["outline"][_kdn]), complex(*_pk["outline"][_knx])
        _depth = abs(complex(*_a0[0][3]) - complex(*_a0[0][0]))
        _BW = _F + _Nf * _depth
        _L0 = _fr[0] - _Uf * 5                                             # a point on the drive edge (5' off the front)
        _CE = _BW + _Uf * ((_L0 - _BW) * _Uf.conjugate()).real
        _e = _DX - _D0                                                     # the drive edge's north end slides along this edge
        _t = ((_L0 - _D0) * _Uf.conjugate()).real / ((_e * _Uf.conjugate()).real or 1e-9)
        _D = _D0 + _e * _t
        _pk["outline"][_kbw], _pk["outline"][_kce], _pk["outline"][_kdn] = _r1(_BW), _r1(_CE), _r1(_D)
        _new = []
        for q in _a0:
            a0_, a1_ = abs(complex(*q[0]) - _F), abs(complex(*q[1]) - _F)
            _new.append([_r1(_F + _Uf * a0_), _r1(_F + _Uf * a1_), _r1(_F + _Uf * a1_ + _Nf * _depth), _r1(_F + _Uf * a0_ + _Nf * _depth)])
        _pk["stalls_extra"] = _stl + _new
        _rowL, _drvL = _LS([_r1(_F), _r1(_CE)]), _LS([_r1(_CE), _r1(_D)])
        def _turn(q):                                                      # a diagonal-side vertex follows the side it faces
            if q[1] < _D0.imag + 0.2:
                return q
            if _rowL.distance(_Pt(*q)) < _drvL.distance(_Pt(*q)):
                return _r1(_F + (complex(*q) - _F) * _cm.exp(1j * _drot))
            return _r1(_D + (complex(*q) - _D0) * _cm.exp(1j * _drot))
        _pk["holes"] = [[_turn(q) for q in h_] for h_ in _pk["holes"]]
        if _pk.get("island_poly"):
            _pk["island_poly"] = [_turn(q) for q in _pk["island_poly"]]
        # horticulture and the residence, flush to the sidewalk's south corner, keeping their sizes
        _SC = _CE + _Uf * 5 + _Nf * 5
        _ho, _ro = by_id["horticulture"]["outline"], by_id["residence"]["outline"]
        _hl, _hd = abs(complex(*_ho[1]) - complex(*_ho[0])), abs(complex(*_ho[2]) - complex(*_ho[1]))
        _rw = abs(complex(*_ro[1]) - complex(*_ro[0]))
        _HNW = _SC - _Uf * _hl
        _hnew = [_r1(_HNW), _r1(_SC), _r1(_SC + _Nf * _hd), _r1(_HNW + _Nf * _hd)]
        _rnew = [_r1(_HNW - _Uf * _rw), _r1(_HNW), _r1(_HNW + _Nf * _hd), _r1(_HNW - _Uf * _rw + _Nf * _hd)]
        for id_, o_ in (("horticulture", _hnew), ("residence", _rnew)):
            by_id[id_].update(outline=o_, x=min(q[0] for q in o_), y=min(q[1] for q in o_),
                              w=round(max(q[0] for q in o_) - min(q[0] for q in o_), 1), h=round(max(q[1] for q in o_) - min(q[1] for q in o_), 1))
        _WEST_END = _HNW - _Uf * _rw                                       # the sidewalk runs on along the residence's north side
                                                                           # to its far corner (architect's edit, 2026-10-20)
        print("south loop squared to the Red House front: turned", round(_mt.degrees(_drot), 2), "deg; corner", _r1(_CE), "| drive edge 5' off the front")
    # grass parking (architect, 2026-10-14): the north stall row and the two middle rows, from the lot's west stall
    # edge to its east edge, are grass over a base rather than pavement; the south row and the drive aisles stay paved
    _g = [36.5, by_id["parking"]["y"], 170.0, 324.0]
    _pk["grass"] = [[_g[0], _g[1]], [_g[2], _g[1]], [_g[2], _g[3]], [_g[0], _g[3]]]
    _ng = sum(1 for q in _stl if _g[0] - 0.1 <= min(p_[0] for p_ in q) and max(p_[0] for p_ in q) <= _g[2] + 0.1 and _g[1] - 0.1 <= min(p_[1] for p_ in q) and max(p_[1] for p_ in q) <= _g[3] + 0.1)
    _pk["note"] = f"{n_stalls} spaces, {_ng} on grass"
    print("grass parking:", _ng, "stalls")
    # poultry: the unfinished barn (open-sided, on the survey as BUILDING OH), where the poultry stay at every Level;
    # shown so the walkway's connection to it reads. The walk is carried east from the network's strip along the
    # existing barn's north side to the barn's west face, 5' wide.
    _oh2 = [(_sf.M_SP * complex(q.x, q.y) + _sf.T_SP) for _d in _sf.cadpdf.export(_sf.SURVEY, ["BUILDING OH"]).get("BUILDING OH", [])
            for _it in _d["items"] if _it[0] == "l" for q in (_it[1], _it[2])]
    _oh2 = [(z.real, z.imag) for z in _oh2 if abs(z.real - 1177) < 25 and abs(z.imag - 264) < 25]
    _poul = [_to_d(q) for q in list(_MPt(_oh2).minimum_rotated_rectangle.exterior.coords)[:4]]
    _xs_p, _ys_p = [q[0] for q in _poul], [q[1] for q in _poul]
    add("existing-poultry", "Poultry", min(_xs_p), min(_ys_p), max(_xs_p) - min(_xs_p), max(_ys_p) - min(_ys_p), "small_animal", 1, note="unfinished barn",
        outline=_poul, context=True)
    # walkway network as drawn
    _wk = _svg_pts(_re.search(r'<g id="walk">\s*<polygon class="[^"]*" points="([^"]+)"', _sv).group(1))
    # the walk's apron west of the existing pens ends on the barn front line, like the holding block above it (owner,
    # 2026-10-20); the architect's file has it 3.6' short of the line
    _wk = [[by_id["existing-barn"]["x"] if abs(px - 196.0) < 0.6 and by_id["existing-pens"]["y"] - 0.6 <= py <= by_id["existing-pens"]["y"] + PEN_D + 0.6 else px, py]
           for px, py in _wk]
    _wkp = _Poly(_wk).buffer(0)
    _poly_p = _Poly(_poul)
    _ys0 = by_id["existing-barn"]["y"] - 8                            # the network's strip north of the existing barn
    # 8' wide, the width of the existing aisle between the cattle pens and the barn that it continues
    _link = _box(by_id["existing-barn"]["x"] + by_id["existing-barn"]["w"] - 2, _ys0, max(_xs_p), _ys0 + EX_AISLE).difference(_poly_p.buffer(0.5))
    _link = max(getattr(_link, "geoms", [_link]), key=lambda g: g.bounds[0] * -1 if False else -g.bounds[0])
    # The barn's west gable is diagonal to the walk: rather than end on it at a slant, the walk's edges run on to
    # the corners of the barn's 12'-6" centre aisle, and the aisle is concrete end to end (owner, 2026-10-19;
    # frame from the architect's sheet A2.0 Unfinished Barn: posts 46'-8" x 35'-6", 2'-2 1/4" end overhangs).
    import math as _m
    _pp = _poly_p.exterior.coords[:4]
    _ed = sorted(((_m.dist(_pp[i], _pp[(i + 1) % 4]), i) for i in range(4)))
    _cx, _cy = _poly_p.centroid.x, _poly_p.centroid.y
    _aisle_ends = []
    for _l, _i in _ed[:2]:                                       # the two short sides: the gable ends
        _a, _b = _pp[_i], _pp[(_i + 1) % 4]
        _mx, _my = (_a[0] + _b[0]) / 2, (_a[1] + _b[1]) / 2
        _nx, _ny = _cx - _mx, _cy - _my; _nl = _m.hypot(_nx, _ny); _nx, _ny = _nx / _nl * 2.19, _ny / _nl * 2.19
        _ux, _uy = (_b[0] - _a[0]) / _l, (_b[1] - _a[1]) / _l
        _aisle_ends.append([(_mx + _nx + s_ * 6.25 * _ux, _my + _ny + s_ * 6.25 * _uy) for s_ in (-1, 1)] + [(_nx / 2.19, _ny / 2.19)])
    _near = min(_aisle_ends, key=lambda q: min(c[0] for c in q[:2]))   # the gable facing the walk (west)
    # the far (south-east) end runs on 10' past the barn's end wall (owner, 2026-10-19)
    _far = [q for q in _aisle_ends if q is not _near][0]
    _far = [(x - 10 * _far[2][0], y - 10 * _far[2][1]) for x, y in _far[:2]]
    _near = _near[:2]
    _aisle = _Poly(_near + _far[::-1]).convex_hull
    _x_cut = min(c[0] for c in _near) - 14
    _link = _link.intersection(_box(-1e4, -1e4, _x_cut, 1e4))
    _taper = _Poly([(_x_cut, _ys0), (_x_cut, _ys0 + EX_AISLE)] + sorted(_near, key=lambda c: c[1], reverse=True)).convex_hull
    _wkp = _union([_wkp, _link, _taper, _aisle]).buffer(0.01).buffer(-0.01)
    _wk = [[round(x, 1), round(y, 1)] for x, y in _wkp.exterior.coords][:-1]
    print("walk carried to the poultry barn:", round(_link.bounds[2] - _link.bounds[0]), "ft")
    by_id["walk"].update(outline=_wk, x=min(q[0] for q in _wk), y=min(q[1] for q in _wk), w=max(q[0] for q in _wk) - min(q[0] for q in _wk), h=max(q[1] for q in _wk) - min(q[1] for q in _wk))
    # walkways phased (architect, 2026-10-14): the cut is the arena's east edge carried across the walk. East of it
    # (the Red House, the parking, the existing barn and pens, and the poultry barn) is Level 1; west of it (along the
    # arena to the new barns, and the spur between the cattle barns) comes with the Level 2 barns.
    _xcut = by_id["arena"]["x"] + by_id["arena"]["w"]
    _wk1 = _wkp.difference(_box(-1e4, -1e4, _xcut, 1e4)); _wk2 = _wkp.intersection(_box(-1e4, -1e4, _xcut, 1e4))
    # the walk through the small animal barns' dogtrot keeps to the dogtrot (12' now): it stops at the wings
    _sab = _union([_box(e["x"], e["y"], e["x"] + e["w"], e["y"] + e["h"]) for e in E if e["id"] in ("small-a", "small-a2", "small-b")])
    _wk2 = _wk2.difference(_sab)
    _ring = lambda g_: [[round(x, 1), round(y, 1)] for x, y in max(getattr(g_, "geoms", [g_]), key=lambda h: h.area).exterior.coords][:-1]
    _bb = lambda q: dict(x=min(v[0] for v in q), y=min(v[1] for v in q), w=max(v[0] for v in q) - min(v[0] for v in q), h=max(v[1] for v in q) - min(v[1] for v in q))
    _o1, _o2 = _ring(_wk1), _ring(_wk2)
    by_id["walk"].update(outline=_o1, **_bb(_o1))
    E.append(E.pop(E.index(by_id["walk"])))                     # drawn after the (open-sided) poultry barn, so its aisle shows
    _b2 = _bb(_o2)
    add("walk-2", "", _b2["x"], _b2["y"], _b2["w"], _b2["h"], "circulation", 2, kind="walk", note="", outline=_o2, context=True)
    by_id["walk-2"] = E[-1]
    print("walks by Level: 1 =", round(_wk1.area), "sf, 2 =", round(_wk2.area), "sf | cut at x", _xcut)
    # the south sidewalk (owner, 2026-10-20), 5' wide, Level 1: flush with the parking loop's outer pavement edge, from
    # the walk network's stub by the dumpster, down the one-way drive's east edge past the Red House's front porch, and
    # round the corner along the heads of the stall row in front of the horticulture area to the row's west end. It is
    # the band 5' outside the pavement along that run; the horticulture area and the residence butt up to it.
    _pave = _Poly(by_id["parking"]["outline"]).buffer(0)
    _run = [q for q in by_id["parking"]["outline"]]
    _k0 = min(range(len(_run)), key=lambda k: (_run[k][0] - 170.0) ** 2 + (_run[k][1] - 344.3) ** 2)     # the east leg's foot by the stub
    _k1 = min(range(len(_run)), key=lambda k: (_run[k][0] - _xy(_u0, STALL_D)[0]) ** 2 + (_run[k][1] - _xy(_u0, STALL_D)[1]) ** 2)  # stall row's west head corner
    # and on round the loop's turn at the row's west end (owner, 2026-10-20): back along the pavement edge past the
    # row's end and round the curve to where it straightens onto the entry drive
    # (it stops at the residence: carried on west from the row's end along the heads' line to the residence, below)
    _path = [tuple(_run[k % len(_run)]) for k in range(_k1, _k0 + 1)] if _k1 <= _k0 else [tuple(q) for q in _run[_k1:] + _run[:_k0 + 1]]
    _band = _pave.buffer(5, join_style=2, mitre_limit=3).difference(_pave)
    _sw = _band.intersection(_LS(_path).buffer(5.5, cap_style=2, join_style=2))
    _sw = max(getattr(_sw, "geoms", [_sw]), key=lambda g: g.area)
    if "_WEST_END" in dir():                                          # from the row's end on to the residence
        _bw_ = complex(*_run[_k1])
        _uw = ((_WEST_END - _bw_) * _Uf.conjugate()).real              # negative: west of the row's end
        if _uw < -0.1:
            _ext = _Poly([_r1(_bw_), _r1(_bw_ + _Uf * _uw), _r1(_bw_ + _Uf * _uw + _Nf * 5), _r1(_bw_ + _Nf * 5)])
            _sw = _union([_sw, _ext.buffer(0.05)]).buffer(-0.05)
            _sw = max(getattr(_sw, "geoms", [_sw]), key=lambda g: g.area)
    _wk1u = _union([_Poly(by_id["walk"]["outline"]).buffer(0), _sw.buffer(0.05)]).buffer(-0.05)
    # clean corner at the dumpster apron (owner, 2026-10-20): the network's stub there poked past the sidewalk's outer
    # edge; everything south of the apron's south edge and beyond the sidewalk's outer line is trimmed off, so the
    # outline runs straight from the apron's south edge down the sidewalk
    _pa, _pb = complex(*_path[-1]), complex(*_path[-2])                  # the pavement edge's first leg from the stub
    _d = (_pb - _pa) / abs(_pb - _pa); _out = _d * -1j if ((complex(*_xy(_ue + 10, -60)) - _pa) * (_d * -1j).conjugate()).real > 0 else _d * 1j
    _o0 = _pa + _out * 5                                                   # the sidewalk's outer line
    _yap = max(q[1] for q in by_id["walk"]["outline"] if q[0] > _pa.real + 3 and q[1] < _pa.imag + 6)   # apron's south edge
    _tq = (_yap - _o0.imag) / _d.imag
    _oq = _o0 + _d * _tq                                                   # outer line meets the apron's south edge
    _cut = _Poly([(_oq.real, _yap), (_oq.real + 400, _yap), (_oq.real + 400, _yap + 400),
                  ((_oq + _d * 400 / abs(_d.imag)).real, (_oq + _d * 400 / abs(_d.imag)).imag)])
    _cut = _cut.intersection(_box(_oq.real - 30, _yap, _oq.real + 60, _yap + 30))   # only at the apron corner
    _wk1u = _wk1u.difference(_cut).buffer(0)
    _o1 = _ring(_wk1u)
    by_id["walk"].update(outline=_o1, **_bb(_o1))
    print("south sidewalk ft:", round(_LS(_path).length), "| along the pavement edge from", _path[0], "to", _path[-1])
    # circulation as drawn: the loop is two-way, so its runs carry arrowheads at both ends
    _circ = []
    for m in _re.finditer(r'<(polyline|line) id="([^"]+)"(?: data-name="([^"]+)")? class="(st\d+)" (?:points="([^"]+)"|x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)")', _sv):
        tag, id_, name, cls, pts_, x1, y1, x2, y2 = m.groups()
        pts = _svg_pts(pts_) if pts_ else _svg_pts(f"{x1} {y1} {x2} {y2}")
        base = name or id_
        kind = "animal" if base.startswith("an-") else "service"
        label = {"loop-parking": "Two-way loop", "aisle-cattle": "Tractor aisle"}.get(id_, "")
        _circ.append(dict(id=id_, kind=kind, label=label, pts=pts))
    C[:] = _circ
    by_id = {e["id"]: e for e in E}
    for c in C:      # the tractor aisle runs down the middle of the cattle barns' 16' aisle
        if c["id"] == "aisle-cattle":
            c["pts"] = [[q[0], by_id["cattle-a"]["y"] + PEN_D + CATTLE_AISLE / 2] for q in c["pts"]]
    E.sort(key=lambda e: 0 if e["id"].startswith("turnout") else 1)
    # ---- the architect's edits of 2026-10-20 (drawings/ag-area-diagram3.svg, an Illustrator export of this script's
    # generated diagram; its coordinates are this diagram's feet less (-118, 11)). Taken from it: the circulation arrows
    # as redrawn (the loop's north leg split off as an aisle arrow, the middle aisle arrow redrawn, an arrow on the
    # entry drive, a third animal arrow at small animal barn B's turnout, the pens' arrow centred in the alley), the
    # compost area as moved, and the walk from the Red House to the addition's entry canopy (Level 3).
    AG_EDIT3 = os.path.join(ROOT, "drawings", "ag-area-diagram3.svg")
    if os.path.exists(AG_EDIT3):
        _s3 = open(AG_EDIT3).read()
        _o3 = lambda q: [round(q[0] - 118, 2), round(q[1] + 11, 2)]
        _raw3 = lambda txt: (lambda v: [[v[i], v[i + 1]] for i in range(0, len(v), 2)])([float(x) for x in txt.replace(",", " ").split()])   # this file's own coordinates
        _cg = _s3[_s3.index('<g id="circulation"'):_s3.index("</g>", _s3.index('<g id="circulation"'))]
        _c3 = []
        for m in _re.finditer(r'<(polyline|line) id="([^"]+)"(?: data-name="([^"]+)")? class="[^"]*" (?:points="([^"]+)"|x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)")', _cg):
            tag, id_, name, pts_, x1, y1, x2, y2 = m.groups()
            pts = [_o3(q) for q in _raw3(pts_ if pts_ else f"{x1} {y1} {x2} {y2}")]
            base = name or id_
            _c3.append(dict(id=id_, kind="animal" if base.startswith("an-") else "service",
                            label={"loop-parking": "Two-way loop", "aisle-cattle": "Tractor aisle"}.get(id_, ""), pts=pts))
        if _c3:
            C[:] = _c3
        _cm3 = _re.search(r'<g id="compost">\s*<rect class="[^"]*" x="([-\d.]+)" y="([-\d.]+)" width="([-\d.]+)" height="([-\d.]+)"', _s3)
        if _cm3:
            _x3, _y3, _w3, _h3 = map(float, _cm3.groups())
            next(e for e in E if e["id"] == "compost").update(x=round(_x3 - 118, 1), y=round(_y3 + 11, 1), w=_w3, h=_h3)
        # the walk to the addition was drawn in the names layer, in the walk's style (class of the walk polygon)
        _wcls = _re.search(r'<g id="walk">\s*<polygon class="([^"]+)"', _s3)
        _nm = _s3[_s3.index('<g id="names"'):]
        _w3 = [_raw3(m.group(1)) for m in _re.finditer(r'<polygon class="%s" points="([^"]+)"' % (_wcls.group(1) if _wcls else "st10"), _nm)]
        if _w3:
            _o = [_o3(q) for q in max(_w3, key=lambda q: len(q))]
            _xs3, _ys3 = [q[0] for q in _o], [q[1] for q in _o]
            add("walk-3", "", min(_xs3), min(_ys3), max(_xs3) - min(_xs3), max(_ys3) - min(_ys3), "circulation", 3, kind="walk", note="",
                outline=_o, context=True)
            by_id["walk-3"] = E[-1]
        print("architect's edits of 2026-10-20 imported:", os.path.basename(AG_EDIT3), "| circulation runs", len(C), "| walk to the addition", bool(_w3))
    print("architect's edits imported:", os.path.basename(AG_EDIT), "| stalls", n_stalls, "| dogtrot ft", _dog, "| circulation runs", len(C))
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
_core = [e for e in E if not e.get("context")]
xs = [v for e in _core for v in (e["x"], e["x"] + e["w"])] + [q[0] for c in C for q in c["pts"]]
ys = [v for e in _core for v in (e["y"], e["y"] + e["h"])] + [q[1] for c in C for q in c["pts"]]
view = None   # set once the dimension strings exist (below)

# dimension strings. North string: across the top of the new work. Small barn: at the extension's north end.
# East string: complete, from the north end of cattle barn B down to the south end of the existing barn.
def dim(label, x1, y1, x2, y2):
    return {"label": label, "x1": x1, "y1": y1, "x2": x2, "y2": y2}
yt = Y_ROW1 - TURN_D - 14
_he = HOLD_E if "HOLD_E" in dir() else _ex                     # the holding block's east edge (the dog-ear line, Option B)
xe = _he + 12
dims = [dim(f"{MOD}'", XB, yt, XB + MOD, yt), dim(f"{GAP}'", XB + MOD, yt, XA, yt), dim(f"{MOD}'", XA, yt, X_HOLD, yt),
        *([dim(f"{_front - X_HOLD:g}'", X_HOLD, yt, _front, yt), dim(f"{_he - _front:g}'", _front, yt, _he, yt)]
          if "HOLD_E" in dir() and _front - X_HOLD > 0.5 else [dim(f"{_he - X_HOLD:g}'", X_HOLD, yt, _he, yt)]),   # lane, then the holding block
        dim(f"{TURN_D}'", x_sa_b - TURN_D, y_sa - 10, x_sa_b, y_sa - 10), dim(f"{SMALL_W}'", x_sa_b, y_sa - 10, x_sa_b + SMALL_W, y_sa - 10),
        dim(f"{GAP}'", x_sa_b + SMALL_W, y_sa - 10, x_sa_a, y_sa - 10)]
by_id = {e["id"]: e for e in E}
string = [by_id["turnout-cattle-a"]["y"], by_id["holding-3"]["y"], by_id["holding-2"]["y"], by_id["holding-1"]["y"], _ep["y"], _ep["y"] + PEN_D, y_barn, SOUTH]
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
    "counts": {"cattle_pens": {"1": 7, "2": 21, "3": 35}, "small_animal_pens_per_barn": (SA_PENS["2"] if "SA_PENS" in dir() else 2 * (SA_L // SA_PEN_W)), "small_animal_pens": SA_PENS if "SA_PENS" in dir() else {"2": 2 * (SA_L // SA_PEN_W), "3": 4 * (SA_L // SA_PEN_W)}, "option": OPTION, "parking": n_stalls},
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
    if e.get("grass"):
        out.append('<polygon points="' + " ".join(f"{px},{py}" for px, py in e["grass"]) + f'" fill="{P["pasture"]["tint"]}" fill-opacity=".6" stroke="{P["pasture"]["base"]}" stroke-dasharray="3 2"/>')
    for z in e.get("zones", []):
        if "poly" in z:
            out.append('<polygon points="' + " ".join(f'{e["x"] + px},{e["y"] + py}' for px, py in z["poly"]) + '"/>')
        else:
            out.append(f'<rect x="{e["x"] + z["x"]}" y="{e["y"] + z["y"]}" width="{z["w"]}" height="{z["h"]}"/>')
    return f'<g fill="none" stroke="{N["ink"]}" stroke-width=".35" opacity=".45">{"".join(out)}</g>' if out else ""


svg = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
       f'viewBox="{view[0]} {view[1]} {view[2]} {view[3]}" font-family="Avenir Next,Helvetica,Arial,sans-serif">'
       f'<title>Primary ag area, Level 3 (feet)</title><rect x="{view[0]}" y="{view[1]}" width="{view[2]}" height="{view[3]}" fill="{N["paper"]}"/>']
_names = []          # element names go on their own layer above the shapes, so a later shape (the walk) never hides one
for lv in (1, 2, 3):
    svg.append(f'<g id="level-{lv}" inkscape:groupmode="layer" inkscape:label="Level {lv}">')
    for e in [e for e in E if e["level"] == lv]:
        use = e.get("becomes", {}).get("2", {}).get("use", e["use"])
        c = P[use]
        dash = ' stroke-dasharray="3 2"' if e["kind"] == "yard" else ""
        fill = "#fff" if e["kind"] == "walk" else c["tint"] if e["kind"] != "yard" else "none"     # the walk: plain concrete
        if e.get("holes"):
            shape = '<path fill-rule="evenodd" d="' + " ".join("M" + " L".join(f"{px},{py}" for px, py in ring) + "Z" for ring in [e["outline"]] + e["holes"]) + f'" fill="{fill}" stroke="{c["base"]}" stroke-width="1"{dash}/>'
        elif e.get("outline"):
            shape = '<polygon points="' + " ".join(f"{px},{py}" for px, py in e["outline"]) + f'" fill="{fill}" stroke="{c["base"]}" stroke-width="1"{dash}/>'
        else:
            shape = f'<rect x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}" fill="{fill}" stroke="{c["base"]}" stroke-width="1"{dash}/>'
        svg.append(f'<g id="{e["id"]}">{shape}{pens_svg(e)}</g>')
        if e["label"]:
            _names.append(f'<text data-id="{e["id"]}" x="{e["x"] + e["w"] / 2}" y="{e["y"] + e["h"] / 2}" text-anchor="middle" font-size="5" font-weight="700" fill="{N["ink"]}">{e["label"].replace("&", "&amp;")}</text>')
    svg.append("</g>")
svg.append('<g id="drives" inkscape:groupmode="layer" inkscape:label="Driveways">' + "".join(
    f'<rect id="{d["id"]}" x="{d["x"]}" y="{d["y"]}" width="{d["w"]}" height="{d["h"]}" fill="{P["circulation"]["tint"]}" opacity=".6"/>' for d in DRIVES) + "</g>")
svg.append('<g id="circulation" inkscape:groupmode="layer" inkscape:label="Circulation">')
for c in C:
    col = P["cattle"]["base"] if c["kind"] == "animal" else N["ink"]
    pts = " ".join(f"{x},{y}" for x, y in c["pts"])
    svg.append(f'<polyline id="{c["id"]}" points="{pts}" fill="none" stroke="{col}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>')
svg.append("</g>")
svg.append('<g id="names" inkscape:groupmode="layer" inkscape:label="Names">' + "".join(_names) + "</g></svg>")
open(os.path.join(ROOT, "drawings", "ag-area-diagram.svg"), "w").write("".join(svg))
print("extent (ft):", round(view[2]), "x", round(view[3]), "| elements:", len(E), "| circulation runs:", len(C), "| parking:", n_stalls)
