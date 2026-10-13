"""Layout study: ways to keep small animal barn B off the very poorly drained soil.

Reads the barnyard diagram (slides/data/ag-area.js) and the soils and trees already transformed into the
diagram's frame by tools/build_site_map.py (drawings/data/*-in-barnyard-frame.json). Each option moves a few
elements; the script reports, per option, how much of each building and turnout sits on the wettest soil,
whether anything overlaps, and how many surveyed trees fall inside buildings.

Writes drawings/studies/wet-soil-options.svg (+ .png) and drawings/studies/wet-soil-options.json.
Run:  python tools/study_wet_soil.py   (after build_ag_area.py and build_site_map.py; needs shapely, pymupdf)
"""
import copy, json, os
from shapely.geometry import shape, box, Point

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
pal = json.load(open(os.path.join(ROOT, "design", "palette.json")))
P, N = pal["program"], pal["neutral"]
src = open(os.path.join(ROOT, "slides", "data", "ag-area.js")).read()
A = json.loads(src[src.index("{"):src.rindex("}") + 1])
wet = shape(json.load(open(os.path.join(ROOT, "drawings", "data", "soils-in-barnyard-frame.json")))["very poorly"])
trees = [Point(x, y) for x, y in json.load(open(os.path.join(ROOT, "drawings", "data", "trees-in-barnyard-frame.json")))]
BASE = {e["id"]: e for e in A["elements"]}
if "turnout-small-b" not in BASE:
    raise SystemExit("This study compared options for the two-barn layout of 2026-10-12. The barnyard has since adopted a 42' extension "
                     "of barn A instead (see NOTES.md), so the study no longer runs; its results are kept in drawings/studies/.")
KEEP = ["existing-barn", "existing-pens", "cattle-a", "cattle-b", "small-a", "small-b", "arena", "feed-1", "feed-2",
        "turnout-cattle-a", "turnout-cattle-b", "turnout-small-a", "turnout-small-b", "parking", "trailer-stop", "handling"]
NEW = [k for k in KEEP if not k.startswith("existing")]
from shapely.geometry import LineString
BLD = [LineString([(a, b), (c, d)]) for a, b, c, d in json.load(open(os.path.join(ROOT, "drawings", "data", "buildings-in-barnyard-frame.json")))]


def option(name, note, moves):
    els = {k: copy.deepcopy(BASE[k]) for k in KEEP}
    for k, ch in moves.items():
        if "dx" in ch:
            els[k]["x"] += ch["dx"]; els[k]["y"] += ch["dy"]
            els[k].pop("outline", None)
        else:
            els[k].update(ch)
    return dict(name=name, note=note, els=els)


OPTIONS = [
    option("As drawn", "For reference.", {}),
    option("A. Slide the north row 12' south",
           "Barn B, the arena, cattle barn B and their turnouts all move 12' south. The gap between barn rows drops from 24' to 12'.",
           {k: {"y": BASE[k]["y"] + 12} for k in ("small-b", "arena", "cattle-b")} |
           {"turnout-small-b": {"y": 12, "h": 96}, "turnout-cattle-b": {"y": 12, "h": 96},
            "turnout-small-a": {"y": 108, "h": 84}, "turnout-cattle-a": {"y": 108, "h": 108}}),
    option("B. Swap barn B and the arena",
           "Barn B takes the middle strip; the arena moves to the west run. The arena, not a barn, ends up on the wet corner.",
           {"small-b": {"x": 67, "y": 0}, "arena": {"x": -7, "y": 0},
            "turnout-small-b": {"x": -55, "y": 0, "w": 48, "h": 96}}),
    option("C. Barn B beside barn A",
           "Both small animal barns in the south row, side by side, each with a turnout. The north-west corner is left as pasture.",
           {"small-b": {"x": -60, "y": 108}, "turnout-small-a": {"x": -24, "y": 108, "w": 24, "h": 84},
            "turnout-small-b": {"x": -108, "y": 108, "w": 48, "h": 84}}),
    option("D. Barn B in the middle strip, south of the arena",
           "Barn B goes where the feed containers are; the containers move to the west run's north slot. Barn B has no turnout of its own.",
           {"small-b": {"x": 67, "y": 108}, "feed-1": {"x": -2, "y": 66}, "feed-2": {"x": -2, "y": 74},
            "turnout-small-b": {"x": 0, "y": 0, "w": 0, "h": 0}}),
    option("F. Everything new 48' south and 12' west",
           "Every new element, the parking and handling yard included, moves 48' south and 12' west. The existing barn and pens stay put.",
           {k: {"dx": -12, "dy": 48} for k in NEW}),
    option("E. C, plus slide the arena and cattle barn B 12' south",
           "Barn B beside barn A, and the two remaining north-row buildings pulled 12' south. Only a corner of the arena (5%) is left on wet soil.",
           {"small-b": {"x": -60, "y": 108}, "turnout-small-a": {"x": -24, "y": 108, "w": 24, "h": 84},
            "turnout-small-b": {"x": -108, "y": 108, "w": 48, "h": 84},
            "arena": {"y": 12}, "cattle-b": {"y": 12}, "turnout-cattle-b": {"y": 12, "h": 96}, "turnout-cattle-a": {"y": 108, "h": 108}}),
]


def geom(e):
    return box(e["x"], e["y"], e["x"] + e["w"], e["y"] + e["h"])


def assess(opt):
    els = opt["els"]
    out = {"wet_pct": {}, "overlaps": [], "trees_in_buildings": 0}
    solid = [k for k, e in els.items() if e["kind"] in ("building", "container") and e["w"] > 0]
    for k, e in els.items():
        if e["w"] <= 0 or k.startswith("existing"):
            continue
        g = geom(e)
        out["wet_pct"][k] = round(100 * g.intersection(wet).area / g.area)
    for i, a in enumerate(solid):
        for b in solid[i + 1:]:
            if geom(els[a]).intersection(geom(els[b])).area > 1:
                out["overlaps"].append([a, b])
    out["trees_in_buildings"] = sum(1 for t in trees if any(geom(els[k]).contains(t) for k in solid if not k.startswith("existing")))
    # yards and lots against what already exists
    ex = [k for k in els if k.startswith("existing")]
    for k in els:
        if k in ex or els[k]["w"] <= 0:
            continue
        for x in ex:
            a_ = geom(els[k]).intersection(geom(els[x])).area
            if a_ > 1 and [k, x] not in out["overlaps"]:
                out["overlaps"].append([k, x, round(a_)])
    park = geom(els["parking"])
    stalls = box(park.bounds[0], park.bounds[1], park.bounds[2], park.bounds[1] + 128)
    out["trees_in_parking"] = sum(1 for t in trees if park.contains(t))
    # surveyed building lines south of y = 300 are the Red House and its outbuildings
    rh = [l for l in BLD if min(l.coords[0][1], l.coords[1][1]) > 300]
    out["stalls_to_red_house_ft"] = round(min(l.distance(stalls) for l in rh))
    out["red_house_wall_ft_inside_stalls"] = round(sum(l.intersection(stalls).length for l in rh))
    out["small_b_to_small_a_ft"] = round(geom(els["small-b"]).distance(geom(els["small-a"])))
    return out


results = []
for o in OPTIONS:
    r = assess(o)
    results.append({"name": o["name"], "note": o["note"], **r})
    w = r["wet_pct"]
    print(f'{o["name"]:48s} small B {w.get("small-b", 0):3d}%  arena {w.get("arena", 0):3d}%  cattle B {w.get("cattle-b", 0):3d}%  '
          f'| overlaps {r["overlaps"]} | trees in buildings {r["trees_in_buildings"]}, in parking {r["trees_in_parking"]} | stalls to Red House {r["stalls_to_red_house_ft"]} ft, wall inside stalls {r["red_house_wall_ft_inside_stalls"]} ft')

os.makedirs(os.path.join(ROOT, "drawings", "studies"), exist_ok=True)
json.dump(results, open(os.path.join(ROOT, "drawings", "studies", "wet-soil-options.json"), "w"), indent=1)

# ---- small multiples
VX0, VY0, VW, VH = -120, -30, 410, 480
PW, GAP = 410, 30
for l in []: pass
cols = 4
rows = (len(OPTIONS) + cols - 1) // cols
W = cols * PW + (cols + 1) * GAP
H = rows * (VH + 130) + GAP + 50
from shapely.geometry import mapping
def path(g):
    d = ""
    for p in getattr(g, "geoms", [g]):
        if p.geom_type != "Polygon":
            continue
        for ring in [p.exterior, *p.interiors]:
            d += "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in ring.coords) + "Z"
    return d
clipbox = box(VX0, VY0, VX0 + VW, VY0 + VH)
wet_d = path(wet.intersection(clipbox))
font = "font-family=\"Avenir Next,Helvetica,Arial,sans-serif\""
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" {font}><rect width="{W}" height="{H}" fill="{N["paper"]}"/>']
short = {"cattle-a": "Cattle A", "cattle-b": "Cattle B", "small-a": "Small A", "small-b": "Small B", "arena": "Arena",
         "existing-barn": "Existing barn", "existing-pens": "", "feed-1": "", "feed-2": ""}
for i, (o, r) in enumerate(zip(OPTIONS, results)):
    ox = GAP + (i % cols) * (PW + GAP)
    oy = GAP + (i // cols) * (VH + 130)
    svg.append(f'<g transform="translate({ox} {oy})"><text x="0" y="16" font-size="17" font-weight="700" fill="{N["ink"]}">{o["name"]}</text>')
    svg.append(f'<g transform="translate({-VX0} {26 - VY0})"><rect x="{VX0}" y="{VY0}" width="{VW}" height="{VH}" fill="#fff"/>'
               f'<path d="{wet_d}" fill="#9FB9C6" fill-opacity=".75"/>')
    svg.append(''.join(f'<line x1="{l.coords[0][0]}" y1="{l.coords[0][1]}" x2="{l.coords[1][0]}" y2="{l.coords[1][1]}" stroke="{P["education"]["base"]}" stroke-width="1.4"/>' for l in BLD if clipbox.contains(l)))
    for k, e in o["els"].items():
        if e["w"] <= 0:
            continue
        if k in ('parking', 'handling', 'trailer-stop'):
            svg.append(f'<rect x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}" fill="none" stroke="{N["line"]}" stroke-width="1"/>')
        use = "circulation" if k in ("existing-barn",) else e["use"]
        c = P[use]
        yard = e["kind"] == "yard"
        hot = k == "small-b"
        dash = ' stroke-dasharray="4 3"' if yard else ""
        svg.append(f'<rect x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="{e["h"]}" fill="{"none" if yard else c["tint"]}" stroke="{N["ink"] if hot else c["base"]}" '
                   f'stroke-width="{2.4 if hot else 1}"{dash}/>')
        if k in ('parking', 'handling', 'trailer-stop'):
            continue
        if short.get(k):
            svg.append(f'<text x="{e["x"] + e["w"] / 2}" y="{e["y"] + e["h"] / 2 + 3}" text-anchor="middle" font-size="8.5" font-weight="700" fill="{N["ink"]}">{short[k]}</text>')
    svg.append("</g>")
    w = r["wet_pct"]
    line1 = f'Small barn B {w.get("small-b", 0)}% on wet soil · arena {w.get("arena", 0)}% · cattle barn B {w.get("cattle-b", 0)}%'
    svg.append(f'<text x="0" y="{VH + 46}" font-size="14" font-weight="700" fill="{P["water"]["base"]}">{line1}</text>')
    words, lines, cur = o["note"].split(), [], ""
    for wd in words:
        if len(cur) + len(wd) > 62:
            lines.append(cur); cur = wd
        else:
            cur = (cur + " " + wd).strip()
    lines.append(cur)
    for li, ln in enumerate(lines[:3]):
        svg.append(f'<text x="0" y="{VH + 66 + li * 17}" font-size="13" fill="{N["muted"]}">{ln}</text>')
    svg.append("</g>")
lx = GAP
ly = H - 56
svg.append(f'<g transform="translate({lx} {ly})"><rect width="26" height="16" fill="#9FB9C6" fill-opacity=".75"/><text x="36" y="13" font-size="14" fill="{N["ink"]}">Very poorly drained soil (Delray)</text>'
           f'<rect x="300" width="26" height="16" fill="none" stroke="{N["ink"]}" stroke-width="2.4"/><text x="336" y="13" font-size="14" fill="{N["ink"]}">Small animal barn B</text>'
           f'<text x="520" y="13" font-size="13" fill="{N["muted"]}">Barnyard diagram frame, in feet, all panels at one scale. Existing barn at the bottom right; north is roughly up.</text></g>')
svg.append("</svg>")
out = os.path.join(ROOT, "drawings", "studies", "wet-soil-options.svg")
open(out, "w").write("".join(svg))
try:
    import pymupdf
    pymupdf.open(out)[0].get_pixmap(dpi=110).save(out.replace(".svg", ".png"))
except Exception as ex:
    print("png skipped:", ex)
