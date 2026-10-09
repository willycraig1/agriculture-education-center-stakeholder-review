# Project Notes

## Meeting
- Presentation to the owner: Wednesday 2026-10-14, 30–45 min
- Format: presented live and sent ahead as a link
- Narrative and gap list: `docs/presentation-outline.md`
- Owner / decision needed: _TBD_

## Program
Source: `source/Clark Farm Master Plan - PROGRAM DRAFT_Extension comments 7-9-26.docx` (Owner review draft)
- Beginning Farmer and 4-H Youth Agriculture Complex, Clark Farm, 9600 SR-72, Sarasota (Seibert project 2601)
- Elements: A Red House (ops/education/outreach) · B Primary barn (reuse) · C Unfinished new barn · D Cattle barn · E Small animal barn · F Pastures · G Arena/turnout · H Horticulture · I Kennel/ancillary · J Site infrastructure
- Planning modules: cattle pens 12'×24', small animal pens 6'×10' (The Farm precedent), checked against the Ag Guide 4th ed.
- Ag Guide Table 6-1 (p. 92): beef cattle under cover need about 20–50 sf per head depending on class and bedding. A 12'×24' pen (288 sf) is well above that, so pen count follows the number of animals, not welfare minimums.
- Study plan A0.2 shows 51 cattle pens (7+9+9+9+17), 32 hog pens, 51 + 9 parking spaces, turnout yards, "barnyard", retention area, bioswale, horticulture area
- Red House plans in investment Levels: Existing, Level 1, Level 2, Level 3 (Level 3 adds event space / classroom addition and equipment carport)

## Site data
- Pasture worksheet `source/Clark_Farm_Pasture_Calculations.xlsx` (UF/IFAS AN155 stocking rates):
  - Site pasture 45.1 ac (24.7 open/light, 20.4 dense) at 4 / 25 ac per CE → ≈7 CE (Level 1)
  - Site + bonus 99.6 ac (43.8 open, 55.8 dense) at 2 / 10 ac per CE → ≈27 CE (Ultimate)
  - Middle cells: site at improved management ≈14 CE; site + bonus at conservative management ≈13 CE
  - The draft infographic still shows the earlier ≈6 / ≈25 CE (18.9/26.2 and 38.0/61.6 ac). It needs updating.
- Soils (survey sheet): Bradenton, Holopaw, Delray, EauGallie/Myakka, Floridana & Gator, Pineda; Cowpen Slough along the west; FEMA flood zone line crosses the site
- Trees: survey and study plan carry `TreesMARK` / `TREE LINE` layers. The tree survey covers the parcel only, not the bonus pasture.

## Drawings (generated, auditable)
- `drawings/fencing-plan-trees.svg` (+ `.png`, `data/trees.csv`): fencing plan with 362 surveyed trees (266 from the study plan, 96 from the survey), the woodland edge, and paddock tags colored by site/bonus with canopy class from the worksheet. Built by `tools/build_fencing_trees.py`.
- Sheet registration: `tools/register.py` → `tools/registration.json`. Survey→study plan matched on 59 trees (≈0.6 ft); survey→fencing plan fit on the pond and the campus turnout fence (≈3–4 ft).
- Fencing sheet scale ≈ 2.59 ft/pt (≈1" = 186'), calibrated from the 14.4 AC and 4.9 AC labels.
- On the fencing sheet, survey north points to +x (right), *if* the survey sheet is plotted north-up. Not confirmed, so the drawing has no north arrow yet.
- Tooling: Python with pymupdf, numpy, scipy, openpyxl (`tools/requirements.txt`).

## Design system
- Program palette: `design/palette.json` (source of truth) → `design/palette.css`, `design/palette.html` via `tools/build_palette.py`
- Each program element has one hue that is used for nothing else. Phase is shown by tint/hatch, never by a new hue.

## Constraints

## Decisions
- 2026-10-08: Use an HTML slideshow on GitHub Pages (public link accepted) instead of PDF/PowerPoint
- 2026-10-08: Drawings come in as CAD-exported vector PDFs with text and layers kept; DXF optional for floor plans (3D)
- 2026-10-08: Plan: core slides first → plan animations → 3D as a stretch goal; PDF export as a backup
- 2026-10-09: Narrative leads with cattle: pasture capacity → herd size → cattle facilities → other programs → Red House → phasing
- 2026-10-09: Program color palette adopted (draft, pending review)

## Open questions
- Are "Levels" the investment-tier framework for every program element? Does pasture "Ultimate" equal Level 3, and is there a Level 2?
- Basis for converting CE to project cattle (class and weight), and do pen-housed project animals count against pasture capacity?
- What is the target cattle pen count per Level (A0.2 shows 51)?
- Confirm north orientation on the fencing plan
- Is there an aerial or canopy data for the bonus pasture woodland?
- Can paddock boundaries be exported as closed polylines (DXF) so paddocks can be color-filled?
- Do any barn plans or sketches exist (e.g., The Farm precedent barns)?
- Can the source documents (survey, program draft with Extension comments) go in a public repo?
