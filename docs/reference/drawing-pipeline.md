# Drawing pipeline

Generated files are never edited by hand. Change the script or its inputs, then rebuild.

## Setup on this Windows computer

```powershell
python -m venv .venv
```

```powershell
.venv\Scripts\python -m pip install -r tools\requirements.txt
```

## Stormwater rebuild

Use this after changing `tools/stormwater_inputs.py`.

```powershell
.venv\Scripts\python tools\build_stormwater_concept.py
```

```powershell
.venv\Scripts\python tools\build_report_data.py
```

```powershell
.venv\Scripts\python tools\export_sheets.py site campus
```

## Meandering channel option

The option reads the stormwater concept and never changes it. Rebuild it after any stormwater rebuild. It prints to its own PDFs, `exports/site-plan-AS-1-option-meander.pdf` and `AS-2-option-meander.pdf`.

```powershell
.venv\Scripts\python tools\build_meander_option.py
```

```powershell
.venv\Scripts\python tools\export_sheets.py --option meander site campus
```

Adding `?option=meander` to a sheet's address shows the option. Without it, the sheets show the base plan.

## Figures rebuild

Use this after changing `tools/build_report_data.py`.

```powershell
.venv\Scripts\python tools\build_report_data.py
```

## Full rebuild order

Run these in order after a change to the base drawings. The barnyard and site map each run twice. This order combines the README with the run order in the project log. It has not been run end to end on this computer.

| Step | Script | Makes |
|---|---|---|
| 1 | `register.py` | `tools/registration.json` |
| 2 | `build_fencing_trees.py` | `drawings/fencing-plan-trees.svg` |
| 3 | `build_palette.py` | `design/palette.css` |
| 4 | `import_site_edits.py` | `drawings/data/site-edits.json` |
| 5 | `build_fences.py` | `drawings/data/fences.json` |
| 6 | `register_aerial.py` | Aerial fit |
| 7 | `build_canopy.py` | `drawings/data/aerial-derived.json` |
| 8 | `build_south_roads.py` | `drawings/data/south-roads.json` |
| 9 | `build_slough_bed.py` | `drawings/data/slough-bed.json` |
| 10 | `build_civil.py` | `drawings/data/civil.json` |
| 11 | `build_ag_area.py` | Barnyard data for the site map |
| 12 | `build_site_map.py` | `slides/data/site-map.js` |
| 13 | `build_retention_markup.py` | `drawings/data/retention-markup.json` |
| 14 | `build_site_map.py` | `slides/data/site-map.js`, with the ponds |
| 15 | `build_capacity_data.py` | `slides/data/pasture-capacity.js` |
| 16 | `build_red_house.py` | `slides/data/red-house.js` |
| 17 | `build_ag_area.py` | `slides/data/ag-area.js` |
| 18 | `build_stormwater_concept.py` | `drawings/data/stormwater-concept.js` |
| 19 | `build_report_data.py` | `drawings/data/report-data.json`, `docs/reference/figures.md` |
| 20 | `stamp.py` | Cache-busting links on the slides |
| 21 | `export_sheets.py` | `exports/site-plan-AS-0.pdf` through `AS-2.pdf` |

## What feeds the sheets

```text
tools/stormwater_inputs.py
  -> tools/build_stormwater_concept.py -> drawings/data/stormwater-concept.js
       -> tools/sheet.html -> tools/export_sheets.py -> exports/site-plan-AS-1.pdf, AS-2.pdf
       -> tools/build_report_data.py -> drawings/data/report-data.json, docs/reference/figures.md
```

The stormwater concept appears on AS-1 and AS-2 only. The deck slides do not load it. Adding `?stormwater=0` to a sheet's address shows the plan without it.

## Reviewing the sheets

Serve the repository from its root, then open `http://localhost:8917/tools/review.html`.

```powershell
python -m http.server 8917
```

The browser pane in the desktop app downloads PDFs instead of showing them, so use the review page there.

## Checks after a rebuild

1. Compare `figures.md` with its previous version, and explain any change.
2. Confirm storage gained is at or above storage lost.
3. Open both sheets on the review page and check them against `drafting-standards.md`.
4. Confirm the new PDFs show the change. On Windows, Chrome returns before printing ends, so `export_sheets.py` waits for the finished file.
