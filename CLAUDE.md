# Agriculture Education Center – Stakeholder Review

An HTML slideshow for the owner's stakeholder review of Clark Farm (Seibert project 2601). Hosted on GitHub Pages, and it also runs offline.

Read before changing anything:
1. `NOTES.md`: project log (program, site data, decisions, open questions). Add new decisions here.
2. `docs/presentation-outline.md`: the narrative of record and the gap list.
3. `README.md`: folder layout and the full drawing rebuild order.

## Rules
- Generated files (`drawings/`, `slides/data/`, `design/palette.css`) are built by `tools/` from `source/`. Change the script or the source, never the output.
- `design/palette.json` is the color source of truth.
- North is to the **left** in every graphic.
- Slides are 1920×1080. Arrow keys step through builds, and `?static` shows the finished frame for PDF export.
- **This repo is public.** `source/` (client drawings, survey, program drafts, reference books) and the CAD files (`drawings/*.dwg`, `*.bak`) are local only and gitignored. Never commit them or link to them from slides. Publish only generated drawings, photos and slides.

## Run
- Tools: `.venv/bin/python tools/<script>.py` (create the venv per the README).
- Preview: start `python3 -m http.server 8917` from Bash and open http://localhost:8917 (the preview pane can't launch servers from ~/Documents).
- Work goes through branches and PRs into `main`. Pushing to `main` updates the shared link.
