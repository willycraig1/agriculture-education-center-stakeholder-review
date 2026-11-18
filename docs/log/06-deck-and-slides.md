# Stakeholder deck and slides

Moved verbatim from the original NOTES.md. `<!-- from line n -->` marks where each entry stood.

<!-- from line 73 -->
## Viewer
- `design/viewer.js`: shared pan/zoom for any drawing on a slide (scroll = zoom, drag = pan, pinch, double-click = reset, preset chips, live scale bar, north arrow). Elements tagged `data-fixed` / `data-w` keep near-constant size on screen. Used by `slides/site.html` and `slides/red-house.html`; use it for every new drawing slide.

<!-- from line 76 -->
## Review link
- Deck: https://willycraig1.github.io/agriculture-education-center-stakeholder-review/ (GitHub Pages from `main`). → / space / click step through builds then slides; ← back; F fullscreen; Slides menu in the bottom bar.
- Red House slide: `tools/build_red_house.py` aligns sheets A1.0–A1.0-3 by wall cross-correlation (offsets in `drawings/data/red-house.json`) and diffs walls Level to Level.
- Sheet A1.0-3 crops the plan (addition off the top-left, porch/storage off the bottom). Repaired in the build: the addition comes from the sheet's own orthogonal inset, rigid-fit onto its placed position (98.6% of on-sheet walls within 1 pt; rotation 141.4°, i.e. the addition is aligned to true north), and the bottom strip comes from Level 2, where it is unchanged. Repairs carry class `repair` in the SVG. A re-plotted sheet with the whole plan inside the border would replace both.

<!-- from line 351 -->
### Design-driver icons carried through the deck (2026-10-13)
- The four icons from the design drivers slide are defined once in `design/deck.js` (`Deck.drivers`) and drawn at the
  top right of any slide whose `<body>` has `data-drivers="…"` (pasture, reuse, module, water), with the driver's name.
- Tagged: **Protect the water** on water-site and water-quality; **Pasture is scarce** on pasture-capacity and
  paddocks; **Reuse first** on existing and red-house; **Grow by module** on cattle-pens, levels and ag-area (on
  cattle-pens the tag sits left of the sticky note). Not tagged: site, program, bud-box, site-plan, input, where no
  single driver leads.

<!-- from line 375 -->
### Firm credit and review date (2026-10-13)
- **Stakeholder review moved:** Wednesday 2026-10-21, 5:30 pm, Extension Green Room (cover slide and outline updated).
- **"Seibert Architects" footer** on every slide except the cover (which already credits the firm): drawn by
  `design/deck.js` (`Deck.firm`), small letterspaced caps at the bottom right, inside the stage's bottom margin.
  Checked clear of content on all slides. The Bud Box slide's all-steps (static) view was running past the bottom
  of the stage; it is now compact enough to fit.
- Residence keeps the education colour (architect).
- **Barnyard slide opening view** tightened (architect): from the west side of the cattle handling yard to the dimension strings on the north and east, and down to the parking loop's in/out notes. Holding pens, Red House, horticulture and residence are reached by panning. The plan panel is wider than this frame, so a strip of the holding pens still shows at the left edge.

<!-- from line 569 -->
## 2026-10-14: water slide framing
- Step 5 (compensation) frames the compensation options west to east through the bonus retention ponds
  (`frames.comp`) instead of the full site. Step 6 (pipes) zooms out slightly and pans so both pipe notes clear the
  step panel and the map's right edge.

<!-- from line 579 -->
## 2026-10-14: barnyard slide framing by step
- Levels 1 to 3 on the barnyard slide open close on the barnyard (`tight` in `slides/ag-area.html`, from the small
  animal turnout's dimension string to the east dimension string, per the architect's screenshot); the Flow step
  flies out to the whole diagram (and static mode shows that view). Reset returns to the step's framing.

<!-- from line 592 -->
## 2026-10-14: Act 1 campus step framing and labels
- The campus step on the site slide frames from the entry arrow at the lane up to the unfinished (poultry) barn, in
  the part of the map the step panel leaves open. Labels added on or beside each existing building: Red House (now
  centred on the house; it sat off to the east), Existing barn, Cattle pens (the lean-to), Unfinished barn, Carport.

<!-- from line 597 -->
## 2026-10-14: program slide animals regrouped
- Act 2 program slide: "Swine, sheep and goats" is one need (pink swine swatch: shared 6' x 10' small-animal pens,
  hog-proof, interchangeable), and Poultry is its own need (predator-safe housing, apart). Matches the Levels grouping.

<!-- from line 601 -->
## 2026-10-14: Act 3 swine, sheep & goat pens slide
- New `slides/small-animal-pens.html` after the cattle pens slide, in the same format: Level 1 reuses the hog pens in
  the existing barn (no count on record); Level 2 small animal barn A, 32 pens (two 16-pen wings and a roofed
  dogtrot); Level 3 adds barn B to the south, 44 pens in all, about 5,472 sf against the 5,500 sf Group U / VB limit.
  Plans drawn lengthwise at one scale, north to the left, read from `data/ag-area.js` so they follow the barnyard plan.
- Level 1 (architect): the 10 existing hog pens give way to the Level 1 site improvements, so the hogs move into the existing barn,
  which fits about 32 pens. Barn A at Level 2 (32 pens) is then a clean swap that frees the existing barn for
  much-needed storage. Updated on the pens slide (Level 1 ≈32), the Levels slide and the barnyard slide's Level text.

<!-- from line 610 -->
## 2026-10-14: Oxford commas
- House style is the serial (Oxford) comma in every list of three or more, across the slides, levels.js, and labels.
  The deck was converted throughout; compound items keep their inner "and" ("feed and tack storage").

<!-- from line 614 -->
## 2026-10-14: pinwheel gate weights
- The four gate leaves added at the main pasture's pinwheel lacked `data-w`, so the viewer did not counter-scale them
  on zoom and they drew heavy on the close paddock framings. They now carry it, like every other gate and fence.

<!-- from line 626 -->
## 2026-10-14: table questions from the ag consultant
- "Over to you" slide: water oaks along the entry drive (poorly suited, drop limbs on the drive; OK to thin?) under
  Wooded pasture; the consultant's manure spreader recommendation (over more complex nutrient recovery) under Animals
  and operations; a new Demonstration card (which areas, which cutting-edge practices). Layout now three columns, with
  Water and wet ground running the full height of the middle one.

<!-- from line 639 -->
## 2026-10-14: bioswale on the water slide
- The parking lot's bioswale (island_poly, class `bioswale` on the site map) is picked out in a stronger water fill and
  labelled "Bioswale" (`#bioswale-label`, hidden unless a slide shows it) on the water slide's plan steps; added to
  step 4's legend.

<!-- from line 659 -->
## 2026-10-15: cover illustration
- `tools/build_cover_art.py` draws `drawings/cover-perspective.svg`: a watercolour-style SVG sketch (not a rendering)
  of a 4-H student leading a heifer past the existing barn (from photos/barn.jpeg: weathered board-and-batten, four
  roll-up doors, lean-to with gate), the open-sided arena canopy behind at left and white monitor-roof barns and a
  tractor beyond (after the reference project's photos, Seibert Architects MMS Ag Farm, Ryan Gamma Photography), live
  oak with moss and cabbage palms, late-afternoon sky. Deck palette; fades into the slide paper on its left edge.
- Placed on the cover (`slides/title.html`) at the right of the slide; the text column is held to 900px.
- Superseded the same night: the cover now uses the architect's own watercolour (`photos/cover-watercolor.webp`,
  2000 x 1200), set at the right of the slide (1040px wide, cropped from the right so the arena, existing barn,
  tractor, and student with heifer stay in view) and masked to fade into the paper under the title. The SVG sketch
  and its script remain in the repo, unused.

<!-- from line 671 -->
## 2026-10-15: PDF export for County review
- The County web filter blocks willycraig1.github.io ("Computers / Internet"). As a stopgap for review before Friday,
  `tools/export_pdf.py` serves the repo locally, drives headless Chrome over the DevTools protocol, and captures
  every slide at 1920 x 1080 (x1.3): map and plan slides one page per step (site, paddocks, barnyard, Bud Box, barnyard on
  the site, water, Red House), the Red House program key per Level, the rest at their last step. 49 pages, about
  12.8 MB, written to exports/stakeholder-review-draft.pdf (git-ignored; rerun after changes).

<!-- from line 848 -->
## 2026-10-19: vision-first restructure, part 1
- New running order (index.html, 15 slides): cover, The vision (new `slides/vision.html`: the Level 3 picture in four
  points, the Option B watercolour, McIntosh Ag Center and Siesta Key Chapel comparatives, credited), drivers, the site
  today (2 steps), existing buildings, the campus at Level 3 (2 steps, fit checks hidden), the barnyard (Level 3 with
  its flow, then back to Levels 2 and 1, short items, no NEW badges), Bud Box, cow & calf pens and small animal pens
  (Level 3 row first), Red House, Levels table, paddocks, water quality, over to you. Out of the order, kept for the
  report: three-levels, program, pasture-capacity, water-site. Eyebrows renamed (no "Act" numbers).
- Images: photos/reference/ (1400px copies) and photos/vision-watercolor.jpg (from Watercolor_Rendering_Working).
- Still to do: a full review pass (the rest of part 1's list is done in part 2, 2026-10-20, below).

<!-- from line 858 -->
## 2026-10-19: barnyard slide fix; slide script check
- The barnyard slide came up blank: in the restructure, a comment inserted mid-line commented out the rest of the
  line, a syntax error that stopped the slide's script (not the 3D model work). Fixed.
- `tools/check_slides.py` syntax-checks the inline scripts of every slide and index.html with Node; run it after
  editing slides or rebuilding data.

<!-- from line 947 -->
## 2026-10-20: vision-first restructure, part 2; the 3D model closes the deck
- `index.html`: the massing viewer (`massing/index.html`) is slide 16, "The campus in 3D", after Over to you. It runs
  live in the deck's iframe; it has no build steps, so the deck's ‹ › buttons (and a clicker's PageDown / PageUp) change
  slides, while the arrow keys stay with the viewer for walking. F, Escape, Home, and End go to the deck. The PDF export
  skips it (it only takes `slides/` entries).
- Owner: the bonus pasture stays in the model as context (its paddocks and fencing at Level 3), though the slides show
  the main parcel only.
- Levels table, Level 3 first: `levels.html` shows the columns 3, 2, 1 and builds them in that order. `levels.js` stays
  written up from Level 1; the slide resolves each "Same as Level n", then a cell matching the one to its left reads
  "Same as Level 3 / 2". Where a Level 3 cell is only an add-on, its new `whole` text leads instead (cow & calf pens,
  swine & small animals, Red House): drafted wording, for the owner to check.
- Paddocks, rotation first: step 1 is the nine paddocks in rotation (Levels 2 and 3, about 15 CE, the highlight
  stepping through them), step 2 back to Level 1's conservative grazing (about 7 CE).
- Red House from Level 3 back: the steps run the house today (owner, 2026-10-20: existing first), then Level 3, 2, 1, with the list in that order and the
  plan's framing following; the static page (PDF) shows Level 3. Level 2 and 1 text reworded to read walking back
  (figures unchanged). The viewer's first preset is now "House + addition".

<!-- from line 1106 -->
## 2026-10-20: cover watercolour, "Leading a heifer"
- Title slide: the architect's new watercolour (`exports/Leading a heifer watercolor.png` →
  `photos/cover-heifer-watercolor.webp`) replaces `cover-watercolor.webp` (removed). The painting is 16:9 with its
  subject left of centre, so it is shown whole on the right (1060 px wide), multiplied into the paper with its edges
  feathered, and the text column narrows to 760 px (title on three lines).
- Residence front porch (owner, 2026-10-21): the porch's back wall is a full-width sliding glass door between the end walls (four panels, head at 10.5' with the window and transom heads), replacing the door and window.
- "The shade house" view is now the owner's framing (2026-10-21): from above the south pond, the residence's porch end at left and the shade house running away to the right (camera -3, -538, 21 to 122, -506, 8; 27 deg vertical).
- Service lane east of the arena (owner, 2026-10-21): grass over a drivable base, as on the site plan, not concrete (`scene.py` ground, `grass2`); the bedding storage pad at its north end stays concrete.
- "Poultry barn" view (owner, 2026-10-21): the unfinished barn close in from the west, above the walk that leads to its aisle (camera 455, -262, 20 to 534, -280, 6; 45 deg).
- Bonus pasture acreage labels removed from the viewer (owner, 2026-10-21); its paddocks and fencing still show at Level 3, and the site pasture keeps its labels.

<!-- from line 1117 -->
## 2026-10-20: campus watercolour slide
- New `slides/campus-watercolor.html` ("The campus"), slide 15 of 17, just before Over to you: the architect's aerial
  watercolour (`exports/Watercolor Campus with Tractor Outside Cattle Pen.png` → `photos/campus-watercolor.webp`)
  alone, full height and centred, multiplied into the paper with feathered edges as on the cover. No text. The PDF
  export picks it up as a one-page slide.

<!-- from line 1123 -->
## 2026-10-20: vision slide, campus at Level 3 watercolour
- `slides/vision.html` hero: the architect's "Watercolor Campus Level3" (`exports/Watercolor Campus Level3.png` →
  `photos/vision-campus-level3.webp`) replaces `photos/vision-watercolor.jpg` (removed); label "The campus at Level 3"
  (was "The barnyard at Level 3"). Same crop (object-position centre 62%).

<!-- from line 1128 -->
## 2026-10-21: the site today, drawing step and callouts
- `slides/site.html`: three steps now. From the air (aerial, full site); "The site, drawn" (new: the aerial off, our
  base drawing at the same full-site framing, names and entry arrow hidden); the campus close-up.
- Campus names are callouts: 15 px names set out in clear ground on leaders to their buildings (dot on the building),
  counter-scaled with the zoom as one group so size and offset hold on screen. ENTRY arrow and text smaller.
  "Hog pens" added on the long open-sided shed west of the cattle pens (about 26' x 60' on the drawing, matching the
  hog enclosure photo). "Kennels" added on the small building south of the Red House (architect). The
  names are drawn on top of the map, outside the campus layer, which is clipped at the main parcel line just past the
  kennels. Leaders run from the centre of each building (a white dot with a red ring, so it shows on the red
  fill); checked in the browser that each dot lands on its own shape and no name overlaps another name or a building.
- What is already built (`existing.html`): names match the site slide's callouts ("Cattle pens", "Hog pens",
  "Unfinished barn", singular); "timber" is now "wood-framed" (architect: no heavy timber on site). Every caption is
  sized to the tallest (set in the page after fonts load), so the photos line up across both rows. The Red House
  porches are no longer "wraparound" (they are segmented), here and on the Red House slide.
- Vision slide: a sticky note beside the title, from the first step: "Level 3 is the full build-out. The plan starts
  here, so each earlier Level grows toward it as funding and demand allow." (Styled after the old Cow Pen Slough note.)
- Running order: Paddocks and rotation moves up to slide 7, right after The campus (same full-site map; pasture is the
  first design driver), eyebrow "The plan" (was "Getting there"). The campus slide's first step now names them:
  "nine paddocks, about 45 acres of pasture" (acres from pasture-capacity.js). Levels table is now slide 13.
- Paddocks rotation animation: the two pinwheels turn together, one paddock a tick clockwise around their Feed + water
  hubs (west 3.9 → 3.3 → 5.2 → 2 ac; east 4.8 → 12.4 → 7.8 → 3.7 ac). The 2.1 ac paddock lights with its nearest
  pinwheel paddock, the 3.7 ac (architect, 2026-10-21). Groups and order are found from the drawing's `#pinwheel-labels` hubs (a hub's four nearest site paddocks,
  all within 300 units, sorted by angle), so they follow the drawing if it changes.
- Paddocks back to Level 1 first (architect, 2026-10-21: "this one doesn't make sense going backwards"): step 1
  "Nine site paddocks" (Level 1, about 7 CE), step 2 "Rotate through them" (Levels 2 and 3, about 15 CE) with the
  rotation, which restarts from each pinwheel's first paddock (12.4 ac and 3.3 ac) every time it begins.

<!-- from line 1155 -->
## 2026-10-21: How the plan took shape (`slides/plan-logic.html`)
- New slide 8, before the barnyard by Level (architect's design narrative): the Level 3 barnyard built up one design
  move at a time on the site plan, framed tight on the central campus. Six steps, the current move at full strength and
  the earlier ones faded: (1) the existing barn sets the grid (perpendicular to Cowpen Slough, parallel to the entry drive; a
  12' grid square to the barn, and the barn's axis dashed up to the unfinished barn, which falls on it); (2) cattle
  builds off the existing pens; (3) parking central to the new barns and the Red House; (4) small animal barns complete
  the parking's shape, horticulture frames the south edge of the drive loop, the residence completes the central
  campus; (5) arena, grooming, and feed storage central for vehicle access and daily use; (6) the classroom extends
  east into the tree canopy.
- The grid and frame are measured from the drawing's own elements (`#barnyard .by[data-id]`, the existing barn's
  rect for the orientation), so they follow the plan if it changes. Labels are matched to moves by their text.
- PDF export: one page per step (`STEPPED`).
- Architect's edits (same day): no pasture fencing (`#paddocks`) on this slide; Cowpen Slough, not SR-72 (the road
  is at the property's north end); cattle "immediately adjacent to the pasture"; parking avoids most existing trees and
  gives vehicles loading and unloading access to all these structures; the working center has central dumpster access.

<!-- from line 1171 -->
## 2026-10-21: PDF backup; picture blow-up on the vision slide
- PDF backup exported from main at 33973fb: 38 pages, 10.0 MB (`exports/stakeholder-review-draft.pdf`, git-ignored; a
  dated copy in the main checkout's `exports/stakeholder-review-2026-10-21.pdf`). `tools/export_pdf.py` needs
  `websocket-client`, now in `tools/requirements.txt`.
- Vision slide: click the watercolour or any reference photo for it full screen, with its caption and credit (the
  watercolour reads "Potential conceptual rendering", the owner's phrase). ← → step through them; Escape or a click
  closes. While open, keys and clicks go to it, and the deck's ‹ › buttons close it rather than change step: that
  message guard is registered before deck.js, since messages reach a window's listeners in the order they were added.
  Never shown in the static / PDF page.

<!-- from line 1181 -->
## 2026-10-21: final edits before the meeting
- Title slide: "Draft, for discussion" removed from the meta row.
- Barnyard slide, small animal barn dimensions (`build_ag_area.py`): the string over the barns had been left on the
  side-by-side layout (36' / 36' / 24', 26' off and measuring a gap to a barn no longer there). Now taken from the barns
  as drawn: across the north end, turnout 36' and barn 36'; down the west side, barn A's wings 48' and 48' either side
  of the 12' dogtrot, then barn B 48'. Only `dims` and the drawing's `view` changed in `ag-area.js` (elements
  identical); the site map does not read either, so it needs no rebuild. Like the cattle string, the dimensions show at
  every Level.
