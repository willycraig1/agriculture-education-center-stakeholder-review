"""Build drawings/fencing-plan-trees.svg: the proposed pasture fencing plan with existing trees.

Sources (all in source/):
  Clark Farm Proposed Fencing Plan.pdf   fence lines, ponds, drive, acreage labels (base frame)
  Clark Farm Study Plan-A0.1 (3)1.pdf    surveyed trees around the campus (most detailed)
  Survey + Soils Map Info.pdf            surveyed trees outside the study-plan sheet, tree line,
                                         existing building footprints
  Clark_Farm_Pasture_Calculations.xlsx   canopy class per paddock (labels)
Colors come from design/palette.json. Sheet-to-sheet transforms come from tools/registration.json
(run tools/register.py to regenerate). Output SVG has one named layer per content type, so it opens
with editable layers in Illustrator or Inkscape. Also writes drawings/data/trees.csv.

Run:  python tools/build_fencing_trees.py   (needs pymupdf, numpy, scipy, openpyxl)
"""
import csv, json, os, sys
import numpy as np
import openpyxl
import pymupdf


from siteframe import *  # noqa: F401,F403  (shared geometry, transforms, trees, labels)

os.makedirs(os.path.join(OUT, "data"), exist_ok=True)
with open(os.path.join(OUT, "data", "trees.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["source_sheet", "x_pt_fencing_sheet", "y_pt_fencing_sheet", "symbol_size_ft"])
    for src, x, y, s in trees:
        w.writerow([src, f"{x:.2f}", f"{y:.2f}", f"{s:.1f}"])

def tag(ac, x, y):
    area, cls = canopy.get(ac, ("?", "?"))
    key = "pasture" if area == "Site Pasture" else "bonus"
    c = P[key]
    w = 92
    wooded = "woods" in cls
    return (f'<g class="tag {key}" transform="translate({x:.1f} {y:.1f})">'
            f'<rect x="{-w/2}" y="-19" width="{w}" height="38" rx="5" fill="{c["tint"]}" stroke="{c["base"]}" stroke-width="1.6"/>'
            f'<text y="-1" text-anchor="middle" font-size="17" font-weight="700" fill="{N["ink"]}">{ac:g} ac</text>'
            f'<text y="13" text-anchor="middle" font-size="11" fill="{P["woodland"]["base"] if wooded else N["muted"]}">{cls}</text></g>')

# ---------------------------------------------------------------- assemble
x0, y0, x1, y1 = VIEW
W, H = x1 - x0, y1 - y0
font = "font-family=\"'Source Sans 3','Helvetica Neue',Arial,sans-serif\""
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" '
       f'viewBox="{x0} {y0} {W} {H}" width="{W}" height="{H}" {font}>',
       f'<title>Clark Farm: proposed pasture fencing with existing trees</title>',
       f'<rect id="paper" x="{x0}" y="{y0}" width="{W}" height="{H}" fill="{N["paper"]}"/>']

svg.append(layer("woodland-edge", "Woodland edge (survey tree line)",
                 f'<g transform="{mat(M_SF, T_SF)}" fill="none" stroke="{P["woodland"]["base"]}" '
                 f'stroke-width="{2.2/abs(M_SF):.3f}" stroke-dasharray="{6/abs(M_SF):.2f} {3/abs(M_SF):.2f}" '
                 f'stroke-linecap="round">{paths(sv.get("TREE LINE", []))}</g>', ROT))
svg.append(layer("water", "Water / stormwater",
                 f'<g fill="{P["water"]["tint"]}" stroke="{P["water"]["base"]}" stroke-width="1.4">{paths(water_ds)}</g>', ROT))
svg.append(layer("drive", "Drives",
                 f'<g fill="none" stroke="{P["circulation"]["base"]}" stroke-width="2.4" stroke-linejoin="round">{paths(drive_ds)}</g>', ROT))
svg.append(layer("fence", "Proposed pasture fencing",
                 f'<g fill="none" stroke="{N["ink"]}" stroke-width="1.6" stroke-linecap="round">{paths(fence_ds)}</g>', ROT))
svg.append(layer("buildings", "Existing structures",
                 f'<g fill="{P["circulation"]["tint"]}" stroke="{P["circulation"]["base"]}" stroke-width="1">{paths(bldg_ds)}</g>'
                 f'<g transform="{mat(M_SF, T_SF)}" fill="{P["circulation"]["tint"]}" stroke="{P["circulation"]["base"]}" '
                 f'stroke-width="{0.8/abs(M_SF):.3f}">{paths(sv.get("BUILDING", []))}</g>', ROT))

tree_svg = []
for src, x, y, s in trees:
    r = 5.2 if s > 20 else 3.6
    tree_svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>')
svg.append(layer("trees", "Existing trees (surveyed)",
                 f'<g fill="{P["woodland"]["base"]}" fill-opacity="0.78" stroke="{P["woodland"]["base"]}" stroke-width="0.6">{"".join(tree_svg)}</g>', ROT))

svg.append(layer("labels", "Paddock labels", "".join(tag(ac, *rot(x, y)) for ac, x, y in labels) +
                 f'<text x="1095" y="292" text-anchor="middle" font-size="17" font-weight="700" letter-spacing="2" '
                 f'fill="{P["cattle"]["base"]}">CAMPUS</text>'))

# legend / title block in the empty lower-left of the (rotated) sheet
lx, ly = 110, 905
site_ac = sum(a for a, (g, _) in canopy.items() if g == "Site Pasture")
bonus_ac = sum(a for a, (g, _) in canopy.items() if g == "Bonus Pasture")
bar_ft = 500
bar_pt = bar_ft / FT_PER_PT
leg = [f'<text x="{lx}" y="{ly}" font-size="34" font-weight="700" fill="{N["ink"]}">Pasture Fencing &amp; Existing Trees</text>',
       f'<text x="{lx}" y="{ly+30}" font-size="16" fill="{N["muted"]}">Clark Farm · Agriculture Education Center · stakeholder review draft</text>']
rows = [("swatch", P["pasture"], f"Site pasture · Levels 1–3 · {site_ac:.1f} ac"),
        ("swatch", P["bonus"], f"Bonus pasture · Level 3 · {bonus_ac:.1f} ac"),
        ("tree", P["woodland"], f"Existing tree, surveyed ({len(trees)} shown)"),
        ("edge", P["woodland"], "Edge of wooded area (survey tree line)"),
        ("fence", None, "Proposed pasture fence"),
        ("water", P["water"], "Pond / retention area"),
        ("drive", P["circulation"], "Drive / solid site edge")]
yy = ly + 72
for kind, c, text in rows:
    if kind == "swatch":
        leg.append(f'<rect x="{lx}" y="{yy-13}" width="34" height="18" rx="4" fill="{c["tint"]}" stroke="{c["base"]}" stroke-width="1.6"/>')
    elif kind == "tree":
        leg.append(f'<circle cx="{lx+17}" cy="{yy-4}" r="5.2" fill="{c["base"]}" fill-opacity="0.78"/>')
    elif kind == "edge":
        leg.append(f'<line x1="{lx}" y1="{yy-4}" x2="{lx+34}" y2="{yy-4}" stroke="{c["base"]}" stroke-width="2.2" stroke-dasharray="6 3"/>')
    elif kind == "fence":
        leg.append(f'<line x1="{lx}" y1="{yy-4}" x2="{lx+34}" y2="{yy-4}" stroke="{N["ink"]}" stroke-width="1.6" stroke-dasharray="14 6"/>')
    elif kind == "water":
        leg.append(f'<rect x="{lx}" y="{yy-13}" width="34" height="18" rx="7" fill="{c["tint"]}" stroke="{c["base"]}" stroke-width="1.4"/>')
    elif kind == "drive":
        leg.append(f'<line x1="{lx}" y1="{yy-4}" x2="{lx+34}" y2="{yy-4}" stroke="{c["base"]}" stroke-width="2.4"/>')
    leg.append(f'<text x="{lx+48}" y="{yy+1}" font-size="16" fill="{N["ink"]}">{text}</text>')
    yy += 30
yy += 14
leg.append(f'<g transform="translate({lx} {yy})"><rect width="{bar_pt/2:.1f}" height="7" fill="{N["ink"]}"/>'
           f'<rect x="{bar_pt/2:.1f}" width="{bar_pt/2:.1f}" height="7" fill="none" stroke="{N["ink"]}" stroke-width="1"/>'
           f'<text y="26" font-size="13" fill="{N["muted"]}">0</text>'
           f'<text x="{bar_pt/2:.1f}" y="26" font-size="13" text-anchor="middle" fill="{N["muted"]}">250</text>'
           f'<text x="{bar_pt:.1f}" y="26" font-size="13" text-anchor="middle" fill="{N["muted"]}">500 ft</text></g>')
# north arrow: survey north points left in this orientation
leg.append(f'<g transform="translate({lx + bar_pt + 90:.1f} {yy + 4})"><path d="M-22 0 L10 -11 L4 0 L10 11 Z" fill="{N["ink"]}"/>'
           f'<text x="24" y="6" font-size="17" font-weight="700" fill="{N["ink"]}">N</text></g>')
yy += 58
notes = ["Trees: Seibert study plan A0.2 (campus) and survey A0.1 (rest of parcel), overlaid by matching",
         "the CAD sheets (see tools/registration.json). Symbols are schematic, not canopy to scale.",
         "Bonus pasture woodland was not part of the tree survey; canopy notes come from the pasture worksheet.",
         "Scale calibrated to paddock acreages, approx. 1 in = 186 ft on the 36x24 sheet."]
for t in notes:
    leg.append(f'<text x="{lx}" y="{yy}" font-size="12.5" fill="{N["muted"]}">{t}</text>')
    yy += 18
svg.append(layer("legend", "Title and legend", "".join(leg)))
svg.append("</svg>")

os.makedirs(OUT, exist_ok=True)
out_svg = os.path.join(OUT, "fencing-plan-trees.svg")
open(out_svg, "w").write("\n".join(svg))
pix = pymupdf.open(out_svg)[0].get_pixmap(dpi=96)
pix.save(os.path.join(OUT, "fencing-plan-trees.png"))
print(f"trees: {len(trees)} ({sum(1 for t in trees if t[0].startswith('study'))} study plan, "
      f"{sum(1 for t in trees if t[0].startswith('survey'))} survey); labels: {len(labels)}; wrote {out_svg}")
