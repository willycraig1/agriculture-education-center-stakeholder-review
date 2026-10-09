# Agriculture Education Center – Stakeholder Review

An HTML slideshow for the owner's stakeholder review: animated site and floor plans, plus a rough 3D massing model for scale. Hosted on GitHub Pages so it can be shared by link, and it also runs offline from this folder.

## Layout

- `source/` – original drawings (CAD-exported vector PDFs; DXF optional for floor plans) and reference documents
- `NOTES.md` – project log: program, site data, constraints, decisions, open questions
- `docs/` – presentation outline and gap list
- `design/` – program color palette (`palette.json` is the source of truth)
- `drawings/` – generated drawings: layered SVG masters (editable in Illustrator/Inkscape), PNG previews, extracted data
- `tools/` – scripts that rebuild every generated drawing from `source/`

## Rebuilding drawings

```
python3 -m venv .venv && .venv/bin/pip install -r tools/requirements.txt
.venv/bin/python tools/register.py            # sheet-to-sheet alignment -> tools/registration.json
.venv/bin/python tools/build_fencing_trees.py # drawings/fencing-plan-trees.svg
.venv/bin/python tools/build_palette.py       # design/palette.css + palette.html
```

## Viewing

Open `index.html` in a browser, or visit the GitHub Pages link once it's enabled.
