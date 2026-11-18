# Print sheets and fact sheet

Moved verbatim from the original NOTES.md. `<!-- from line n -->` marks where each entry stood.

<!-- from line 790 -->
## 2026-10-19: project fact sheet (`factsheet/`)
- Two-page letter fact sheet, front and back. First drafted after the County's own sheet
  (`source/Clark Farm Project-Fact Sheet-PRINT 10-15-26.pdf`); restyled the same day to the presentation's language
  (architect): deck serif and sans, eyebrows, Level badges, palette colours, and the design-driver icons. No
  "Clark Farm" anywhere on the sheet. No County or UF/IFAS logos.
- Front: the Option B watercolour, an At a Glance grid (six figures, each with an icon in the deck's style: parcel,
  herd, cattle pens, small animal pens, classroom, Levels), the project and thesis, and the four design drivers.
  Back: site plan of the main parcel (drawn live from `slides/data/site-map.js`, Level 3 colours) with a barnyard
  close-up, the three Levels table, and the program. Figures follow `levels.js`, `ag-area.js`, and `pasture-capacity.js`;
  floodplain compensation and the bonus pasture are left out, as in the deck.
- Main parcel area on the sheet is the Property Appraiser's published 60.83 ac (architect), not a measured figure.
- Print: `python tools/export_factsheet.py` → `exports/agriculture-education-center-fact-sheet.pdf` (git-ignored).

<!-- from line 816 -->
## 2026-10-19: Level 3 classroom on the site plans; fact sheet legend and close-up fences
- Red House Level 3's instructional classroom / event building (51' x 31' with restrooms and storage, about
  2,200 sf with walls) is now an element of the barnyard plan (`build_ag_area.py`, id `red-house-classroom`, Level 3,
  education), so it appears on the barnyard diagram, on the site map's barnyard layer (fading in at Level 3 on the
  site-plan slide), in the massing site data, and on the fact sheet. Placed by fitting the Red House study sheet to
  the architect's outline of the house: the house footprint on the Level 3 sheet (porches left out) against the
  outline, scale fixed by the two drawings, rotation and offset fitted. Fit: 51.2 deg (the sheet's north lands
  exactly at the plans' north-left), 542 sf mismatch on a 4,000 sf house. The building lands east of the house
  across the patio, as on the sheet. Site map label "Classroom / event".
- Fact sheet: FEMA flood zone line added to the site plan legend; in the barnyard close-up the pasture fences are
  drawn at 0.8 with 4.5 / 2.5 dashes (casing 2) instead of the full plan's 2 with 14 / 6, since the close-up is at
  about twice the scale.

<!-- from line 829 -->
## 2026-10-20: fact sheet, owner's comments (`source/agriculture-education-center-fact-sheet _LHB.pdf`, kept local)
- Carried over the architect's Illustrator edits to the export: the aerial watercolour (`exports/Watercolor Campus
  with Tractor Outside Cattle Pen.png` → `factsheet/rendering.jpg`), "60.8 ACRES / Property", the thesis box removed,
  and the back heading "The barnyard grows from the existing barns".
- Owner's edits: no "Project fact sheet" in the heads; "Sarasota County, Florida"; rendering caption "Potential
  conceptual rendering of …"; "(CE)"; pens "as funding allows"; project paragraphs and driver wording rewritten; back
  label "The conceptual site plan", caption "Conceptual site plan for the 60.83-acre parcel."; program lines trimmed.
- Back page restructured on her suggestion: the Levels table is gone; the site plan runs full width and the barnyard
  close-up sits beside a "Potential infrastructure and features" list (her 12 items). The plan drops the paddock
  fences, acreage tags, Feed + water labels, FEMA flood zone line, and the slough bed label ("for this version").
  Close-up badge "Barnyard, full build-out" (readers don't know the Levels yet). Kept: the "3 Levels" tile.
- Our readings where her marks were ambiguous: "a conference room for 20 to 25"; the second project paragraph as
  "It serves two programs, 4-H youth and adult beginning ranchers, with infrastructure for cattle, swine, sheep,
  goats, poultry, and horticulture. It also provides … for the agriculture industry and the public …".
- Follow-up (architect): no campus labels on the full-width plan (too small to read). The barnyard close-up is now
  square (2.75") and closer in (196 site units across, framed on the barnyard, Red House, and classroom building),
  with its badge allowed over the drive. Its labels are placed by the fact sheet itself at the centre of each
  building's shape (or group: "Small animal barns" for barns A and B, "Holding pens" for pens 1 to 5), with
  "Classroom / event" on two lines on its building.
<!-- from line 923 -->
## 2026-10-20: Arch D site plan sheets
- `tools/export_sheets.py` prints `tools/sheet.html` with headless Chrome to 36" x 24" vector PDFs in `exports/`:
  AS-0, the existing site on the full-colour aerial at 1" = 100'; AS-1, the main property at Level 3, 1" = 100';
  AS-2, the campus at Level 3, 1" = 40'. `--date` sets the sheet date; name sheets (existing, site, campus) to print
  only those. Title strip: north arrow, scale and graphic scale, legend, notes, project, sheet title, firm.
- AS-0 follows the site slide's campus step: property lines, water and the FEMA line, surveyed trees, existing
  buildings and drive, Cowpen Slough; nothing proposed. The County aerial is about 30 px per inch at this scale, so it
  prints soft; a higher-resolution aerial would drop straight in.
- The architect's Illustrator edits to the first AS-1 / AS-2 (main project `exports/`) are folded into the template:
  project name "Agriculture Education Center", AS numbering, "Site plan: overall", the firm name in the title block,
  labels Red House, Addition, and Entry Gate (read back to plan units), and the slough-bed label moved off the fence on AS-1.
- The slide's screen-sized labels (`data-fixed`) and line weights (`data-w`) keep one printed size on every sheet
  (labels at 0.4 of their slide size at 1" = 100'). The frame is kept on the parcel, so AS-2 runs to the parcel line.
- Scale checked in the PDFs: existing barn 80.4', cattle barns 84' x 64'. Rerun after `build_site_map.py`.

<!-- from line 938 -->
## 2026-10-20: sheet A-1, Red House Levels
- `tools/export_red_house_sheet.py` prints `tools/red-house-sheet.html` to `exports/red-house-A-1.pdf` (Arch D,
  vector) and saves its SVG (`red-house-A-1.svg`), whose top-level groups open in Illustrator as layers: Program
  colors (one group per Level, under the plans), Plans, Room names, Plan titles, Titleblock.
- 1/16" = 1'-0". Plans turned 90 deg counter-clockwise (read with the sheet's right edge as the bottom), Level 3 on
  the left, Level 1 on the right, equal gaps. All three placed on Level 1's box (the Levels share one plan frame), so
  the house lines up across the sheet; Level 3's addition runs past the shared edge.
- The architect cleans up unfilled program-colour corners in Illustrator; those edits do not flow back into the data.

<!-- from line 964 -->
## 2026-10-20: fact sheet branch merged with main
- Main had added the same Level 3 building independently as `red-house-addition`, placed from study plan A0.1
  (owner, 2026-10-20). Main's placement is kept; this branch's fitted `red-house-classroom` (fit to the Red House
  sheet) is dropped. The site map's "Classroom / event" label and the fact sheet close-up now point at
  `red-house-addition`.
- Generated files taken from main and rebuilt with the parcel fix (build_canopy, build_ag_area, build_site_map,
  build_retention_markup, build_site_map, massing/export_site, stamp). ag-area.js rebuilds identical to main's.
  The Arch D site plan sheets (exports/, not tracked) predate the parcel fix; re-export them for 61.3 ac.
