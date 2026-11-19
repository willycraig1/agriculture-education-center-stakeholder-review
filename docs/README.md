# Project guide

Read this page first, then open only the files your task needs. Each reference page is short and covers one subject.

## Where to start

| Your task | Read | Change | Then run |
|---|---|---|---|
| Check where the plan stands | `reference/site-plan-status.md` | Nothing | Nothing |
| Move a swale, pond, path, or culvert | `reference/stormwater-design-basis.md`, `reference/drafting-standards.md` | `tools/stormwater_inputs.py` | Stormwater rebuild |
| Change an elevation or bank slope | `reference/stormwater-design-basis.md` | `tools/stormwater_inputs.py` | Stormwater rebuild |
| Change how the sheets look | `reference/drafting-standards.md` | `tools/sheet.html` | Export the sheets |
| Lay out Red House rooms, furniture, or finishes | `reference/county-interior-standards.md`, `log/04-red-house.md` | `tools/build_red_house.py` | Full rebuild |
| Change the barnyard or buildings | `log/03-barnyard-and-buildings.md`, `reference/drawing-pipeline.md` | `tools/build_ag_area.py` | Full rebuild |
| Quote a number in the report or pricing | `reference/figures.md`, `reference/report-data-framework.md` | Nothing | Nothing |
| Add a number to the register | `reference/report-data-framework.md` | `tools/build_report_data.py` | Figures rebuild |
| Find out why something was decided | The topic log below | Add a dated entry there | Nothing |

The rebuild commands are in `reference/drawing-pipeline.md`.

## Reference pages

| Page | What it answers |
|---|---|
| `reference/site-plan-status.md` | What the plan shows today, what is open, and who has to answer |
| `reference/stormwater-design-basis.md` | The owner's direction, how it is drawn, and which input controls it |
| `reference/drafting-standards.md` | The architect's graphic rules for the site plan sheets |
| `reference/county-interior-standards.md` | County furniture, office, and finish standards for the Red House, and what they leave out |
| `reference/drawing-pipeline.md` | Which script makes which file, and in what order |
| `reference/report-data-framework.md` | How figures reach the report, and what each status means |
| `reference/figures.md` | Every current figure (generated) |

## Decision logs

The logs keep the full history and are long. Search them for a subject instead of reading them through.

| Log | Subject |
|---|---|
| `log/01-foundation.md` | Meeting, program, site data, constraints, and early decisions |
| `log/02-site-and-water.md` | Base map, alignment, water, and floodplain through 2026-10-21 |
| `log/03-barnyard-and-buildings.md` | Barnyard, barns, pens, parking, and Option B |
| `log/04-red-house.md` | Red House |
| `log/05-massing-3d.md` | 3D massing model |
| `log/06-deck-and-slides.md` | Stakeholder deck and slides |
| `log/07-sheets-and-fact-sheet.md` | Print sheets and fact sheet |
| `log/08-owner-direction.md` | Owner reviews and direction |
| `log/09-stormwater-concept.md` | Stormwater concept, November 2026 |

## House rules

- Put each number in one place. Quote `reference/figures.md` instead of retyping a value.
- Record a new decision in its topic log. If it changes the current plan, update the reference page too.
- This repository is public. See "What stays local" in `reference/report-data-framework.md` before adding anything drawn from a draft.
