# Owner reviews and direction

Moved verbatim from the original NOTES.md. `<!-- from line n -->` marks where each entry stood.

<!-- from line 758 -->
## 2026-10-19: owner's review; report reference archived; main parcel only
- Owner (Lee Hayes Byron) reviewed the draft (`source/Architect stakeholder-mtg presentation- review-draft_LHB.pdf`,
  kept local, not in the public repo): the audience is internal (her and her staff); shorter, less detail on the
  slides (details to speaker notes), lead with the Level 3 vision and walk back to Level 1, more renderings and
  comparative images (McIntosh, Siesta Key Chapel for the event space), and communicate only about the main property:
  no bonus pasture, nothing that commits Solid Waste beyond what it has provided.
- Archived the full detailed deck as the reference for the final report: `archive/report-reference-2026-10-19/`
  (self-contained copy of the working tree, including the uncommitted 16' aisle / McIntosh barn changes).
- Main parcel only (`tools/siteframe.py` MAIN_PARCEL_ONLY = True; set False for the report): the site maps show the
  side of parcel line pl-04 the campus is on (65.1 ac of the 154.9 ac property). Soils, canopy, trees, pasture
  areas, paddocks, fences, property lines, campus drives, the historical bed, ponds, and the flood line are clipped
  to it (Cowpen Slough is kept whole); the veil washes out the rest. Bonus retention and the outfall (on Solid Waste
  land) are dropped. Every map slide's full frame is the parcel. The site's figures count the parcel only (65 ac,
  canopy 28 ac / 43%, very poorly drained 13%, slough bed 2.4 ac, one pond).
- Pasture: Level 3 grazes the site pasture as Level 2 does (about 15 CE); `build_capacity_data.py` reads the switch.
  The capacity slide shows two cards (Level 1; Levels 2 and 3); the Levels table's Level 3 pasture reads "Same as
  Level 2"; the paddocks slide loses its bonus step; the site, three Levels, and water slides drop the bonus land,
  the bonus retention, the outfall, and the landfill line.

<!-- from line 777 -->
## 2026-10-19: owner's slide comments, first pass
- Red House: program colours on by default (the owner found the coloured plans easier); the Program button still
  turns them off. The PDF export no longer adds separate program pages.
- Wording per her notes: design drivers (pasture sentence clarified; reuse "and limiting costs"; "first come, first
  served" dropped; water generalized to design and operations); three Levels (Level 2 "more program capacity", not
  "managed harder"); cattle pens (title "Pens grow with demand", the herd "lives primarily on pasture", second barn
  "if funds and demand are present", Cow Pen Slough sticky note removed, Level 1 "existing pens at the barn");
  "What each Level provides"; program ground rule adds "or wetlands"; water quality pared to seven short points with no
  Playbook citations or compensation (detailed version in the archive); closing slide reworded positively and cut
  to one or two questions per topic on usability and desired features.
- Floodplain compensation is held back from this presentation (owner's concern about pastures as compensation; civil
  has new thoughts in its 2026-10-16 narrative, not to be introduced yet). The fact sheet is a separate task.

<!-- from line 973 -->
## 2026-10-20: owner's comments on the presentation (eve of the meeting)
- Cow & calf pens: title "Pens scale with funding and demand"; the lede no longer says the Beginning Rancher herd lives
  on pasture or ties growth to enrollment ("added in 7-pen modules as funding allows and demand grows", after the fact
  sheet's "as funding allows"); module card "A second barn can follow as funding allows and demand grows."
- Over to you: "How would you use the site day to day?" (no "and your staff"); Barns and animals adds "How could the
  project maximize usability for livestock management?"

<!-- from line 1190 -->
## 2026-11-16: stakeholder feedback and owner direction (meetings of 10-21, 11-02, and 11-12)
Sources: Seibert meeting notes in the project folder's `Meeting Notes/` (10-21 stakeholder review; 11-02 and 11-12
progress meetings). Meeting notes are treated as final even where the file is labelled Draft (architect, 2026-11-16).
The notes themselves are not committed; this entry summarizes them.

**Stakeholder review, 10-21** (flip charts typed by the County, then clarified by Lee Hayes). No changes are approved
unless the owner says so.
- Flooding and pasture use are the main concern, especially during the October to March fair season. Lee Hayes asked
  that the Level 3 site design deal with flooding as fully as it can, pasture flooding above all; civil to evaluate.
- Livestock: gates and pasture links for safe movement, water throughout, wind or solar well pumps, vet and handling
  facilities, beef breeding pasture, pest control (pasture mealybug), and the chute kept open as a public resource.
- Uses suggested: aquaculture in the existing barn, poultry processing and storage, poultry tractors, a silviculture
  demonstration lot, equine and equine therapy, an apiary, ag-technology demonstrations, and areas for dogs.
- Shows (jackpot and invited), with parking and event operations; volunteer and full utility hookups.
- Solar: grid-tied for the buildings and off-grid for remote loads; aquaponics tied to the stormwater system.
- Name vote (stickers): Agriculture Education Center 5, SAGE Ranch 5, GROW Sarasota County 4, Fields of
  Opportunity 2, Farm Futures 2, Roots 2, RANCH Center 2, Heritage Ranch 1. No name chosen yet.

**Owner direction, 11-02** (Lee Hayes, Matt Ingram). Nothing was denied; everything depends on demand, funding, and
phasing.
- Poultry tractors at Level 1. Poultry processing and storage at Level 3. Look into floating "duck island" coops.
- Separate budget line items, outside the Levels: innovation, a dog agility course, and an aquaculture system like the
  MMS installation.
- Site plan: a dedicated apiary location, a dedicated kennel location, one pen or paddock for equine projects, and the
  north triangle pasture as a possible silvopasture demonstration area.
- Overflow parking within walking distance; it may go onto Solid Waste property or onto widened road shoulders.
  Access control from the south through Solid Waste property still to be coordinated.
- "Volunteer hookups": assume the caretaker RV hookups cover them, pending confirmation of what was meant.
- Report: two full-time staff minimum, four recommended. Operating procedures (escaped animals, storm preparation,
  public use of the chute, project selection, maintenance, youth and adult separation, participant agreements, and
  handling training) go in the report, and shape the facilities only where they need space, equipment, security, or
  infrastructure.
- Solar: battery backup only for off-grid systems.
- Cost estimate: each Level carried separately, each improvement its own line item, so items can move between Levels
  after pricing.

**Owner direction, 11-12** (with Brad Gaubatz and Kate Traugott).
- Horticulture programs add urban farming models (hydroponics and the like) and ECHO Farm principles (diverse,
  year-round perennial crops and markets for them).
- Apiary: well away from the core campus; mobile hives and electric fencing; bee suits stored in a climate-controlled
  space; a place in the field to clean honey off suits.
- Veterinary support is covered by the chute, medicine storage, and easy vehicle access across the campus. Kate will
  supply procedure and policy documents.
- Equine: a contingency only. 4-H has a mini-horse program, but the need for capacity here is unclear.
- Beef breeding shade, fixed systems only (no canopies for staff to move in an emergency): fabric shade structures at
  Level 1, a permanent pole barn at Level 2, in all central pasture service and circulation areas.
- Schedule: to the cost consultant by 11-19; pricing back by 12-03; cost review meeting 12-07 at 4 pm. Resend the
  renderings to Lee Hayes.

**Deck not updated.** This direction goes to the cost estimator and the consultants for their reports and narratives;
the 10-21 deck stays as presented (`slides/data/levels.js` unchanged). It is carried in the program's pricing draft
and cover memo of 2026-11-16 (project folder, `Task 2 - Program and Site Analysis/`, not committed): line items by
Level (L1-, L2-, L3-), items with no Level yet (A-), and items priced outside the Levels (S-).

**Open**
- Animal quarantine requirements (Kate): not settled at either meeting.
- Levels for the apiary, kennel, silvopasture area, and horticulture additions.
- What stakeholders meant by "volunteer hookups".
- Project name.
