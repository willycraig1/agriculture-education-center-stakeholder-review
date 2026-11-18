# Stormwater concept, November 2026 (decision history; current state is in docs/reference/)

Moved verbatim from the original NOTES.md. `<!-- from line n -->` marks where each entry stood.

<!-- from line 1250 -->
## 2026-11-18: owner's stormwater direction on the site plan sheets (AS-1, AS-2)
Direction (via the architect): raise the holding pens, new barns, turnout yards, and working spaces to BFE + 1'; open the
retention pond into the historical slough bed (native predators for mosquito control, migratory bird habitat); expand the
bed with wide radii, leaving about 30% of the open pasture just above the BFE; connect under the road to a similar swale in
the north triangle pasture; add high-ground paths to the gates across the swale centerlines, on culverts.
- `tools/build_stormwater_concept.py` -> `drawings/data/stormwater-concept.js`, drawn by `tools/sheet.html` on AS-1 and AS-2
  only. The deck's slides and `site-map.js` are unchanged. `?stormwater=0` prints the sheets as they stood before.
- BFE +21.70', the modelled 100-year elevation (architect, 2026-11-18). Raised pad +22.70'. Civil's earlier 21.70' covered
  building floor now sits a foot below the pad. High ground +22.00' and swale average +18.50' are planning assumptions.
- Result: 20.2 ac of open pasture, 13.6 ac (67%) swale and 6.6 ac (33%) high ground. Pad 1.6 ac (2.0 ac with slopes). Three
  paths (A and B in the main pasture, C in the triangle), three path culverts, the road culvert (about 86 ft), and the entry
  culvert replaced. The swale takes about 1.9 ac of ragged woods edge so its banks can hold their radii.
- Earthwork from survey spots, rough: cut 37,800 cy, fill 29,400 cy, net cut 8,500 cy. Storage below the BFE: 22,900 cy lost,
  36,500 cy gained. About 35% of the swale has no survey spots (north triangle), so +19.9' is assumed there.
- For civil: confirm grades, culvert sizes, compensation, and permitting. Pasture capacity has not been rechecked.

## 2026-11-18: stormwater sheets, architect's review
- Path B rerouted off the fence line: from the road gate it crosses the swale centerline once, then curves past the wooded
  island in the 3.7 ac paddock to the hub gate (about 318 ft). Path A is unchanged. The route is my reading of "rerouted".
- The swale and pond are now one graded surface with 1' contours. Assumed for civil to confirm: NWL 18.00', littoral shelf
  17.50', pond bottom 12.00', swale banks 12:1, pond banks 4:1. The swale floor falls to the pond and works as its shelf.
- Pond limits (north is left on the sheets, so east is up and south is right): the east side holds the designed edge, and the
  south top of bank holds 10' off the fence. A pipe through that strip keeps the connection to the existing outfall.
- Earthwork, rough: cut 31,200 cy; fill 37,300 cy (basin banks 7,500, pad 9,500, high ground 20,300); about 6,000 cy imported.
  Floodplain storage above the NWL and below the BFE: 23,200 cy lost, 24,400 cy gained.

## 2026-11-18: stormwater sheets, architect's markup of AS-2
- Path A is cut straight on the centerline between the two cattle barns (x = 74 in the barnyard grid), hub gate to pad edge,
  about 322 ft. Path B now joins the high ground in the middle of the 4.8 ac paddock to that paddock's corner gate, about 210 ft.
  The gate between the pastures is no longer a path destination.
- Paths and the pad are drawn as the same ground plane as the high ground. Only contours and culverts show them.
- Pad outline is one clean L in the barnyard's grid: the notch west of cattle barn B and the angle north of Pen 5 are gone, and
  the handling yard is on the pad. Pad 1.9 ac (2.3 ac with slopes). One surveyed tree falls on the pad's slope, just east of
  Pen 1.
- Earthwork, rough: cut 31,400 cy; fill 38,400 cy (basin banks 7,500, pad 10,800, high ground 20,100); about 7,100 cy imported.
  Floodplain storage above the NWL and below the BFE: 24,000 cy lost, 24,500 cy gained.

## 2026-11-18: stormwater sheets, architect's second markup of AS-2
- Surveyed trees are drawn over the grading, and the grading runs beneath them (the architect's call, realistic or not). They no
  longer hold rings of high ground in the swale.
- Top of bank turns on rounded corners wherever it meets a path. Narrow swale arms stop short of the path in a rounded end.
- Path A leaves the pad on a gentle ramp: 22.70' to 22.00' over 70 ft (1%), shown by contours running out along the path.
- Culverts run out to the swale invert on both sides: Path A 52 ft, Path B 143 ft, Path C 71 ft, road 99 ft, entry drive 29 ft,
  outfall link 67 ft. A low-flow invert is graded along every swale centerline so the narrow arms reach it.
- Open pasture 20.4 ac: 13.6 ac (67%) swale, 6.8 ac (33%) high ground.
- Earthwork, rough: cut 33,800 cy; fill 36,700 cy (basin banks 5,200, pad 10,800, high ground 20,700); about 2,800 cy imported.
  Floodplain storage above the NWL and below the BFE: 24,500 cy lost, 26,800 cy gained.

## 2026-11-18: stormwater sheets, architect's third markup of AS-2
- The swale arm along the road fence is carried north to Path B, which shortens the Path B culvert from 143 ft to 73 ft.
- The swale bottom is rerouted wide of cattle barn B along the architect's line. At that corner and north of Pen 5 the banks are
  eased and the ground falls evenly from top of bank to the swale bottom. The pad shows one continuous 22' contour.
- All culverts are straight: Path A 52 ft, Path B 73 ft, Path C 71 ft, road 99 ft, entry drive 27 ft, outfall link 65 ft.
- Earthwork, rough: cut 32,900 cy; fill 37,200 cy (basin banks 5,600, pad 10,800, high ground 20,800); about 4,200 cy imported.
  Floodplain storage above the NWL and below the BFE: 24,500 cy lost, 25,900 cy gained. Swale 67%, high ground 33%.

## 2026-11-18: stormwater sheets, north triangle (architect's markup of AS-1)
- Path C now runs on from the triangle hub along the slough-side fence to the gate at the triangle's south tip, about 1,081 ft
  in all, its centerline 20 ft off the fence.
- A small retention pond (about 0.1 ac, 105 ft x 56 ft) collects the north triangle swale. Assumed: NWL 18.50', bottom 14.00'.
- The old road culvert is replaced by the pond's outlet: one straight pipe, about 125 ft, under the road to the bend in the main
  swale. The swale invert at the bend is 18.30', so the outlet has only about 0.2 ft of fall. Civil to confirm.
- Earthwork, rough: cut 32,300 cy; fill 36,900 cy (basin banks 5,500, pad 10,800, high ground 20,600); about 4,600 cy imported.
  Floodplain storage above the water levels and below the BFE: 24,400 cy lost, 25,200 cy gained. Swale 67%, high ground 33%.

## 2026-11-18: stormwater sheets, drafting clean-up
- Contours stay at 1' intervals: the 22.25' line on the Path A ramp is removed, and the ramp reads from the 22' contour running out
  along the path. The pad edge (22.70') and the pond water levels (18.00' and 18.50') are still drawn as edges, not as contours.
- The fence offset label and its dimension tick are off the retention pond. The 10' hold itself is unchanged.
- Pasture gates are drawn at half their earlier line weight on AS-1 and AS-2.

## 2026-11-18: stormwater sheets, contour spacing
- The pad edge line (22.70') is removed. It was not a 1' contour and it broke at Path A. The pad now reads from one continuous 22'
  contour that runs out along the ramp.
- Top of bank is 22.00' all the way around the swales, so every 21' contour runs as a closed line inside it. Swale banks are never
  steeper than 5:1: the 21' line stays at least 4 ft off the 22' line (about 3 ft at the steepest pond banks, which are 4:1).
- Typical swale banks change from 12:1 to 8:1 to hold floodplain storage with the higher top of bank.
- Culverts: Path A 73 ft, Path B 93 ft, Path C 85 ft, pond outlet under the road 125 ft, entry drive 57 ft, outfall link 66 ft.
- Earthwork, rough: cut 31,700 cy; fill 41,200 cy (basin banks 9,900, pad 10,800, high ground 20,500); about 9,600 cy imported.
  Floodplain storage above the water levels and below the BFE: 24,300 cy lost, 24,600 cy gained. Swale 67%, high ground 33%.

## 2026-11-18: stormwater sheets, final figures after the contour spacing pass (supersedes the entry above where they differ)
- Typical swale banks are 7:1. The north triangle pond's assumed water level is 18.40', so the triangle's pasture floor stays above it
  and only the pond and its shelf hold water. The outlet falls about 0.3 ft to the swale invert at the bend.

## 2026-11-18: meandering low-flow channel, drawn as a separate option
The Ag Ed consultant asked whether the swale basin could wiggle at a 10' to 20' radius to lengthen the run and improve
treatment. The architect asked for it as a new option, with the existing plans left alone.
- `tools/build_meander_option.py` reads `stormwater-concept.js` and writes `drawings/data/stormwater-meander-option.js`.
  `tools/sheet.html` draws it only with `?option=meander`. The base sheets, figures, and 11-18-26 pricing do not change.
- Channel: 6' wide, 1' below normal water (inverts 17.00' main, 17.40' north triangle), 15' design radius. Bends swing 75
  degrees where the floor allows and 60 or 45 degrees where it is narrower. Straight runs at culverts, junctions, and pools.
- Result: about 3,990 ft of channel, 420 ft (12%) longer than a straight channel, with bends on about 1,530 ft. About 910 cy
  of cut. The first estimate of 25% assumed more usable floor than the narrow arms and hold-backs leave.
- Paths A, B, and C and the entry drive culverts would need lower inverts. All values are assumed until civil confirms them.
- Consultant's position: cattle manure in the channel is not a concern, because the cattle do not drink this water and it
  has enough time for treatment before leaving the property. No fencing or buffers are shown along the channel.
## 2026-11-18: meandering channel option, architect's review
Supersedes the figures in the entry above.
- The 3.9 ac paddock's channel now goes around the tree island, at least 29' clear of it.
- The channel follows the midpoint between the banks through the tight swales.
- Wider bends at the two spots the architect named: the 4.8 ac paddock and the floor just east of Path A. Those use a 20' radius,
  with straight legs between bends in the 4.8 ac paddock.
- Result: about 4,320 ft of channel, 620 ft (17%) longer than a straight channel, with bends on about 1,690 ft. About 940 cy of cut.
  The tightest radius is about 10', where bends fall on a curving stretch of the swale.
## 2026-11-18: meandering channel option, 7.8 ac paddock as sketched
Supersedes the figures in the entry above. The branch north of the Path A culvert now follows the architect's sketch: a wide S on
the lower floor, then north through the neck into the upper floor of the 7.8 ac paddock. The alignment is held in `DRAWN` in
`tools/build_meander_option.py`. Result: about 4,590 ft of channel, 770 ft (20%) longer than a straight channel, with about 1,010 cy of cut.