"""Stormwater concept: every design decision, in one short file.

Change a value here, then run tools/build_stormwater_concept.py and tools/export_sheets.py. See
docs/reference/stormwater-design-basis.md for where each value came from and which ones civil still has to confirm.

Coordinates are the site map's presentation frame (map units; 1 unit = 2.59 ft; north is to the left, so east is up and
south is to the right on the sheets). Distances are feet unless noted.
"""
import re

# ---- elevations (ft, survey datum)
BFE = 21.70                   # modelled 100-year elevation
PAD_EL = BFE + 1.0            # direction item 1
HIGH_EL = 22.00               # "just above the BFE": pasture benches and paths
NWL = 18.00                   # normal water level of the pond and the swale's wet shelf (assumed)
SHELF_EL = 17.50              # littoral shelf, 6" under the normal water level (assumed)
POND_BOTTOM = 12.00           # retention pond deep pool (assumed)
TRI_NWL = 18.40               # the north triangle's pond holds its water here before it discharges (assumed)
TRI_BOTTOM = 14.00            # that pond's deep pool (assumed)
SWALE_SIDE, POND_SIDE = 7, 4  # bank slopes, horizontal to 1 vertical (assumed)
TARGET_SWALE = 0.70           # direction item 3

# ---- plan dimensions (ft)
PATH_W, HUB_R = 40, 60        # path: 16' crest plus 4:1 side slopes; high ground around each feed + water hub
ROAD_STRIP = 15               # high ground kept along the road
PATH_FILLET = 45              # radius where a swale's top of bank turns to run along a path
WOODS_EDGE, PAD_EDGE = 10, 15 # swale held back from the woods, and from the pad's toe of slope
PAD_TOE = 10                  # pad side slope, about 4:1
RADIUS, ARM = 50, 40          # radius of the swale's inside bends; radius of its outside corners
WOODS_SPUR, WOODS_NOTCH = 25, 30   # the woods' edge for grading: spurs under 50' wide trimmed, notches under 60' filled

# ---- centerlines (presentation frame), following the historical bed where there is one
MAIN = [(712, 345), (716, 395), (745, 418), (775, 416.5), (800, 418.5), (830, 422), (900, 424), (960, 412), (1000, 392), (1022, 400), (1030, 440),
        (1060, 475), (1110, 500), (1145, 506), (1175, 520), (1230, 538), (1270, 531)]
BRANCHES = {
    "north":      [(1000, 392), (1018, 350), (1030, 315), (1022, 285)],
    "west strip": [(672, 318), (625, 303), (578, 300)],
    "east strip": [(726, 316), (800, 300), (885, 298)],
    "pond":       [(1175, 520), (1200, 500)],
    "triangle":   [(650, 412), (590, 397), (520, 388), (455, 399), (400, 418), (345, 425)],
    "triangle e": [(674, 414), (697, 424)],
    "triangle n": [(520, 388), (482, 335), (440, 302), (398, 286)],
    "triangle w": [(345, 425), (300, 428), (262, 418), (215, 398), (165, 365), (140, 320)],
}
ROAD_CULVERT = [(672, 415), (716, 395)]              # the triangle pond's outlet, under the road to the bend in the main swale
ENTRY_CULVERT = [(1146.7, 503.2), (1156.1, 507.6)]   # the surveyed crossing under the entry drive, to be replaced
OUTFALL_LINK = [(1270, 531), (1293, 528)]            # through the 10' strip to the existing bed and outfall
SOUTH_FENCE = [(1288.0, 595.5), (1286.8, 444.3)]     # the fence on the pond's south side
SOUTH_HOLD = 10                                      # top of bank held this far off that fence
HUBS = [(927.4, 312.9), (322.6, 329.3)]
# the working barnyard goes on the pad; parking, the garden, the Red House, and the walks stay at grade
PAD_SKIP = re.compile(r"parking|garden|horticulture|red-house|classroom|walk|sidewalk|rv|residence|existing", re.I)

# ---- swale bottom: swings wide of cattle barn B (architect's markup)
BARN_B_BEND = [(1000, 392), (1008, 404), (1012.6, 418), (1013.5, 432), (1028.7, 449), (1049, 464.2), (1075, 484), (1110, 500)]
# floor elevation against distance along the flow to each pond: (feet of flow, elevation)
MAIN_FLOOR = ([0, 120, 300, 3500], [SHELF_EL, SHELF_EL, NWL, NWL + 0.1])
TRI_FLOOR = ([0, 100, 300, 2600], [TRI_NWL - 0.5, TRI_NWL - 0.5, TRI_NWL + 0.12, TRI_NWL + 0.35])   # the pasture floor stays above the pond's water
# banks eased from top of bank to swale bottom: around the pad corner at cattle barn B, and north of Pen 5 (center, radius ft)
SOFT_CIRCLES = [((1035, 428), 200), ((1062, 298), 150)]

# ---- raised pad: one clean L in the barnyard's own grid (feet), straight north and west edges, 8' clear of the outermost yards
PAD_OUTLINE = [(-92, 34), (301, 34), (301, 224), (-4, 224), (-4, 332), (-92, 332)]

# ---- paths
BARN_AXIS = (62 + 86) / 2                                          # Path A: centerline between the two cattle barns (barnyard grid x)
RAMP_LEN, RAMP_HW = 70, 18                                         # Path A ramp off the pad; shown by the 22' contour alone
PATH_B_POINTS = [(796.6, 355), (788, 376.5), (779, 391), (761, 412), (752.4, 422.1)]     # high ground in the 4.8 ac paddock to its corner gate
PATH_C_POINTS = [(721.6, 440.3), (690, 440.4), (600, 436.6), (530, 433.7), (505, 430), (470, 416.6), (430, 392), (332.6, 328.7)]   # south tip gate, along the fence, to the triangle hub
PATH_B_ARM_LINE, PATH_B_ARM_HALF = [(773, 416.5), (800, 418.5), (830, 422)], 16          # the swale arm carried north to Path B

# ---- north triangle retention pond, from the architect's sketch
TRI_POND_POINTS = [(634.8, 414.5), (638.2, 405.3), (650.7, 403.2), (667.3, 406.2), (676.5, 413.2), (674.8, 422.8), (659, 425), (640.3, 420.8)]
