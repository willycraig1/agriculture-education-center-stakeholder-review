# 3D massing model

Moved verbatim from the original NOTES.md. `<!-- from line n -->` marks where each entry stood.

<!-- from line 678 -->
## 2026-10-16: 3D massing viewer (`massing/`)
- `massing/index.html`: three.js viewer of the campus, published as a private claude.ai artifact. Geometry comes from
  the watercolour's `Watercolor_Rendering_Working/scripts/scene.py` (barnyard massing, fitted to the barnyard diagram
  within 0.6 ft) via `massing/export_scene.py`, and from the deck's site plan via `massing/export_site.py`. Rerun both
  after changes to scene.py or the deck's build tools.
- Owner direction: small animal barns A and B and the dogtrot sit under one continuous roof; trees under the parking
  lot and swale stay (three surveyed trees stand in the paving as drawn: a conflict to resolve); woods are oak
  hammock with sabal palms, pines mostly in the north triangle pasture (between SR 72 and Cowpen Slough).
- Water features (slough, ponds) are cut as basins: drawn outline = top of bank, water 3' below (placeholder).
  SR 72 sits on fill at its surveyed average, 4.3' above the adjacent grade (24.23' vs 19.91'), 2:1 shoulders.
- `tools/read_survey_spots.py` reads the survey's spot elevations (stroked CAD glyphs, matched to the templates in
  `tools/survey_glyphs/`) into `drawings/data/survey-spots.json`: 930 of 1,265.
- **Pinned (owner, 2026-10-16):** no accurate terrain model for now; the ground stays flat apart from the water basins
  and the road fill. The spot elevations are there if it is picked up later.
- The civil narrative of 2026-10-16 (`source/civil/0_County4H_Narrative1withExhibits...`) is a draft study: not to be
  incorporated until the owner's team has discussed it. Not committed.

<!-- from line 731 -->
## 2026-10-19: barn-kit system for the new barns (massing)
- Reference: `source/Clark Farm Study Plan-A2.0 Arena and SmAnimal Barn Reference.pdf` (McIntosh Ag Center covered
  pavilion, 96' x 50' clear span, 8 bays, 4:12, ~14' to the joists; Bldg 18 small animal barn, 34' wide, 12 bays,
  4:12, ~12' to the joists, clad gable ends with exhaust fans, roll-up clear curtains over livestock panels). Same
  pre-engineered system as the cattle barn reference: 8x8 wood columns, steel bar joists, 2x roof framing, metal panels.
- Owner direction for ours: 3' overhangs on every new barn; bar joists 18" deep following the roof, painted black;
  a ~6" roof plane (2x6 framing, metal panels, trim) on the joists; exterior walls thick enough not to see through.
  Arena one bay shorter than the reference (84' x 50', unchanged in the plans). Small animal barns 36' o.c. (on the
  12' module), no tack rooms, the wings' dividing walls on their column lines at the dogtrot, curtains and
  ventilation, no A/C.
- `scene.py`: kit helpers (`slab`, `thick_wall`, `bar_joist`, `kit_gable`); cattle barns, arena, and small animal
  barns rebuilt on them. Small animal barns: 6' x 10' pens either side of the 16' aisle, concrete floor, exhaust fan
  in each gable, clear curtains (drawn translucent in the viewer).

<!-- from line 864 -->
## 2026-10-19: Red House massing (from photos)
- `massing/index.html` `redHouse()`: built on the surveyed outline from `photos/Red House` (24 site photos and a roof
  aerial). Main block ~41' x 66' on a crawlspace (floor ~2.5' up, 8' walls), red-stained board siding, a 3.5:12
  galvanized metal gable along its length (ridge ~16.5'); the north-west porch (44' x 12', wood railing, steps) under a
  1.5:12 extension of the main roof; a screened porch across the north-east end (8.4', solid kneewall); the
  south-west wing (~43' x 34') under its own 3:12 gable (ridge ~16'); a stone chimney on the south-east side; windows in
  white frames. The carport: an open wood-post shed with a 4:12 gable and exposed trusses. Heights and pitches
  estimated from the photos; the Level 3 event space addition is not modelled yet.

<!-- from line 980 -->
## 2026-10-20: Red House teaching space in the massing (`massing/index.html` `teachingSpace()`)
- Owner's brief: conceptually the Siesta Key Chapel, built on the barns' kit system. 72' x 36' on the 12' grid (six
  bays, 8x8 wood columns, bar joists spanning the 36' with no interior columns). Same centre as the study plan's
  addition (`red-house-addition`), but turned square to the existing barn and the barnyard instead of true north (a
  departure from the site plan drawings, which still show the A0.1 placement; the plan has not been updated).
- Section: floor 5.5' above grade; crawlspace closed with wood louvers on the column lines, the floor framing drawn as
  a band outside the columns; 10' from the floor to the bearing of 18" bar joists (black) that follow the 4:12 roof;
  galvalume roof, wood underside (reads as wood between the joists), 3' overhangs all round.
- Envelope: side walls glass floor to eave, mullions at the columns and mid-bay (6' module). The end bays are solid
  weathered wood: the west bay is the restroom and storage core (its inner wall one bay in, open in the middle third),
  the east bay solid. East endwall: solid centre third, glass in the outer thirds up to the joists' bottom chord.
  West endwall: solid, entry doors at its centre. East balcony deck 12' out at floor level, on posts, wood railing.
- Access: the grade rises behind the house (owner), so the model fakes it: the walk (plan walk-3 carried on to a
  landing at the new door) climbs from grade at the house to floor level at the door, about 40' at 1:7, with the
  ground banked at about 1:2 around it. Not an accessible slope; the real topo will set it. A surveyed tree stands in
  the walk (as on the plan).
- Data: `massing/export_site.py` writes `campus.addition` (centre, axis, size, walk outline, walk ends). Viewer presets
  "Teaching space" and "Inside the classroom". Level 3, education colour.
- Owner's revisions (same day): the whole building moved 5' east (about 12.9' clear from its floor band to the corner
  of the Red House's north-east porch; the walk's link to the landing lengthens with it); the crawlspace louvers carried
  round under the balcony, in the same planes as the main skirt (the column lines) and on the balcony posts; the balcony railing is posts and rails with square welded wire mesh (about 4") that all but
  disappears, no pickets; siding horizontal on the side walls (solid bays and the frieze), vertical on the endwalls.

<!-- from line 1003 -->
## 2026-10-20: palms framing the parking (massing)
- Owner: a line of sabal palms on the parking's north and west sides. Twelve down the 8' strip between the grass
  parking and the concrete lane south of the arena, on the arena's 12' column grid (trunks in line with its columns;
  the end palms pulled in to 172 and 300 to stay in the strip), six in the grass west of the lot's west leg (about
  19.4' apart, from the lane south toward the surveyed oak). Placed by `massing/export_site.py` (`campus.palms`, scene
  feet, read off the owner's markup); Level 1 with the parking.
- That strip was asphalt in `scene.py` (the watercolor's ground); it is now grass, so a re-rendered watercolor shows it
  green too.
- Follow-up: the planted palms are drawn at half the woods' sabal height (kind `cabbage` in the viewer's `treeSet`).
  The north strip had only looked grey because the browser kept the old `scene-data.js`; both exporters now stamp
  the viewer's data script tags with a content hash (`?v=`), so a reload always picks up new data. The watercolor's
  west parking drive (`scene.py`) ran on south past the lot into the south-west pasture; it now stops at the end of
  the lot's west leg (y -455).

<!-- from line 1017 -->
## 2026-10-20: Red House roof corrected (massing)
- The north-east end is a cross gable, not the end of the main gable (roof aerial; photos 7, 9, 13, 19 in
  `photos/Red House`): about 41' square from the screened porch's outer wall (u -8.4) to the chimney's north-east side
  (u 32.9), its ridge across the house at the main ridge's height (pitch about 3.5:12), gable ends on the north-west
  and south-east faces, the screened porch under its north-east eave. The main ridge runs into it in a T; valleys run
  from the T down to the corners at the chimney line. The u extent is read from the photos (the chimney stands just
  south-west of the south-east gable end); the aerial is too oblique to scale.
- South-east wall windows: the wall line had been taken from the outline's widest point, which is the chimney's
  bump (v 43.6), so the windows stood 2.7' off the wall; it is now the wall itself (v 40.8).
- The north-west porch's roof now stops at its last column (u 33.6) instead of running on to the north-east end.
- Follow-up (owner): south-west of the cross gable the house is one roof shape to the wing's far end: the main gable,
  its north-west slope carried on at 1.5:12 (the porch's pitch) over the porch and the wing, and its south-east slope
  stepping in with the wall at the wing (v 30.5), so the eave there is higher (about 13.6'). The wing's own lower gable
  is gone. Walls south-west of the cross gable run up to the roof (split where its pitch changes), so the wing's
  north-west wall is low under the porch roof; its two windows there are shorter and lower to fit. Crawlspace skirts
  now run round under both porches.
- Follow-up (owner): the whole roof raised 1.5' (plate 12.0' above grade, was 10.5'; 9.5' walls on the 2.5' floor;
  ridge about 18'). The higher eave over the wing's south-east wall is now about 14.6'; the wing's north-west wall
  stands about 10.5' under the porch roof, so its windows are back to the standard size.
- Follow-up (owner): the arched-top window in the cross gable's north-west end, behind the oak (photo 15; 3' wide,
  round head, about 9.5' from the screened porch's wall); the north-west porch's railing now opens at the steps (newels
  either side) and returns across the porch's open north-east end.

<!-- from line 1040 -->
## 2026-10-20: residence and horticulture shade structure (massing)
- From the owner's sketch (shed-roof residence at the end of the strip, shade structure over it) and a photo of their
  current shade house (galvanized pipe frame, black shade cloth). `horticultureArea()` in `massing/index.html`, on a
  small shared builder (`localKit`) in each plan rectangle's own axes.
- Residence (Level 3, on the plan's 20' x 30' footprint): one 3:12 shed roof rising to the north-north-east (sidewalk
  side), where the tall wall has a clerestory band over a lower 1.5:12 awning (6' deep, corner posts) sheltering a
  glazed wall and the entry door; an 8' porch open under the roof's low end on the south-south-west; floor 1.5' up;
  vertical weathered-wood boards; galvalume. Heights are assumed (low eave 10', high wall about 17.6').
- Shade structure (Level 3) over the whole 100' x 30' strip: pipe posts on about a 12.5' x 15' grid, rails both ways,
  black shade cloth at 10'. Rows under it along the strip: hydroponic channel racks (north-north-east, Level 3), raised
  beds 4' x 10' (middle, Level 1), planting tables 4' x 8' with flats (south-south-west, Level 3). Only the shade
  structure is labelled. Row widths and counts are my layout, not from the sketch.
- Follow-up (owner): the strip's ground is black weed fabric (was the program tint); the far bay's south half is cut
  out around the surveyed oak standing there (ground, frame, cloth, beds and tables stop short of it). Residence raised
  2' for the flood zone (floor 3.5', roofs with it: low eave 12', high wall about 19.6'); its end walls now run out
  under the roofs to close the sides of both porches (front porch under the main roof, back porch under the north
  awning, which now has a deck); porch columns on both porches stand on the clerestory's four mullion lines, and the
  glazed wall's mullions are on those lines and halfway between, the door in the last bay; steps down from both
  porches; the crawlspace skirt runs under both.
- Follow-up (owner): residence steps removed (not designed yet); the end walls are 1' thick, like the north wall's
  returns, and replace the outer porch columns, leaving columns on the clerestory's two inner mullion lines.
- Follow-up (owner): the horticulture strip sits on a pad 6" up (timber edging, weed fabric on top), so the shade
  frame's rails at 10' above it meet the residence's window and transom heads (10.5'). The residence's door moved to
  the west bay of the glazed north wall; its siding runs down to the ground (no dark plinth), the crawlspace skirt
  and porch decks sitting between the end walls.
- Follow-up (owner): both residence porches screened in between the end walls, screen on a 5" rail through the column line.

<!-- from line 1067 -->
## 2026-10-20: pasture fence through the holding pens (massing)
- The site plan's pasture fence east of the barnyard (fence-07) runs a few degrees askew from the existing pens' corner
  north through the east column of holding pens (about x 414 to 424 against the pens' east line at 426.6), so the
  model drew a wire fence through that column of pens. `export_site.py` now cuts every pasture fence out of
  the holding pens' footprint (each pen's four side objects grouped, buffered 1.5'). The site plan itself
  (`build_fences.py` / `site-layers.svg`) still carries the askew line.
- Site plan fixed at the source (owner): the campus fence (fence-07, redrawn in `build_site_map.py`) still jogged
  back from the lean-to corner column to the existing pens' north-east corner (13' west) and then ran diagonally to
  the holding pens' north-east corner. With the holding pens out to that column line (the dog-ear), it now runs
  straight up it. One paddock beside the campus 7.9 -> 7.8 ac; fenced site pasture 45.3 -> 45.2 ac; CE unchanged
  (7 / 15). Rebuilt: build_site_map, build_capacity_data, build_retention_markup, massing/export_site, stamp.

<!-- from line 1079 -->
## 2026-10-20: grooming area (massing)
- Owner: the grooming area is not a building, just an open space with panels to tie animals to while they are hosed
  down and blown out. `scene.py`: the white box inside the arena's west end is replaced by its own `grooming` object
  (Level 2): a concrete wash pad (about 11' x 43'), four short pipe tie panels out from the west column line (no
  rail along the line: owner). The arena rail now closes its west side too, between the arena floor and the grooming area.
  `export_scene.py` no longer splits the grooming faces out of the arena object.
- Tractor (owner): moved off the holding pens' fence (the painting's spot, `render.py` TRACTOR_AT, kept for the
  watercolor) into the 3.7 ac paddock north of the barnyard, facing west, at least 25' from fences and panels, pulling a
  manure spreader with a load on.

<!-- from line 1089 -->
## 2026-10-20: viewer views (massing)
- Owner: the Watercolor view no longer matches the model, so it is removed with its overlay slider (and the model
  description no longer calls itself "the massing behind the watercolor"); the viewer opens on Bird's-eye.
- Views are now grouped: overviews (Bird's-eye, Plan, Campus, Over the pens, Teaching space, Site pasture, Whole
  property), then eye-level shots chosen to explain the concept: Arriving (palms and arena from the parking, was "Eye
  level"), Leading a steer (a student and steer at cattle barn B), Between barns, From the pasture, The classroom (the
  glass wall from the lawn, Red House beside it), Inside the classroom, The shade house (along the beds to the
  residence). `window.massing` (camera, controls, setView) is the console hook used to frame them.
- Stills from the viewer: `python tools/export_massing_view.py [view] [--size 4800x2000] [--labels] [--level 3]`
  screenshots `tools/massing-shot.html` (the viewer without its control rail, from a named camera) with headless
  Chrome to `exports/massing-<view>.png`. First view: `over-the-pens-wide`, "Over the pens" pulled back to 2.4:1 to
  take in the unfinished (poultry) barn and the classroom building. Second: `leading-a-steer` (16:9; the camera moved
  10' west, out of the feed storage container it stood in, and the viewer preset with it).
- Cattle barns (owner): the monitor's clerestory sidewalls are open, louvered at most (not clad). `scene.py` draws them
  as horizontal louver blades (0.4' deep, about 0.55' apart, sloping down and out) from the shed roofs up to the
  monitor roof, in weathered wood (owner, 2026-10-21; they had followed the red cladding). Gable ends stay clad.
