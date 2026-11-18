# Agriculture Education Center – Stakeholder Review

An HTML slideshow for the owner's stakeholder review: animated site and floor plans, plus a rough 3D massing model for scale. Hosted on GitHub Pages so it can be shared by link, and it also runs offline from this folder.

## Layout

- `source/` – original drawings (CAD-exported vector PDFs; DXF optional for floor plans) and reference documents. **Local only, gitignored**: this repo is public, so client originals are never committed
- `docs/README.md` – **start here**: which reference page or log to read for each kind of task
- `docs/reference/` – short guides to the current plan, plus the generated figures register
- `docs/log/` – project log by subject (`NOTES.md` is its index)
- `slides/` – HTML slides (1920×1080, arrow keys step through builds, `?static` for the finished frame)
- `docs/presentation-outline.md` – presentation narrative (outline of record) and gap list
- `photos/` – site photos for the existing-buildings slide (see `photos/README.md` for file names)
- `design/` – program color palette (`palette.json` is the source of truth)
- `drawings/` – generated drawings: layered SVG masters (editable in Illustrator/Inkscape), PNG previews, extracted data
- `tools/` – scripts that rebuild every generated drawing from `source/`

## Rebuilding drawings

```
python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
.venv/bin/python tools/register.py            # sheet-to-sheet alignment -> tools/registration.json
.venv/bin/python tools/build_fencing_trees.py # drawings/fencing-plan-trees.svg
.venv/bin/python tools/build_palette.py       # design/palette.css + palette.html
.venv/bin/python tools/build_capacity_data.py # slides/data/pasture-capacity.js from the pasture worksheet
.venv/bin/python tools/import_site_edits.py   # architect's boundary, ponds, structures -> drawings/data/site-edits.json
.venv/bin/python tools/build_ag_area.py       # barnyard diagram (run before the site map)
.venv/bin/python tools/build_fences.py        # fences and property lines as polylines -> drawings/data/fences.json
.venv/bin/python tools/register_aerial.py     # fit the aerial to the property lines
.venv/bin/python tools/build_canopy.py        # canopy, drives, slough from the aerial trace -> drawings/data/aerial-derived.json
.venv/bin/python tools/build_site_map.py      # drawings/site-layers.svg + slides/data/site-map.js
.venv/bin/python tools/build_red_house.py     # drawings/red-house-levels.svg + slides/data/red-house.js
.venv/bin/python tools/build_ag_area.py       # drawings/ag-area-diagram.svg + slides/data/ag-area.js
.venv/bin/python tools/build_stormwater_concept.py # owner's stormwater direction -> drawings/data/stormwater-concept.js (site plan sheets)
.venv/bin/python tools/build_report_data.py   # figures register -> drawings/data/report-data.json + docs/reference/figures.md
```

Windows commands and the stormwater-only rebuild are in `docs/reference/drawing-pipeline.md`.

## Viewing

Open the deck at https://willycraig1.github.io/agriculture-education-center-stakeholder-review/ , or serve this folder locally (`python3 -m http.server`) and open `index.html`, or visit the GitHub Pages link once it's enabled.
