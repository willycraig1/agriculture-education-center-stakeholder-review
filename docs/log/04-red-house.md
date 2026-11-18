# Red House

Moved verbatim from the original NOTES.md. `<!-- from line n -->` marks where each entry stood.

<!-- from line 584 -->
## 2026-10-14: Red House porches
- The Red House's two porches are drawn on the site map as open canopies, like the carport (tinted, dashed outline):
  the porch along the north-west wall and the one across the north-east end, from the survey's overhang lines
  (BUILDING OH) closed against the house walls (BUILDING). About 520 sf and 340 sf. On every slide using the site map.
- Also on the barnyard diagram (`tools/build_ag_area.py`): the carport (from the survey overhang rectangle, as on the
  site map) and both porches, as context elements of kind `canopy`, drawn tinted with a dashed outline. The site map
  skips them (it draws its own from the survey).

<!-- from line 632 -->
## 2026-10-14: Red House offices without closets
- Architect's accessibility comments (not yet on the sheets): the closets along the south walls of Office 1 and
  Office 2 are removed on Levels 1, 2, and 3. Done in `tools/build_red_house.py` as an edit after the sheets load:
  two closet boxes on the Level 1 sheet, carried to Levels 2 and 3 by the Office 1 label; every drawn item with all
  its points inside a box is dropped (62 per Level: closet walls, bifold doors, headers), and each office's walls are
  closed along the corridor wall. The dashed marks left there are the Existing walls shown as removed.

<!-- from line 644 -->
## 2026-10-15: Red House program key; Level 3 patio artifact
- Program toggle on the Red House slide ("Program" button in the key; applies to whichever Level is showing).
  Architect's colours: yellow circulation (hall, lobby, commons), blue restrooms, red primary spaces (conference,
  instructional classroom / event space, demo kitchen), grey storage; Claude's picks: green offices and staff
  (offices), orange kitchen support (dishwash, cooler, pantry, and the breakroom, moved there by the architect). Porches, patio, covered walkway, and
  carport stay uncoloured.
- Rooms are found in `tools/build_red_house.py` from the walls and windows: each label's core is the area more than r
  from any line, with r raised per room (14 to 50 pt) until the core is closed off from the outside and doesn't run
  under another use's room name; rooms open between posts (the classroom) also use the roof edge; a small room whose
  doorway is as wide as the room is seeded at its label. Cores grow back to the walls by watershed, meeting at the
  doorways. `RH_DEBUG=<dir>` writes a check image per Level.
- Level 3: the addition inset's patio (label, roof edge, paving lines) reached past the inset's exclusion box and
  showed as a stray patio beside the house. The box now runs 620 pt left of the inset title; the patio label is kept
  out of the addition fit (fit unchanged: 98.6% of walls within 1 pt).
