# Barnyard, barns, pens, parking, and Option B

Moved verbatim from the original NOTES.md. `<!-- from line n -->` marks where each entry stood.

<!-- from line 81 -->
## Barnyard diagram
- `tools/build_ag_area.py` → `slides/data/ag-area.js`, `drawings/ag-area-diagram.svg`; slide `slides/ag-area.html`. Units are feet, drawn square to the existing barn (17° off true north, measured on the study plan), existing barn at the bottom, north roughly up (confirmed orientation for this diagram). Existing barn 80.4' wide; its 7 pens measure 12' × 24' on the survey.
- Layout per the architect's Illustrator markup of 2026-10-12, snapped to a 12' module with 24' lanes and gaps everywhere: east column = existing barn (bottom-right), existing pens, cattle turnouts A and B (84' wide; A runs down to the pens); cattle run west of the turnouts; centre strip = arena (50' × 84') and feed storage; small animal run; small animal turnouts on the west; new corral/chute/scale bottom-left; parking bottom centre.
- Feed storage is shipping containers: 2 × (8' × 40'), one at Level 2 and one at Level 3 (4 × 8' × 20' is the alternative).
- Small animal barn: 6' × 10' pens both sides of a 16' aisle, 28 per barn (confirmed). First barn of each run at Level 2, second barns and arena at Level 3 (confirmed).
- Parking drawn to scale: 9' × 18' stalls on a 24' aisle, 10 per side = 20 spaces in the block as placed (study plan A0.2 showed 51 + 9).
- Circulation step: straight runs only. Service: west lane (full length, down past the parking), east lane, cross drive, mid cross lane, tractor aisles through both barns of each run. Animals: each barn to its turnout, existing pens to turnout A.
- The master SVG can be edited in Illustrator (element ids survive); moved rectangles are read back into the script's numbers.
- Existing pens sit across an 8' aisle from the existing barn (exists on site; not on the survey). Parking stalls are 10' × 20' (trucks and SUVs), one bay of the main lot shown between two 24' driveways; the east driveway lines up with the cattle tractor aisle. No separate visitor arrows.
- Bud Box slide `slides/bud-box.html`: geometry from the handling layout on study plan A0.2 (12' lead-up alley, 12' × 20' box, single-file alley beside the gate, chute on the scale). Five animated steps. Handler positions and group size are schematic; check against a reference before presenting to IFAS.
- Entry and parking (architect's CAD screenshot, 2026-10-12): the existing asphalt drive comes in from the south-west under the tree row and feeds the west end of the main lot; the lot runs along the south edge of the barnyard from the handling yard to the existing barn, as stall rows around a centre island (one-way loop); the drive leaves the south-east end toward the Red House and returns around the bioswale. In the diagram the north stall row has two 24' breaks (west lane, cattle tractor aisle) for hand-off to the tractor lanes, which leaves 46 stalls drawn against 51 on the CAD.
- Parking and handling per the architect's simplified plan (2026-10-12, supersedes my earlier variants):
  - One-way loop, counter-clockwise: the entry drive leads past the Red House side first; traffic comes up into the lot at the south-east, runs north up the east return, west along the north aisle, south down the west lane, and leaves toward the entry drive.
  - The loop's two north-south legs line up with the tractor aisles of the barn runs: west leg on the small animal barns' aisle, east leg on the cattle barns' aisle, so a tractor runs straight from the lot through both barns.
  - Lot: north row (12), centre island (12 + 12) and south row (12, backing onto the bioswale island) between the two legs, = 48 drawn; 10' × 20' stalls, 24' aisles. No stalls in front of the existing barn: that apron stays open for access to its four overhead doors.
  - Trailer stop is its own lane (24' × 60', gate at each end), west of the loop's west leg and just south of the north aisle; its north end lines up with the north end of the lead-up alley. Overlapping it with the drive aisle was rejected (fence and gate management).
  - Handling yard (72' × 84', west of the trailer lane) keeps the study-plan arrangement: lead-up alley and Bud Box (12' × 20', dead end west) along the north side; 16' single-file alley dropping south beside the box gate to the chute on the scale (four cattle at most); holding pen with chamfered corners wrapping around the chute. Bud Box slide shows the cattle in the lead-up alley before the box (seven steps). Same geometry on `slides/ag-area.html` and `slides/bud-box.html` (keep in sync).
  - Lesson: follow the architect's layout; do not rearrange it.
  - Architect's Illustrator edits of 2026-10-12 (evening), folded into the script: the four turnouts each extend 12' so the pairs meet halfway across the gap between the barn rows (small animal and cattle B 96' deep; cattle A 120', down to the existing pens); the lot outline is a plain rectangle, 177' × 164', from the loop's west edge to its east leg; the two lanes between the runs stop just inside the cross drive; the mid cross lane runs between the barn runs only; label reads "Small animal barn A".
  - Naming: both are "small animal barns". Barn A is drawn in the hog color to show the hogs move there at Level 2; barn B stays in the small animal color.
  - Round trip: the architect edits `drawings/ag-area-diagram.svg` in Illustrator; I diff it against the generated master by element id, fold the changes into `tools/build_ag_area.py`, and regenerate. Illustrator styling is not kept, geometry is.
- Bud Box basis: Priefert Bud Box (https://www.youtube.com/watch?v=7Xs6HmrRTUs) plus extension guidance: K-State MF3349, Missouri Extension G2003, Gill & Machen. Box 12' wide for handlers on foot, 20–30' deep; straight single-file alley at least 24'; cattle flow through the box, never held; handler starts opposite the alley, then walks the alley-side fence toward the closed end.

<!-- from line 104 -->
## Barnyard on the site
- The barnyard diagram is placed to scale on the survey/aerial by `tools/build_site_map.py` (layer `barnyard` in `drawings/site-layers.svg`): the middle of the diagram's existing-pens north edge is pinned to the middle of the surveyed pen fence line on study plan A0.2 (P-RAILING, 80.9' long; the diagram's row is 84'), turned to that line's bearing (17.3°). Slide: `slides/site-plan.html` (Levels 1–3 at barnyard scale, then the full site). Run `build_ag_area.py` before `build_site_map.py`.
- Fit checks computed in the build (`SITE_MAP.barnyard.checks`), 2026-10-12:
  - Barn runs, arena, feed storage and turnouts: no surveyed trees inside.
  - Parking footprint: 22 surveyed trees inside, including the row along the existing drive.
  - Two existing surveyed structures (61' × 25' and 35' × 29') sit in the cross drive, at the south end of cattle barn A.
  - Very poorly drained soil (Delray), before the 2026-10-13 change: small animal barn B 62% of its footprint, arena 18%, cattle barn B 9%. After it: extension 0%, arena 18%, cattle barn B 9%.
  - South stall row is about 27' from the nearest Red House wall line; the loop's east leg cannot run straight south and has to bend around the house (as on the CAD plan). The diagram's bioswale-island stub south of the stalls is schematic.
  - The fencing plan's paddock lines around the campus follow the earlier U-shaped layout and need redrawing for this one.

<!-- from line 114 -->
## Layout study: small animal barn B and the wet soil (2026-10-12, awaiting the architect's choice)
- `tools/study_wet_soil.py` → `drawings/studies/wet-soil-options.svg/.png/.json`. In the barnyard frame the very poorly drained soil is a wedge coming in from the north-west corner (down to about y = 80' at x = -40') plus a band across the whole north edge (y < 0 to 12'). The south barn row is entirely clear.
- Share of footprint on that soil (small barn B / arena / cattle barn B): as drawn 62 / 18 / 9; A slide north row 12' south 48 / 5 / 0; B swap barn B and arena 18 / 62 / 9; C barn B beside barn A (south row) 0 / 18 / 9; D barn B in the middle strip south of the arena 0 / 18 / 9; E = C plus arena and cattle barn B 12' south 0 / 5 / 0. No option puts surveyed trees inside a building.
- Also tested: shifting everything new 48' south and 12' west (barn B 18%, arena 0%, cattle barn B 0%, but cattle turnout A lands on the existing pens and barn, the cross drive dead-ends at the existing barn, and the parking touches the Red House); and a half-length barn B (26% in place, 8% slid 12' south, 0% attached to barn A).
- **Decision 2026-10-13:** no second small animal barn. Level 3 adds a 42' extension to barn A instead (14 more pens, 42 in all; extended barn 126' × 36' = 4,536 sf, smaller than one cattle barn at 5,208 sf). It shares barn A's turnout. The wet north-west corner stays pasture. The extension keeps the element id `small-b`. Arena (18%) and cattle barn B (9%) are unchanged. `tools/study_wet_soil.py` describes the superseded two-barn layout and no longer runs; its outputs remain in `drawings/studies/`.

<!-- from line 292 -->
### Campus fence redrawn to the turnout yards (2026-10-13)
- The fencing plan's run round the north and west of the campus (`fence-07`, drawn for an earlier layout, cutting
  through cattle barn B and the arena) is replaced on the map by a line on the outer edges of the barnyard: east
  edge of the cattle turnouts, north face of cattle barn B and the arena, round the small animal turnouts, down the
  west side of the handling yard, then back onto the plan's last leg to its gate at the lane. Built in
  `build_site_map.py` from the barnyard diagram's own elements, so it follows the diagram if that moves. The plan's
  first two and last vertices are kept. `fences.json` (the plan as drawn) is unchanged; the redrawn run is written
  to `drawings/data/campus-fence.json`. 1,089 ft → 1,101 ft.
- **Paddock areas:** the 3.4 ac paddock west of the campus now measures 3.8 ac, because the fence moved in to the
  turnouts. Its label and the capacity worksheet still say 3.4. All other paddocks stay within 0.3 ac of their labels.
- The "fence lines need redrawing" finding is removed from the barnyard-on-site slide.
- **Poultry label:** the unfinished barn is labelled "Poultry (Level 1)" on the barnyard-on-site slide, per the
  Levels matrix (poultry moves to small animal barn A at Level 2).

<!-- from line 323 -->
### Holding pens and handling yard corner (2026-10-13)
- **Holding pens (Level 1), from the architect's sketch.** Four yard elements in `build_ag_area.py` (`holding-1..4`),
  so they appear wherever the barnyard is drawn (barnyard slide, barnyard-on-site slide). Pens 1 to 3 run down the
  west side on the line of the handling yard's west fence: pen 1 beside the handling yard (9,170 sf), pen 2 north
  to the middle of small animal barn A (8,730 sf), pen 3 on to the north end of the small animal turnouts
  (5,950 sf). Pen 4 fills the gap between the small animal turnout and the Bud Box (2,640 sf). Sizes are read from
  the sketch, not dimensioned. The west fence was first set at 68'/126' deep from the sketch, which clipped the
  historical slough bed by about 950 sf; it is set at 62'/118' (`PEN_DEPTH_N/S`), which clears it.
- **Handling yard corner.** Its south-east corner is now square, as on the Bud Box slide (the diagonal there is the
  receiving gate, not a fence). Only the south-west corner is chamfered.
- **Campus fence** now runs round the outside of the pens (pen 3's north side, the pens' west fence, then the
  plan's last leg to its gate at the lane): 1,054 ft.
- **Capacity again.** The pens come out of the paddock west of the campus: 3.4 ac on the plan → 3.2 ac (it had
  been 3.7 before the pens). Site pasture 44.7 ac, 99.2 ac with bonus. 6.9 / 14.3 / 27.3 CE, so the planning
  figures are back to **7 / 14 / 27**. Hard-coded mentions reset to match.
- **Handling yard corners, corrected (architect's markup).** I had misread the earlier note and squared the yard's south-east corner; it is chamfered again, with nothing drawn outside the chamfer. At the south-west corner, pen 1's south fence now runs straight on to the end of the chamfer, so there is no fence across the small triangle there (pen 1 is 9,330 sf). Capacity unchanged: 7 / 14 / 27 CE.

<!-- from line 359 -->
### Red House, horticulture area and a tighter parking lot (2026-10-13)
- **Red House and horticulture in the barnyard diagram** (`build_ag_area.py`, as context elements): the Red House is
  the architect's outline from the site edits; the horticulture area is the "HORTICULTURE AREA" rectangle on study
  plan A0.2 (layer A-WALL-OTLN), 100' x 30', beside the drive south-west of the Red House (the 20' x 30'
  "RESIDENCE" at its end on that plan is left out). Both are converted to diagram feet with the inverse of the
  diagram-to-map transform, now shared as `siteframe.diagram_transform()`. The barnyard slide's opening view still
  frames the barnyard only; the two appear when the viewer pans down. The horticulture area also shows on the
  barnyard-on-site and water site plans (Level 1, notes by Level: raised beds and pots / beds with irrigation /
  shade area, planting tables). One surveyed tree falls inside it. The Red House is not redrawn on the site map,
  where it is already a structure.
- **Parking lot:** briefly cut to a 12' island and reverted. "Tighten up" meant representing the design intent more
  closely, not shrinking it; to be worked on with the architect later. Lot back to 164' deep, 36' island.
- **Residence (architect):** the 20' x 30' "RESIDENCE" at the end of the horticulture strip on study plan A0.2 is a
  Level 3 element; at Levels 1 and 2 the spot has hookups for a camper or RV. Added as a context element
  (`residence`, notes by Level) and as a Levels matrix row. Map label "RV / residence".

<!-- from line 384 -->
### Parking lot south loop, from the architect's CAD sketch (2026-10-13)
- The architect's earlier CAD sketch of the lot (screenshot, 2026-10-12; not saved to the repo, coordinates read
  off it into `build_ag_area.py`) is placed on the diagram by the Red House carport drawn on it: its four corners
  are matched to the survey's carport (BUILDING OH, 29' x 38'). Fit within 0.4 ft, 4.36 px/ft, turned 0.6 degrees;
  the sketch's Red House steps land on the Red House. So the south loop is positioned off the Red House, and it
  lines up with the horticulture strip (from the study plan) without adjustment.
- Taken from the sketch: the west leg carries on south and turns south-east along a row of nine angled stalls
  backing onto the horticulture strip, ending at the carport; the drive on the east side runs down toward the Red
  House; the bioswale island gets the sketch's rounded south end. Kept from the current layout: the north part of
  the lot (rows, legs, 36 stalls). The island is cut to the space between the two legs, south of the south row.
  Lot now 45 stalls. Drawn on the barnyard slide, the static diagram SVG and the site plans
  (`stalls_extra`, `island_poly`). First pass, for the architect's markup.
- **Entry drive** (next step from the same sketch): about 12.6' between edges, meeting the lot's west leg with 10' curb returns, drawn as part of the lot's pavement. It lies on the existing surveyed entry drive (the survey's edges cross the diagram at y = 391 and 402) and is carried west to the line of the handling yard's west side, where the drive continues toward the lane. Moved 5' east with the lot's west leg, which sits 5' east of the sketch's.
- **Loop arrows** now follow the south loop: in past the carport, north up the east side and the east leg, west
  along the north aisle, south down the west leg, then south-east along the angled stalls back toward the carport.
  The old "In, from the Red House side" / "Out, to the entry drive" notes are removed.
- **Entry drive to the lane (new Level 1 apron):** the drive now runs straight on to the lane's near edge (from the
  surveyed road edges where the existing drive meets the lane, diagram x about -288), with 10' flares each side at
  the road. On the site plans it lies over the existing tree-lined drive and its flared apron and island.
- The Python build environment in the scratchpad lost its packages overnight; rebuilt (`venv2`). The build
  reproduced the committed outputs exactly before any change.
- **Swale island (architect, 2026-10-14):** the island is cut out of the parking lot's paving (`holes` on the parking element; drawn with an even-odd path in all three renderers). The swale is drawn inside it, set back 5' from the curb (`SWALE_SETBACK`; asked for 4-6'). On the site plans the island is filled with ground colour (hiding the existing drive surveyed under it) and the two surveyed trees inside it are redrawn above the swale (`#swale-trees`).
- **South loop redrawn on the Red House's grid (architect, 2026-10-14: edges not parallel, poorly registered, too
  much paving south of the Red House).** The Red House, carport, angled stalls and horticulture strip are square to
  one another (about 34 degrees off the diagram grid), so the south loop is laid out in that frame (u along the
  stall row, n across it), with only the stall-front line taken from the sketch. The stall row now starts where the
  west leg meets the stall fronts (its west end is a stall side, square to the row); the drive from the east leg
  runs parallel to the Red House's west face, 24' wide and set back 10' from it, then along a 24' aisle (14' clear of
  the Red House's south face) straight into the carport. The paved apron south of the Red House is gone. The swale
  island follows the drive edges with 2' curbs and 4' rounded corners; it is now roughly triangular, and the two
  surveyed trees that were in it fall under paving.
- **One-way drive past the Red House (architect, 2026-10-14):** 13' wide (`DIAG_W`), 5' off the Red House (`RH_SETBACK`) to leave room for an accessible sidewalk; the only one-way stretch of the loop. The aisle stub into the carport (the T-turn south of the Red House) is removed; the stall row now ends at the one-way drive. Loop arrows: west along the north aisle, south down the west leg, south-east along the stalls, north up the one-way drive and the east leg. The island grows into the space freed; the two surveyed trees fall inside it again.
- **Swale island south corner:** the inside corner of the turn from the stall aisle up the one-way drive has a 20' radius (other corners keep 4').\n- **Parking bank (architect):** five 90-degree stalls off the east side of the east leg, between the existing barn and the Red House, centred in the gap (`BANK`). Lot total 50. The site map's parking renderer now draws stall columns (rows flagged "v") correctly.
- **Swale clear of trees (architect):** the swale is cut back from the three surveyed trees in or beside the island, by each tree's drawn canopy plus 3'; about 4,070 sf of swale remains.
- **Parking bank re-angled (architect):** the five stalls are now on the Red House grid, square to the one-way drive
  and opening off its line carried north, with a 24' aisle in front; the paving is filled back to the east leg so
  no slivers remain between the two grids. They start 12' north of the Red House's north-west corner.
- **Accessible walk, first pass (architect):** 5' wide, about 340 ft, element `walk` (Level 1, white). Route: the 5'
  strip between the Red House and the one-way drive, between the Red House's north-west corner and the bank,
  behind the bank, then square to the barnyard grid west of the existing barn and its pens, and along the north
  edge of the cross drive to the south-east corner of cattle barn A. It crosses no drive except the cross drive
  at the barn. A small surveyed outbuilding (about 10' x 9') sits just beside the walk behind the bank.

<!-- from line 475 -->
## Option A archived (2026-10-14)
The barnyard layout developed through 2026-10-14 is archived as **Option A**: git tag `option-a-2026-10-14`
(commit b866f2d, full source and tools) and a viewable copy of the deck in `archive/option-a-2026-10-14/`. The ag
expert on the design team gave substantial feedback on the barnyard; the next option (Option B) follows
`source/NEW SITE PLAN OPTION 10-14 SKETCH.jpg`. Work on Option B continues on `main`.

<!-- from line 481 -->
## Option B (2026-10-14), from `source/NEW SITE PLAN OPTION 10-14 SKETCH.jpg`
Architect's direction: carry over the parking lot (to be fitted to this scheme later); turnouts 36' off the north
side of the cattle barns and 36' west of small animal barn B; the "hog barns" are the small animal barns (either
use); 24' clear between all buildings; small animal barn A at Level 2, B at Level 3.
- Built in `build_ag_area.py` (the OPTION B block after the walk): Option A's barnyard elements and circulation are
  dropped and replaced; parking, Red House, horticulture, residence carry over. Final coordinates (diagram feet):
  cattle barns B (-22..62) and A (86..170) at y 80..142, long sides east-west, pens both sides of an east-west
  tractor aisle; turnouts y 44..80; holding pens 5 and 3 (y 80..116), 4 and 2 (116..164), 1 (164..216) in two
  columns either side of an 8' alley (x 230..238), from cattle barn A's east wall to the existing pens' east edge;
  handling (Bud Box, chute, scale) x 182..230, y 164..216 with a 14' working alley on its west side; arena 86..170,
  y 166..216; feed storage 16' x 40' (two containers); small animal barns A and B 36' x 48', bottoms in line with
  the arena; small animal barn B's turnout to its west. Service drive loop around the arena (the sketch's dotted
  line). Sizes are the deck's standards; the sketch is freehand.
- Campus fence re-routed round Option B (north of the turnouts, west of small animal barn B's turnout); fences that
  ran to the old line are carried on to the new one (fence-19, 32'). Paddocks 8.0 → 7.9 ac and 3.4 → 3.6 ac;
  capacity 7.0 / 14.5 / 27.6 CE; planning figures 7 / 14 / 28.
- The accessible walk's last leg is re-aimed at cattle barn A (north between the arena and the handling alley).
- Fit checks: the two existing surveyed structures that sat under cattle barn A now sit under the arena; cattle
  turnout B is 33% on the wettest soil; the historical slough bed touches the barnyard's north-west corner.
- Slides: barnyard and barnyard-on-site eyebrows read "Option B"; Level texts and the Levels matrix updated; the Bud
  Box slide still shows Option A's yard and says so.
- **Option B handling yard = the Bud Box slide's yard, mirrored (architect, 2026-10-14).** Same geometry as slide 12
  (72' x 84' yard; Bud Box and lead-up alley along the north; single-file alley, chute and scale; holding pen
  wrapping the chute with chamfered corners; 24' tapered pull-through trailer bay), flipped east-west so the bay is
  on the west side, in the lane east of the arena where the sketch's arrow runs north (yard x 194..266, bay
  170..194, y 132..216). The yard's holding pen is pen 1; pens 2 to 5 sit north of the yard (y 80..132) in two
  columns either side of an 8' alley. The service drive's east leg runs through the bay. The accessible walk now
  avoids the bay: west along the cross drive's north edge, north beside the arena's west side, east to cattle barn A.
- **Holding yard sized for four cattle (architect):** 36' x 42' (half the slide's yard each way), corner chamfers as
  single 12' panels (8.5' each way); Bud Box 20' x 12', 16' single-file alley and chute kept; the lead-up is the 16'
  beside the Bud Box; the bay matches the yard's 42' depth. Yard x 194..230, bay 170..194, y 174..216. With the space
  freed, the pens follow the sketch again: 5 and 3 along the top, 4 and 2 below, pen 1 east of the yard, two columns
  either side of an 8' alley in line with the yard's east side. The Bud Box slide itself still draws the 72' x 84'
  yard (its note says Option B is sized down).
- **Cache-busting:** `tools/stamp.py` adds ?v=<time> to every slide's data/design links. Browsers had been showing an old ag-area.js on the barnyard slide after a rebuild. Run it after the build tools, before committing. Run order: build_fences, build_canopy, build_south_roads, build_slough_bed, build_civil, build_ag_area, build_site_map, build_retention_markup, build_site_map, build_capacity_data, stamp.

### Option B, architect's edits imported (2026-10-14): `drawings/ag-area-diagram2.svg`
The architect edited the generated diagram in Illustrator; `build_ag_area.py` now reads that file (block "OPTION B,
architect's edits") and takes its geometry element by element (diagram feet = svg + (-118, 13), the view origin the
file was exported with). What it carries: a **two-way loop** (parking loop and the service drive round the arena
joined); **no trailer enclosure** (the ag consultant: not needed here; the Bud Box slide to follow); **bedding
storage** 24' x 12' beside cattle barn A (Level 2), **compost area** ~49' x 19' and a **12' x 24' dumpster enclosure**
south of the existing barn (taken as Level 1); a **grooming area** at the arena's west end; **one small animal barn**
(Level 2, 36' x 48') with a 15' **dogtrot** to its Level 3 **extension** south; turnouts widened (cattle turnouts
-48..194, small animal turnout the barn's full length); pens 4 and 5 narrowed to 36'; the **parking bank removed**
(45 spaces); a white **walkway network** as drawn. The regenerated `drawings/ag-area-diagram.svg` reflects all this;
`ag-area-diagram2.svg` is the architect's source and is not overwritten. Slide texts and the Levels matrix updated.
Fit checks now skip context elements (walk etc.).
- **Follow-up (architect, 2026-10-14):**
  - Loop legs past the Red House and east of the arena are a pervious drivable surface (aggregate or grass over a
    base), not pavement: left unpaved on the plans.
  - The ten stalls added to the banks sat in the file's circulation layer; the import now takes every 10' x 20'
    stall in the file: **55 spaces**.
  - Small animal turnout comes in at Level 2 beside barn A; Level 3 adds its extension beside barn B.
  - Compost and dumpsters are Level 1 but could wait if funding is tight (said on the barnyard slide).
  - The 24' gap between the cattle barns is both walkway and tractor path, likely the busiest route on the campus:
    participants take animals to the grooming area daily (said in the Flow step).
  - The walkway network is correct as drawn: ADA and vehicular circulation together.
  - **Small animal barns:** what was drawn is **barn A** (Level 2): two 36' x 48' wings either side of a 15' dogtrot
    (3,996 sf with the dogtrot taken as roofed). **Barn B** (Level 3) extends it south to the code limit for a
    Group U, Type VB building, 5,500 sf per story (IBC Table 506.2, no sprinkler or frontage increase): 36' x 41',
    12 pens, 5,472 sf in all. Small animal pens: 32 at Level 2, 44 at Level 3.
  - Labels: the handling yard has no overall label on the barnyard slide (its parts are named); the arena's name is
    centred again (it had been placed below the building because it now has a zone).
- **Grooming area at Level 2** (architect): its own element (`grooming`, 9.7' x 42' at the arena's west end), drawn
  over the arena; the arena stays Level 3 ("built out from the grooming area"). Levels matrix arena row: Level 2
  "Grooming area".
- **Poultry on the barnyard diagram:** the unfinished barn (survey BUILDING OH) as a context element
  (`existing-poultry`, Level 1, small-animal colour), east of the existing barn; outside the slide's opening frame
  (pan east). The walkway network is carried 106' east from its strip along the existing barn's north side to the
  barn's west face, 8' wide (the existing pens' aisle it continues). Not redrawn on the site map (already there as a structure).
- Dogtrot confirmed roofed (barn B 36' x 41' stands).
- **Grass parking (architect):** the north stall row and the two middle rows (lot x 36.5..170, y 240..324) are grass over a base, shown with a pale green, dashed overlay and the label "Grass parking" (`grass` on the parking element; all three renderers). 37 of the 55 stalls; the south row, the angled row and the aisles stay paved.
- Central double row carried one stall further east on each side to match the north row (added in code, skipped if the architect's file gains them): **57 spaces**, 39 on grass.
- Campus fence now runs on the small animal turnout's north and west edges (no 12' jog). The 3.4 ac paddock measures 3.7 ac; Level 2 capacity 14.5 CE now rounds to 15: planning figures **7 / 15 / 28** (water quality slide and outline updated).
- **Bud Box slide, no trailer enclosure (architect):** bay fences, gates and fill removed; the two-way loop lane (24') runs right along the yard's east fence. The receiving gate moves from the south-east chamfer (now solid fence) to the top corner of the holding pen: a 12' opening in the east fence (y 12..24), the gate leaf swinging out to the back of the trailer with a short panel below it forming the unloading funnel. Step 1 ('Pull up and unload'): the rig stands beside the fence, rear at the gate (x 73..81, y 23..56), cattle walk straight into the holding pen.
- Bud Box slide: new first step 'Arrive' (the rig comes in on the loop from the north, top of the diagram, and drives down to the gate in the next step); the last cow sits in the unloading funnel clear of the gate leaf; the closing note moves to the last step. 8 steps.
- Bud Box slide: holding pen 12' shorter (bottom pulled up from 84' to 72'; chamfers, gate to pasture and labels moved up with it; cattle in the Hold step repositioned).

<!-- from line 618 -->
## 2026-10-14: walkways phased
- The walkway network is split at the arena's east edge (architect's markup): east of it, the walks to the Red House,
  the parking, the existing barn and pens, and the poultry barn are Level 1 (`walk`, about 5,300 sf); west of it,
  along the arena to the new barns and up between the cattle barns, Level 2 (`walk-2`, about 8,100 sf). On the
  barnyard slide the Level 2 walks show as future at Level 1; walks carry no NEW badge or Level tag. Level texts updated.
- Site plan slide: the walks phase with the barnyard there too (each carries its data-level, so Level 1 shows only the
  east walks); its Level 1 and 2 texts now name the walkways.

<!-- from line 695 -->
## 2026-10-19: existing barn and pens to the survey; campus fence on the lean-to column line
- **Existing pens flush with the barn (owner):** the 7 existing pens now run the barn's 80.4' length, flush with its
  west face (about 11.5' a pen), per the survey and the architect's sheet A2.0 Existing Barn. Project drawings had
  them on the 84' module, 3.6' proud of the barn's west face. The barnyard diagram stays pinned to the survey at the
  middle of the pens' north edge (`diagram_transform`, now at x 239.8), so the barn and pens sit on the surveyed barn
  (196.7..278.0 in diagram feet before, 1.8' closer now) and the new barnyard moves 1.8' west with them; survey-drawn
  context (Red House, carport, horticulture, residence, poultry barn) is recomputed and stays put. East edge, holding
  pens, and turnouts unchanged. Fit checks and paddock acres unchanged (cattle turnout B 45% on wet soil, was 44%).
- **Campus fence (owner):** east of the barnyard it now runs on the existing barn's lean-to column line (the pens'
  front, which is the walk's north edge) from the walk gate west to the lean-to's corner column 13' past the barn,
  north to the pens' back fence and along it to their north-east corner (`build_site_map.py`). The fence south of the
  walk (fence-10) stops at the walk's south edge, and a gate leaf spans the walk (8').
- **Walk to the unfinished barn:** its edges now run on to the corners of the barn's 12'-6" centre aisle, and the
  aisle is concrete end to end (part of the Level 1 walk). The walk is drawn after the barn so the aisle shows; the
  generated `drawings/ag-area-diagram.svg` now carries element names on their own top layer ("Names").
- Massing: `export_site.py` takes the fence route and walk from the deck (its model-only overrides are removed);
  `export_scene.py` fits the pens at the barn's width.

<!-- from line 713 -->
## 2026-10-19: cattle barns after the McIntosh Ag Center barn; 16' aisle
- Reference: `source/Clark Farm Study Plan-A2.0 Cattle Barn Reference.pdf` (Seibert, McIntosh MS Ag Center Bldg 19:
  108' x 64', 24' pen rows either side of a 16' aisle, 1:12 shed roofs over the pens, a 4:12 monitor over the aisle,
  ~19' ridge, sand bedding over gravel, broom-finish concrete aisle, galvalume, gate panels on the open sides).
  Owner's differences for ours: overhangs about 3'; our pen count (7 a side, 14 per barn, 84' long); no tack or feed
  rooms; the aisle 16' (was 14') for tractor access; walls red metal panel, or vertical wood siding to match the
  existing barn if the budget allows.
- Plan (`build_ag_area.py`): Option B cattle barns 64' deep (`CATTLE_W_B`; the original layout's 62' constant is left
  alone because it also sets the survey-fixed east column). The 2' goes north, keeping 24' clear to the arena row;
  the cattle turnouts move north 2' and holding pens 5 and 3 grow 2' north so their north edge stays flush with the
  barns'. Tractor-aisle arrow re-centred; the east dimension string now reads the holding pens as drawn; holding pen
  areas now from their drawn sizes (pens 4 and 5 had carried their pre-narrowing 60'-wide figures). Paddock acres
  and capacity unchanged; cattle turnout B 48% on wet soil (was 45%).
- Slides: `levels.js` aisle_ft 16; cattle pens slide footnote.
- Massing (`scene.py`): barns rebuilt to the reference section (heights scaled off it: shed roof ~10.4' to 12.4',
  monitor ~16.3' / 19'); sand in the pen rows, concrete in the aisle; gable ends clad with a 16' x 10' aisle opening;
  viewer toggle for the cladding (red metal panel / wood siding).

<!-- from line 745 -->
## 2026-10-19: small animal barns on the 12' module; arena bleachers
- Owner: dogtrot one 12' bay (was 15'), barn A's north end held and its south wing moved north 3'; barn B four 12'
  bays, 48' (was 41', the code-limit length); an 8' aisle with 6' x 10' pens either side and a 4' strip to the curtain
  line, as the reference barn. Arena keeps its dirt floor for now; two 4-row x 24' aluminium bleachers along its north
  side (plan zones on the arena; massing, with the arena rail moved in to clear them).
- **Code:** barns A and B together are now 5,616 sf with the dogtrot counted, past the 5,500 sf one-storey base limit
  for a Group U, Type VB building (IBC Table 506.2). Owner: the frontage increase (IBC 506.3) will cover it; the small
  animal pens slide says so. Small animal pens: 32 at Level 2, 48 at Level 3 (was 44).
- Plan: small animal turnouts follow (A 108', B 48'); the Level 2 walk stops at the wings, so it crosses through the
  12' dogtrot (it stays 15' wide east of the barn, as the architect drew it). Slide text for barn B updated
  (barnyard Level 3, Levels matrix).
- Rebuilt with the main-parcel-only flag (`siteframe.MAIN_PARCEL_ONLY`) on, as it stands in the working tree.

<!-- from line 873 -->
## 2026-10-20: holding pens to the dog-ear
- Holding block: west edge on the existing barn's front (as before); the east column (pens 1 to 3) now runs out to
  the end of the existing pens' lean-to roof, the dog-ear that carries on 13' past the barn's east wall (93.4' from
  the barn front, sheet A2.0 Existing Barn), instead of stopping at the barn's east wall. Pens 1 to 3 are 49.4' wide
  (2,075 / 2,322 / 2,421 sf). The dog-ear is drawn as an open canopy (`existing-dogear`, over the pens' front 12.5').
  North dimension string: 29.6' lane, then the 93.4' holding block; the east string moves out with it.
- The massing model (`Watercolor_Rendering_Working/scripts/scene.py`, `massing/export_scene.py`) has its own pen
  coordinates and still shows pens 1 to 3 at the barn's east wall.
- Same day: the 8' alley is centred in the 93.4' holding block, two 42.7' columns either side (pens 5/4: 2,092 /
  2,007 sf; pens 3/2/1: 2,092 / 2,007 / 1,793 sf). The handling yard's holding pen widens to the alley (its south-east
  chamfer moves with the wall; the Bud Box, lead-up, and chute keep their size). The walk's apron west of the existing
  pens now ends on the barn front line (the architect's file had it 3.6' short).
- South sidewalk restored (owner): 5' wide, Level 1, part of `walk`: the band 5' outside the parking loop's pavement,
  flush with its edge, from the walk network's stub by the dumpster down the one-way drive's east edge past the Red
  House's front porch and round the corner along the heads of the stall row in front of the horticulture area to the
  row's west end (about 277 ft). The horticulture area and the residence stay where they were and butt up to it (the
  walk draws over their edge).
- South loop squared to the Red House (owner): the architect's south lot ran about 0.4 to 0.6 degrees off the house.
  The Red House grid (`_U`) now comes from the house's own walls (length-weighted, 33.65 deg) instead of the parking
  sketch (33.03). In Option B the imported lot is corrected: the stall row turns about its north-west front corner
  (the joint with the west leg) and the one-way drive's outer edge about its north end (the joint with the east leg),
  so both meet the rest of the lot unchanged; their corner is recomputed, the nine angled stalls are redrawn on the
  row, and the swale island's diagonal sides turn with the side they face. The south sidewalk follows.
- Dumpster apron corner cleaned: the walk network's stub there is trimmed to the sidewalk's outer line, so the walk
  runs straight from the apron's south edge down the sidewalk.
- The south sidewalk carries on round the loop's turn at the stall row's west end, along the pavement edge up past the
  row's end and round the curve to where it straightens onto the entry drive (about 339 ft in all). The apron-corner
  trim is limited to the corner (it had cut the new stretch off).
- South loop on the Red House front (owner): the loop now takes its angle from the house's front (its westernmost
  wall and the front porch's outer edge, one line, about 0.4 deg off the walls' average) and the one-way drive's outer
  edge sits 5' off it, so the 5' sidewalk is flush with the house and porch. The drive edge's north end slides along
  the edge it meets; the stall row still turns about its joint with the west leg. The sidewalk no longer goes round
  the turn: along the stall heads it stops at the residence. The horticulture area and the residence (sizes kept) are
  set flush to the sidewalk's south corner, the residence alongside horticulture as before.
- Red House Level 3 addition on the plan (owner): `red-house-addition` (Level 3, education), the instructional
  classroom / event space with its restroom and storage core, as placed on the study plan A0.1 (east of the house,
  square to true north; about 71' x 33'), plus its entry canopy toward the house (`red-house-addition-canopy`, open
  canopy). The patio and walkway between them are not drawn. It shows on the site plans too.
- Dumpster enclosure centred on the drive aisle it opens onto (between the back of the double stall row, y 324, and
  the front of the row along the swale, y 348): now y 330 to 342.
- Architect's edits of 2026-10-20, made in Illustrator on the generated `drawings/ag-area-diagram.svg` (which every
  build rewrites): saved as `drawings/ag-area-diagram3.svg` and read by `build_ag_area.py` like ag-area-diagram2.
  Illustrator's export restarts the frame at 0,0, so its coordinates read as this diagram's feet less (-118, 11);
  nothing in the drawing moved. Taken from it: the circulation arrows as redrawn (the loop's north leg as its own
  aisle arrow, the middle aisle arrow redrawn, an arrow on the entry drive, a third animal arrow at small animal barn
  B's turnout, the pens' arrow centred in the alley), the compost area as moved (x 203.6, y 299, 44.5' x 19'), and
  the walk from the Red House to the addition's entry canopy (`walk-3`, Level 3; it was drawn in the names layer).
  The south sidewalk now runs on along the residence's north side to its far corner. The rebuilt diagram matches the
  edited file group for group. For further edits, save the Illustrator file under a new name (ag-area-diagram4.svg).
