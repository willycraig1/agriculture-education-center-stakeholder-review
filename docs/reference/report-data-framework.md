# Report data framework

How a number gets from the drawings into the report, the sheets, and pricing.

## The rule

Each figure has one source. The report quotes the register in `figures.md` and cites its ID, such as `earth.import`. The same data is in `drawings/data/report-data.json` for anything that reads it automatically.

## What each status means

| Status | Meaning | How the report should word it |
|---|---|---|
| `directed` | Given by the owner or the architect | State it as fact |
| `measured` | Taken from the survey or the drawings | State it, with "about" for areas |
| `assumed` | Planning assumption that civil has to confirm | "Assumed for planning, to be confirmed by the civil engineer" |
| `estimate` | Calculated from the concept | "About," rounded, and not for construction |
| `needs-recheck` | Calculated before the stormwater concept | Do not publish until it is updated |

## Where each report subject gets its data

| Report subject | Data source | Decision history |
|---|---|---|
| Program and animals | `slides/data/levels.js` | `log/01-foundation.md`, `log/08-owner-direction.md` |
| Levels and phasing | `slides/data/levels.js` | `log/08-owner-direction.md` |
| Site analysis | `slides/data/site-map.js`, `figures.md` | `log/02-site-and-water.md` |
| Pasture and herd capacity | `slides/data/pasture-capacity.js` | `log/02-site-and-water.md` |
| Stormwater and floodplain | `figures.md` | `log/09-stormwater-concept.md` |
| Barnyard and new buildings | `slides/data/ag-area.js` | `log/03-barnyard-and-buildings.md` |
| Red House | `slides/data/red-house.js` | `log/04-red-house.md` |
| Staffing and operations | Owner direction only, no data file yet | `log/08-owner-direction.md` |
| Earlier report material | `archive/report-reference-2026-10-19/` | Its own `README.md` |

## Adding a figure

1. Make sure the value comes from a generated file, not from typed text.
2. Add one row to `GROUPS` in `tools/build_report_data.py`, with an ID, label, value, unit, status, and source.
3. Run the figures rebuild and read the new row in `figures.md`.

## Changing a status

Civil's confirmation of an `assumed` value changes its status to `directed`. Update the row in `tools/build_report_data.py` and record the source in `log/09-stormwater-concept.md`.

## What stays local

This repository is public.

| Can be in the repository | Stays in the project folder |
|---|---|
| Generated drawings and data | Client drawings, survey, and CAD files |
| Summaries of meeting notes | Civil engineer's draft documents |
| The figures register | Program and pricing drafts, including their line items |
| These reference pages | The owner's annotated review copies |

Pricing comparisons quote draft line items, so they stay in `Task 2 - Program and Site Analysis` in the project folder.
