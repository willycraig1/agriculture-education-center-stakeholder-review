# Site base map, alignment, water, and floodplain (through 2026-10-21)

Moved verbatim from the original NOTES.md. `<!-- from line n -->` marks where each entry stood.

<!-- from line 120 -->
## Shift of 2026-10-13
- Everything new moves 24' west and 24' south relative to the existing barn and pens (`DX, DY` in `tools/build_ag_area.py`); the layout is unchanged internally. Cattle turnout A is cut back to stop at the existing pens (96' deep instead of 120').
- Fit after the shift: wettest soil under buildings is down to the arena at 3% (cattle barn B 0%, extension 0%, all turnouts 0%). Nothing overlaps the existing barn or pens; parking is 47' from the existing barn. Parking takes in 14 surveyed trees and the handling yard 8 (22 in all, as before). South stall row about 23' from the nearest Red House wall.
- New conflict: the two existing surveyed structures (61' × 25', 35' × 29') that were in the cross drive are now under the south end of cattle barn A. The cross drive now lines up with the existing pens and stops at their west end.
- Dimension strings: 36' moved to the north end of the extension; east string completed (84 / 24 / 84 / 24 / 8 / 50, cattle barn B to the south end of the existing barn).

- 2026-10-13, later: the loop's west leg now continues the west lane between the runs (not the small animal barn's aisle) and is 20' wide, since no stalls open off it; this pulls the lot clear of the end of the entry drive. Stall rows fit 9 between the legs: 36 spaces (was 48). The lot is 139' wide. Trees inside the lot footprint drop from 14 to 10. The handling yard and trailer lane are left where they were and now sit 38' west of the lot, detached; the architect will rework the handling area next.

- 2026-10-13, tweaks: cattle turnouts' east edge lines up with the existing pens (turnouts 108' wide); turnouts are drawn behind the barn footprints; the small animal turnout grows north with the extension at Level 3 (126' long in all, 0% on wet soil); the parking lot moves 12' north so it is 24' (the cross drive) from cattle barn A. After this: south stall row about 30' from the nearest Red House wall; 12 surveyed trees inside the lot; no trees in the handling yard (it moved north with the lot).

- 2026-10-13, handling rework (architect's Illustrator edit, folded into the script): the trailer stop is now a 24'-deep pull-off bay with tapered ends on the west side of the loop's west leg (no separate lane, no gap); the handling yard (72' × 84', same internal layout) sits directly west of the bay, its north edge 11' south of the lot's north stall row. The small animal turnouts split at the barn/extension joint (84' beside barn A at Level 2, 42' beside the extension at Level 3). Circulation arrows have no arrowhead where a run ends on another run (three-way junctions): the lanes and tractor aisles at the cross drive or the loop, and the mid cross lane at the west lane. `slides/bud-box.html` shows the bay the same way.

- 2026-10-13, trailer bay per the architect's sketch over the Bud Box slide (my reading; two points to confirm): the bay is fenced along the loop side; trailers enter through a gate on the north taper, heading south, and leave through a gate on the south taper back onto the loop; there is no gate mid-way along the shared fence; the pen's south-east chamfer is a 22' receiving gate hinged at the bay fence, with the corner triangle behind it closed in as a receiving pocket open to the bay; the pen-to-lead-up gate (12') is hinged in the corner at the bay fence, with no fence return beyond the gate frame, and swings into the alley. Reading confirmed by the architect; this detail stays on the Bud Box slide only, not the barnyard diagram.

<!-- from line 134 -->
## Architect's site-plan edits (2026-10-13)
- Illustrator froze saving the full `site-layers.svg` (aerial plus survey linework), so the architect saved an edits-only `.ai`: `source/site-edits/site-edits-2026-10-13.ai`, drawn on the same artboard (artboard origin = map view origin 40, 110). `tools/import_site_edits.py` → `drawings/data/site-edits.json`; `tools/build_site_map.py` uses it when present.
- New site boundary (32 vertices) replaces the fence-derived footprint: takes in more of the slough, less of the south access road, simpler shape. Area inside it 158.5 ac (fence-derived outline: 152.4 ac). Soils, the outside-site veil and the land outline are clipped to it. Pasture acreages (45.1 + 54.5) are unchanged; they come from the paddock labels.
- Hand-drawn outlines replace survey linework for the two existing ponds and 10 existing structures. The third pond, beside the campus, is the proposed retention pond (my reading, by position): drawn dashed, hidden on the existing-conditions slide (`slides/site.html`), shown on the plan slides.

- The campus-side pond is confirmed as the proposed retention pond.
- Unfinished barn: not in the architect's outlines; taken from the survey, where it is an open roofed frame drawn as a dashed overhang rectangle with no walls (BUILDING OH, about 41' × 52', north of the existing barn). Added to the campus layer as `unfinished-barn` (identification is mine; confirm).
- Aerial: shown only on the first step of the site slide. It does not register closely enough with the drawings and is not worth correcting. Every later step, and the paddock and site-overlay slides, use a plain `ground` layer (site boundary with a pale fill) instead.

<!-- from line 143 -->
## Canopy, drives and Cowpen Slough from the aerial trace (2026-10-13)
- Source: `source/site-edits/aerial-trace-2026-10-13.svg`, the architect's Illustrator image trace of the County aerial (ten flat colours, half the aerial's pixel size, about 7,000 shapes). `tools/build_canopy.py` → `drawings/data/aerial-derived.json`; `tools/build_site_map.py` adds layers `canopy`, `drives` and the `slough` shape. It is placed with the aerial's registration, so it carries the aerial's misfit against the survey.
- Canopy = the three darkest trace colours (crowns and shadows) inside the site boundary, ponds and slough removed, gaps closed and specks dropped: 58.5 ac of the 158.5 ac inside the boundary (37%). The surveyed tree line is still drawn; the survey's individual trees cover the campus only.
- Drives = the lightest trace colour, thin long runs only (roofs and bare patches dropped). This picks up the road along the slough and the tracks, in broken stretches; the drives inside the campus do not separate out in the trace and still come from the survey's edge of pavement.
- Cowpen Slough = redrawn. The dark water band is found within 26 units of the west property line, its position and width are measured every 6 units along that line and smoothed, and the smoothed centreline is drawn at the median width (about 47'). The label follows the channel. The survey's interior top-of-bank lines stay, drawn thin.

<!-- from line 149 -->
## Alignment work (started 2026-10-13)
- Principle from the architect: the proposed fences follow the surveyed property lines closely, and the property lines on the fencing plan are the source of truth for alignment. The architect is adding the property lines to `source/Clark Farm Proposed Fencing Plan.pdf`; once they are in, re-register the aerial (and its trace) and the site boundary against them.
- Fences as polylines: `tools/build_fences.py` → `drawings/data/fences.json`. The plan plots each fence as separate dashes (and curved dashes as several tiny pieces per dash); the script takes each drawn path as one stroke, joins strokes end to end where the gap is under 24 units and the direction holds within 14°, simplifies each chain to its corners, snaps loose ends onto the fence they meet, and merges. Result: 39 runs, 130 vertices, about 29,800 ft, in sheet coordinates and map coordinates. The site map draws these instead of the raw dashes.
- Known rough spots: the dashed pond outlines are left out on purpose; a few short joins near the 5.2 ac paddock and one hook at a pond edge need a manual check; paddocks are not yet closed polygons.

- 2026-10-13, property lines in: `source/Revised fencing plan with PL.pdf` is now the fencing source (`FENCE` in `tools/siteframe.py`; the first plan is kept as `FENCE_V1`). Same sheet frame as before (501 of 568 fence end points identical), property lines on layer SECTION LINE, and the 7.7 and 2.5 ac bonus paddocks merged into one of 10.2 ac (15 paddocks; totals still 45.1 + 54.5).
- `tools/build_fences.py` now also chains the property lines (7 runs; the west line along the slough is two runs meeting at the interior parcel line) into `fences.json` → `property_lines`. Fences: 42 runs, about 29,100 ft.
- Checks against the property lines: the survey's BOUNDARY layer, through the existing survey registration, sits a median 2.1 ft from them (90% within 2.9 ft), so the survey-based layers (trees, soils, buildings, barnyard anchor) were already good. The aerial was the layer that was off: median 15 ft.
- Aerial re-registered to the property lines (`tools/register_aerial.py` → `map_to_aerial_pl` in `registration.json`): median residual 6.6 ft (about 2 px); the aerial and its trace move 36 ft at the campus, 29 ft at the north-west end, 50 ft at the south end; scale −0.5%, rotation −0.5°. Canopy, drives and the trace follow. Canopy is now 60.4 ac.
- Cowpen Slough is drawn centred on the west property line (the centreline of the waterway), 48 ft wide; the width is the median measured on the trace. After re-registration the traced water sits a median 11 ft from that line.
- The architect's hand-drawn site boundary is a display boundary: it follows the earlier, misplaced aerial on the west (6–31 ft off the property line there) and runs well outside the property line elsewhere. The property lines are drawn as their own layer (`property`).

- 2026-10-13, alignment round 2:
  - Fences: the north triangle was disjointed because (a) the four runs meeting in its middle stop short of a gate symbol and (b) one curved stretch of its boundary is plotted as a solid polyline that had been filtered out as a drive. `build_fences.py` now pulls run ends that stop within about 20 units of one another to a single junction point (before T-snapping), and takes a long solid polyline as fence when both its ends meet fence strokes. Result: 25 runs, 114 vertices, about 30,100 ft.
  - Aerial: the similarity fit could not hold both sides of the site; the east line matched at the north end and drifted toward the south. The plan's layer is called SECTION LINE, and the aerial shows two yellow lines along the east road; the plan's east line corresponds to the site-side one. `register_aerial.py` now fits an affine transform (`map_to_aerial_affine`) to the west curved line (nearest yellow) and the east straight line (site-side yellow only). Median residuals: east 1.4 ft, west 2.0–5.6 ft. The aerial is stretched about 3.8% more in one direction than the other. Not fitted, as a check: the interior line pl-04 is 29 ft from its yellow line (was 56–68), pl-06 and pl-07 do not have a matching yellow line nearby.
  - Movement against the first registration: 28 ft at the campus, 1 ft at the north-west end, 44 ft at the south end, 79 ft at the south end of the east line. Canopy 60.9 ac; traced water a median 10 ft from the west property line.
  - The trace's drives layer is no longer drawn (fragmentary, and falling inside pasture enclosures).

- 2026-10-13, round 3 (corrections from the architect):
  - Pinwheels: where four paddock fences meet they are deliberately offset, each ending in a gate, around a small shared space for centralised feed and water. My junction clustering had collapsed these to a point; it is removed. Fence ends within 8 units of a gate leaf are now left exactly as drawn (no joining, no snapping). The plan has three pinwheels (north triangle, the 14.4/4.9/3.8 area, the 13.0/10.2 area).
  - Gates: drawn from the plan's A-DOOR layer (leaf plus swing arc), in the cattle colour, in the `paddocks` layer (`#gates`); also in `fences.json` (`gates`, `gate_arcs`, `pinwheels`). 34 gates: 23 drawn at 16', 10 at 14', 1 at 12'. The architect's intent is 16' at every location; the drawing shows them as plotted.
  - Cowpen Slough ends: the property line turns away from the waterway at each end of the site; the slough line is cut back to its last straight stretch there and carried on 100 ft along that heading.
  - South bonus pasture buildings (fencing plan layer P-WALL, 5 outlines) are drawn again; they had dropped out when the architect's structure outlines replaced the survey linework.

- 2026-10-13, round 4 (architect's markups of the north triangle and a pinwheel):
  - Pinwheel geometry, as on the plan: each fence carries its gate hinge one gate length before its end, so a fence stub runs on past the hinge; the gate closes from the hinge to the end of the neighbouring fence and opens back along its own fence. My guard had been cutting the stubs off (they were treated as separate short runs and dropped). Pieces of the same fence may now join at a pinwheel (heading within 6°); different fences never do.
  - T-snapping no longer moves a fence end (it had dragged the triangle's west line 5 units onto a neighbour, which is why it missed its gates). A run is only extended along its own heading, by an added vertex, and never at a gate.
  - Layer P-BELOW-LIGHT on the fencing plan is the architect's circulation sketch plus pond outlines: no longer read as fence (this removes the phantom fence round the pond) and no longer drawn as grey drive lines.
  - Roads: the survey's edge-of-pavement lines (366 short pieces) are chained into 7 continuous polylines (`fences.json` → `roads`), bridging dash gaps up to 16 units where the heading holds within 9°. No Illustrator work needed for these.
  - "Feed + water" label at each of the three pinwheels.
  - Fences now: 26 runs, about 29,700 ft.

<!-- from line 181 -->
## Water quality
- Reference given by the Owner's side: the 2025 Water Quality Playbook, Gulf Coast Community Foundation (https://waterqualityplaybook.org), a regional blueprint for reducing nutrient pollution, organised as Reduce / Remove / Sustain. Most relevant actions: 4.6 (education and resources for farmers and ranchers: rotational/adaptive grazing, manure management, silvopasture, composting, FDACS BMPs incl. the 2024 Small Farms manual, UF/IFAS outreach to small farms), 4.7 (composting, rebuilding soils), chapter 2 (septic), chapters 6–7 (stormwater, 7.4 demonstration projects), 8.1 (wetland and shoreline habitat). It does not cover livestock exclusion from water or riparian buffers directly.
- Figures used (action 4.6, citing USDA 2022): 286 farms in Sarasota County, about half under 10 acres; cow/calf is 59% of farms; about 46% of registered, eligible farmland is in FDACS BMP programs; only about one-third of farms under 10 acres are enrolled.
- Slide `slides/water-quality.html` (Act 5): site measures grouped under Reduce / Remove / Sustain, each tagged with the Playbook action it follows. The site measures come from the draft program criteria (§3.7, D.5, F.2, J.3–J.5) and the study plan (retention area, bioswale). Page 7.4 could not be fetched (server error); its title is cited only.

<!-- from line 191 -->
### Alignment round 5 (2026-10-13)
- **Road as one shape.** `tools/build_fences.py` joins the three open road-edge runs across each mouth of the road
  (north entry, south end, campus branch at the Red House) into a closed ring, with the two closed runs as islands;
  written to `fences.json` as `road_area` (1.71 ac) and drawn filled on the campus layer (`#road-area`).
- **Gate on the 4.8 ac paddock.** The plan jogs the last 7 ft of that fence over to the gate hinge; the stroke was too
  short and too sharply turned to chain, so the gate straddled the fence end. Runs are now carried on to a gate hinge
  that sits within 6 units of a run end but not on any run (1 case). Short fence stubs that carry a gate are also
  kept (the west arm of the pinwheel in the 10.2 ac paddock).
- **Open canopies.** From the survey's overhang lines (BUILDING OH): cattle pens lean-to along the existing barn's
  west wall (about 21' x 96', 1,830 sf), a small canopy at the barn's north wall (14' x 18'), and the carport at the
  Red House (29' x 38'). Drawn tinted with a dashed outline (`#canopies`), enclosed buildings stay solid. The
  unfinished barn (41' x 52') and the 27' x 10' shed north-west of the pens and the 12' x 10' canopy at the pasture edge west of the campus were moved to the same open-canopy
  style at the architect's request.
- **Slough, north end.** The property line turns a sharp corner onto the site's north line; that leg is 540 ft long, so
  the earlier end trim (short hooks only) left it in. `_tidy_end` now cuts at any corner over 40 degrees within 320
  units of an end, then extends 100 ft on the channel's heading.
- **Trees.** Surveyed trees are plain discs at 70%% opacity with no white outline; the survey's dashed tree line is no longer drawn (the canopy traced from the aerial replaces it).
- **Tree count corrected.** On the study plan each tree symbol came through as up to four marks stacked within a foot, so trees were drawn as stacked discs and counted several times. `siteframe._one_per_tree` keeps one mark per tree: 176 surveyed trees (80 study plan, 96 survey), not 362. Fit check: 3 trees in the parking footprint, not 12.
- **South roads (approximate, not survey).** `tools/build_south_roads.py` → `drawings/data/south-roads.json`, merged
  into the road shape by `build_site_map.py`. Three centrelines: the lane along Cow Pen Slough from the end of the
  surveyed road to the south building drive (located from the aerial trace's drive pixels on 89 of 143 sections,
  bridged and smoothed between; drawn 19 ft wide, the surveyed road's width at its south end), and the two drive
  lines on the fencing plan's sketch layer that the aerial confirms (lane → house loop → long barn → east property
  line; lane → south building and round it), drawn 12 ft wide. Run order: build_fences, build_canopy,
  build_south_roads, build_site_map.
- **Road tidy-up.** The south lane now starts on the middle of the surveyed road's end and the two read as one
  road (the stub toward the slough was the lane's first section, sampled past the end of the property line). The
  32 ft pavement stubs beside the lane are no longer part of the road shape.
- **Entry apron (architect, 2026-10-13).** A new entry apron off the lane is part of Level 1; the stormwater design
  requires it. The existing flared apron and island are still drawn as surveyed. The entry arrow on the site slide
  sits on the centreline of the straight entry drive and ignores the apron. Mentioned in the Level 1 text of the
  barnyard-on-site slide.
- **Slough linework and label.** The survey top-of-bank line that runs along Cow Pen Slough itself is no longer drawn.
  The other four top-of-bank lines are kept for now: they trace the historical slough bed across the site, and the
  architect wants to work on how they are shown. The "Cowpen Slough" label moved to the middle of the slough's
  longest straight reach (beside the site pasture), upright, on the off-site bank.
- **Stakeholder question added** (input slide, Water and wet ground): how sacred is the historical slough bed? It
  conflicts with some of the program and complicates the civil design.
- **Historical slough bed.** `tools/build_slough_bed.py` → `drawings/data/slough-bed.json`: one field from top of bank
  to top of bank (3.4 ac, about 40 ft wide on average), built from the survey's TOP OF BANK, TOE OF SLOPE and EDGE
  OF WATER layers. 11 of the 45 bank pieces belong to the old channel (those with a toe or water edge inside them);
  the rest are roadside ditch and Cow Pen Slough banks. Gaps in the banks (drive crossing, culverts) are bridged
  along the toe lines. Drawn in the water layer at 32% opacity with a label, in place of the bank lines; added to
  the Water step's text and legend on the site slide. The earlier map drew only 5 bank pieces because of a size
  filter. The survey stops at its sheet edge: the bed's north-east arm (toward the 8 ac paddock) and the arm up to
  the pinwheel end there. `source/1948 Aerial of historic Slough Bed.jpg` (north up) shows the original meandering
  channel before Cow Pen Slough was straightened; not yet registered to the map. Run order: build_fences,
  build_canopy, build_south_roads, build_slough_bed, build_site_map.

<!-- from line 240 -->
### Water on the site slide (2026-10-13)
- **New slide** `slides/water-site.html`, placed before the water quality slide (Act 5). Four steps on the site map:
  the 1948 aerial; what is left (canal, historical bed field, ponds, with the 1948 photo faint underneath); wet
  ground (soils); where the plan meets it (barnyard overlay, proposed retention pond). The stakeholder question on
  the slough bed appears beside the map on the last step.
- **1948 aerial registered.** `tools/register_aerial_1948.py` matches the yellow parcel lines of
  `source/1948 Aerial of historic Slough Bed.jpg` to the current County aerial's (same web map, so zoom and shift
  only: zoom 0.8325, shift 185, 13 px; the best match scored 266 against 162 for the next zoom tried) and chains
  that with the current aerial's fit to the property lines. Stored as `aerial_1948` in `tools/registration.json`;
  drawn by `build_site_map.py` as layer `aerial1948` (hidden unless a slide shows it), clipped to the site plus a
  margin so the web map's search box and labels stay out of view. The County's own placement of the 1948 photo
  under its parcel lines is approximate.
- **Bed against the plan.** `SITE_MAP.slough_bed`: 3.38 ac; the only proposed barnyard element the surveyed bed
  crosses is a turnout (about 2,320 sf). It also passes under the existing entry drive.
- **Act 1 site slide:** the historical slough bed stays on the Water step but downplayed (16% fill, no map label, legend entry only, no sentence in the step text). Water-site step 1 now says the waterway was "channelized".
- **Ditch floor.** `build_slough_bed.py` now also writes the toe-of-slope lines and the floor between each pair
  (0.43 ac, about 7 ft wide). The map draws the floor darker than the banks with the toe lines fine on top
  (`#historic-slough-floor`); hidden on the Act 1 site slide, where the bed stays downplayed.
- **Site boundary, west side.** `siteframe.snapped_boundary()` swaps the run of hand-drawn boundary vertices that
  follow the west property line (they were up to about 65 ft off in the south) for the property line itself, the
  centreline of Cow Pen Slough. Used by `build_site_map.py` and `build_canopy.py`. The source edits file is not
  changed. Site area 158.5 → 154.9 ac; canopy 60.8 ac of it.
- **Ditch floor fill widened.** Where the two toe lines swing apart (the bend east of the retention pond) the floor was left unfilled; the fill now thickens by twice the usual bank-to-toe distance and is clipped to the bed. Floor 0.57 ac.
- **Compensation area, for discussion.** A possible compensation area (about 1.1 ac) on the open ground east of the head pond, between the historical bed and the flood zone line, traced by eye from the architect's markup (`COMP_PTS` in `build_site_map.py`). Not designed or sized. Drawn dashed with a label, hidden everywhere except the last step of the water site slide, where the text and legend name it. The earlier request to extend the two cut-off slough arms from the 1948 aerial was cancelled; nothing was changed for it.
- **Retention pond acreage.** The proposed retention pond measures 0.8 ac from the architect's outline; with the 1.1 ac compensation area that is 1.9 ac. The water site slide's plan step labels both on the map with their acres and says the two together are intended to compensate for the new campus elements (the architect's intent; no compensation calculation has been done here).
- **Drainage infrastructure (architect, 2026-10-13).** Two solid lines on the map (`#infrastructure`, hidden unless a
  slide shows it), drawn between the surveyed ends of the ditch floor; diagrammatic, the pipes are not on the survey.
  *Entry culvert* (red, about 123 ft as drawn) joins the bed either side of the entry drive: to be replaced for
  sizing and maintenance. *Outfall* (green, about 98 ft as drawn) runs from the south end of the bed to Cow Pen
  Slough: civil says it is in good shape and sized for the plan. Shown on a new fifth step of the water site
  slide, "The pipes that connect it". The step text ties the culvert replacement to the new Level 1 entry apron.
- **Outfall taken from the survey.** The outfall is on the survey's STORM SEWER layer (two lines, the walls of the
  pipe run, 78 ft, under the ±11' asphalt lane). The map now draws it there instead of my estimate. The survey
  detail sheet (`source/260036_SPS_Draft for FE_9-4-26.pdf`, sheet 10; its text is drawn as linework, so it was
  read by eye) notes "(2) 36" CPP End of Pipe" at both ends: invert 16.47' at the bed end, 16.00' at the slough end.
  The map label and step text carry the pipe size and inverts. The entry culvert is not on the STORM SEWER layer;
  its line is still diagrammatic. Lesson: check the survey's utility layers before estimating infrastructure.
- **Entry culvert shortened.** Its line now runs only where it passes under the driveway, plus 8 ft beyond the pavement on each side: about 27 ft as drawn (the drive is about 11 ft wide where the line crosses it).
- **Fourth pinwheel labelled.** The pinwheel in the middle of the site pasture (12.4 / 8 / 4.8 / 3.4 ac) had no "Feed + water" label: the plan draws its four gate swings but no gate leaves, and pinwheels were being found from leaves. They are now found from the swing arcs: 4 pinwheels. That one still shows arcs only, as on the plan.
- **Leaves added at the central pinwheel.** `fences.json` `gates_added`: four leaves, each from its swing's centre (hinge) to the arc end on its fence, about 14 ft long because the plan's arcs there have a 14 ft radius (the others are 16 ft). Drawn in the same style as the plan's own leaves (`#gates-added`).

<!-- from line 281 -->
### Pasture colour fields (2026-10-13)
- **Paddocks as closed shapes.** `build_site_map.py` thickens the fence lines until the gate openings close, which
  cuts the site into faces, and grows each face back to the fence line. The two fence ends that stop short of each
  other at the 3.8 ac paddock are joined first. All 15 paddocks come out within 0.3 ac of their labels.
- **Paddocks slide:** each paddock is filled in its area's colour (site pasture green, bonus pasture olive, 30%
  fill with a solid edge in the same colour) under the fence lines. Bonus fills appear with the bonus step; the
  rotation highlight now also darkens the paddock being grazed.
- **Act 1 site slide, "The land" step:** the two pasture areas are shown as plain colour fields with no paddock
  lines (`#pasture-areas`), since fences are not proposed until Act 5.
- Fills are hidden on the barnyard-on-site slide. Colours are the palette's `pasture` and `bonus`.

<!-- from line 306 -->
### Capacity from the areas as fenced; poultry (2026-10-13)
- **Paddock acres.** `drawings/data/paddocks.json` (from `build_site_map.py`): each paddock keeps the fencing plan's
  own acreage, adjusted only where a fence has moved since, by the change measured between the plan's fence and the
  redrawn one. Two paddocks changed with the campus fence: 3.4 → 3.7 ac (open pasture, west of the campus) and
  8.0 → 7.8 ac (dense woods, north of it). Site pasture 45.1 → 45.2 ac; with bonus 99.6 → 99.7 ac. Map tags and
  the Site pasture total use these.
- **Capacity.** `build_capacity_data.py` now reads those acres (worksheet's dense-woods shares and AN155 rates
  unchanged): 7.0 → 7.1, 14.4 → 14.5, 27.5 → 27.6 CE. Rounded planning figures are now **7 / 15 / 28** (were
  7 / 14 / 27): Levels 2 and 3 sat just under a half and the extra 0.3 ac of open pasture tipped them over. The
  source worksheet is not edited. Hard-coded mentions updated (water quality slide, outline). Run order:
  build_fences, build_canopy, build_south_roads, build_slough_bed, build_site_map, build_capacity_data.
- **Poultry (architect correction).** Poultry is not a "small animal": it is housed in the unfinished barn from
  Level 1 and stays there at every Level. Levels matrix split into a Poultry row (unfinished barn, same at all
  Levels) and a Small animals row (Level 1 "None yet", marked to confirm; barn A at Level 2; extension at Level 3).
  Map label on the unfinished barn reads "Poultry".
- **Levels matrix:** swine and small animals merged into one row, "Swine & small animals", in the swine pink (same kinds of pens and barns); the separate Small animals row and its "None yet" cell are gone. Poultry keeps its own row. 7 / 15 / 28 CE accepted by the architect: the land dictates the number.

<!-- from line 340 -->
### Compensation area widened after civil's note (2026-10-13)
- **Civil's strategy (email to the architect, 2026-10-13; report and quantities still to come):** a larger, more
  expansive floodplain compensation area at a shallower depth, so water levels stay lower outside major storms
  and the area keeps its grazing vegetation; minimal change to the historical stormwater flows; less and cleaner
  stormwater discharged to Cow Pen Slough. Stormwater treatment and added storage are a separate matter (County /
  SWFWMD) from floodplain compensation, though treated similarly.
- **Map:** the discussion-only compensation area grows from 1.1 to 2.3 ac: the open ground of the 4.8 ac paddock
  east of the head pond, between the flood zone line and the historical bed, as far as the paddock's east fence
  (`COMP_PTS`, extent chosen by eye). Label and step text say it is only a few inches deep and stays in grazing.
  With the 0.8 ac retention pond: 3.1 ac. No depth figure or quantity from civil yet.

<!-- from line 427 -->
### Civil's stormwater comments (email from John Monville, 2026-10-14; report with numbers due Friday)
- **No phasing of site work.** Permitting, stormwater and floodplain compensation are done for the whole plan up
  front (at Level 1); only the interior development is phased. Doing compensation phase by phase would disrupt the
  pastures. Added: a Levels matrix row ("Site work: stormwater, floodplain compensation": all at Level 1), a
  sentence on the three-levels slide, the water quality slide's civil line, and a new water-site step.
- **Retention:** the retention shown is undersized and is to be expanded, preferably as civil sketched (cyan, along
  the barnyard's north and west edges) to save cost and underground piping.
- **Floodplain:** the whole site is in the floodplain; nearly all fill needs compensation. The spoil could cover
  the adjacent County landfill (which the property was likely bought for). Option 1 lowers an area uniformly by
  stripping topsoil and reseeding/resodding (drainage unchanged); Option 2 clears/grubs and lowers a larger area,
  costlier and may need connectivity, but the biggest grazing gain (low forage value today). Both spread wide and
  shallow to stay as dry as possible.
- **Finished floor 21.70'** for covered livestock buildings, slightly above the County model's 100-year level;
  little freeboard; civil leaves the cost/benefit of going higher to the team. Added as a fact on the water-site
  slide and as a question for the tables (water-site and closing slide).
- **Sketches placed** by `tools/build_civil.py` (sources in `source/civil/`): retention expansion 0.6 ac (two
  parts), Option 1 4.4 ac (paddock north-west of the campus), Option 2 13.0 ac (the north pasture). Drawn on the
  new water-site step "Floodplain compensation, all at Level 1"; they replace the discussion-only compensation area.
  **Conflict:** civil drew the retention against the study plan's older barnyard, so as placed it overlaps cattle
  barn B (~1,800 sf), its turnout (~3,200 sf), holding pens 1-3 (~6,900 sf) and the arena edge; Option 1 overlaps
  cattle turnout B (~2,600 sf). To resolve with civil.
- Parking sketch saved as `source/site-edits/parking-sketch-2026-10-12.png`.
- **Wildcard retention (architect, 2026-10-14):** the County's Solid Waste department controls the property and drew
  the site line somewhat arbitrarily; it is open to IFAS using more of its land (hence the bonus pasture). The same
  approach could put extra retention ponds in the bonus pastures near the outfall. Shown on the water-site
  compensation step as a dotted zone (`#wildcard`): the bonus paddocks within 300' of the outfall, the 3.8 ac and
  8.2 ac paddocks (12.0 ac), not a design. The Solid Waste point is also added to the Act 1 site slide's "The land"
  step. The compensation step's text was shortened and the options moved to a list beside the map; the second
  "for the tables" box (freeboard) was dropped from that slide to fit; the question remains on the closing slide.
- **Retention from the architect's markup (2026-10-14)** — `tools/build_retention_markup.py`, source
  `source/site-edits/retention-markup-2026-10-14.webp` (a screenshot of the water slide's map, placed by a
  scale-and-shift fit on eight labels in it, max residual 2.8 px). Red outlines filled; each pond split at the
  parcel line pl-04 (the dash-dot line between the County site and the Solid Waste land). Result: **new retention**
  on the site between the historical bed and the lane, 0.5 ac (plus a sliver by the proposed pond); **bonus
  retention** on Solid Waste land, 3.3 ac: that pond and the proposed retention pond extended south, plus two more
  ponds past the outfall drive. Replaces the wildcard zone, which was too far south to use without underground
  equalization pipes (architect). "Wildcard" renamed "bonus", matching the bonus pasture.
- **Entry apron cleaned up:** on the map the drive is carried to the lane's surveyed near edge with 10' curb returns
  (computed in map coordinates in `build_site_map.py`; the barnyard diagram keeps its rough lane position). The old
  flared apron and island beneath are covered with ground colour on the plan views; the entry culvert is redrawn
  over that patch, still under the new drive (`.infra-copy`). Act 1 still shows the existing apron.
- **Ponds cleaned up (architect's markup):** the markup's pond beside the proposed retention pond is merged into it
  (no line between them) and each pond's edges run straight across the parcel line (convex hull of its part within
  60' of the line). Site retention pond by the campus 0.9 ac (it replaces the drawn pond on the map); second site
  retention pond 0.4 ac. Bonus retention 3.3 ac in four ponds (1.0, 0.7, 0.6, 1.0 ac), each labelled with its own
  area. Labels now read "Site retention pond" (not "Retention pond" / "New retention").
- The second site retention pond (0.4 ac) is its own group (`#site-retention`) shown on every plan step of the water slide (steps 4-6), with the site retention pond; only the bonus ponds wait for the compensation step.

<!-- from line 560 -->
## 2026-10-14: civil's retention refitted as a site retention option
- Civil's expanded retention (sketched on Option A) ran under the Option B cattle turnouts and pens. Refitted in
  `tools/build_site_map.py` to the architect's markup on the water slide, as two clean diagrammatic ponds rather
  than civil's sketch line: a west pond in the paddock between fence-19, the campus fence and the old bed, and a
  south pond between the small animal turnout's fence, the campus's east fence and the old bed. Each is kept about
  11 ft clear of new elements, fence lines and top of bank, simplified to a few straight sides, corners rounded.
- Renamed "Site retention option" (0.2 ac and 0.4 ac, labelled each); water slide legend and notes list updated.
  Not designed or sized.

<!-- from line 574 -->
## 2026-10-14: historical slough bed in pasture green
- The bed's bank-to-bank field is now a transparent pasture green (most of the time it is grassed pasture); the ditch
  floor between the toe lines stays blue. Water slide strong state .45 (was .6); legends on the water and site slides
  updated ("Historical slough bed, grassed" plus "Ditch floor" on the water slide). Trial, to review.

<!-- from line 803 -->
## 2026-10-19: main parcel 65.1 → 61.3 ac (site outline trimmed to property line pl-01)
- The deck's main parcel measured 65.1 ac against the SCPA's published 60.83 ac. Cause: the architect's hand-drawn
  site boundary (`site-edits-2026-10-13.ai`) runs a steady 54 to 59 ft outside property line pl-01, the long top
  edge of the north-left plans, for its whole length. That strip was 4.0 ac. The property lines alone (pl-01, pl-04,
  pl-02, with the 82 ft gap at the corner of pl-01 and pl-02 closed straight) enclose 61.1 ac.
- `siteframe.snapped_boundary()` now also trims the boundary to the inside of pl-01 (extended past both ends), so
  build_canopy, build_site_map, and build_retention_markup all use the trimmed site. Main parcel 61.3 ac (0.8% over
  SCPA; the rest is likely the slough centreline and the corner closure). Whole property 154.9 → 149.4 ac.
- Figures that follow: canopy 28.1 → 26.6 ac (still 43%), very poorly drained still 13%, slough bed 2.4 ac, paddock
  acres unchanged (fenced pasture 45.3 ac, 7 / 15 CE). Slides compute these from site-map.js, so no text changed; the
  site slide's "The land" now reads about 61 acres. Massing `site-data.js` re-exported (boundary and canopy only);
  the published 3D artifact has not been republished. The report reference archive keeps the old figures.
