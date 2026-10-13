"""Read the architect's Illustrator edits of the site plan into drawings/data/site-edits.json.

Source: source/site-edits/site-edits-2026-10-13.ai (Illustrator file with PDF content, one layer). It was
drawn over drawings/site-layers.svg on the same artboard, so artboard point (0, 0) is the map's view origin
and the shapes drop straight into the presentation frame (north left) after adding that origin.
Contents, told apart by color: the site boundary (dark stroke, no fill), ponds (blue fill), existing
structures (red fill). The pond beside the campus is the proposed retention pond; the other two exist.

Run:  python tools/import_site_edits.py   (needs pymupdf), then tools/build_site_map.py
"""
import json, os, sys
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
import cadpdf

SRC = os.path.join(ROOT, "source", "site-edits", "site-edits-2026-10-13.ai")
ORIGIN = (40, 110)                       # view origin of drawings/site-layers.svg

page = pymupdf.open(SRC, filetype="pdf")[0]
out = {"source": os.path.relpath(SRC, ROOT), "origin": ORIGIN, "boundary": [], "ponds": [], "structures": []}
seen = set()
for d in page.get_drawings():
    fill, stroke = d.get("fill"), d.get("color")
    r = d["rect"]
    pts = []
    for it in d["items"]:
        if it[0] == "l":
            pts += [it[1], it[2]]
        elif it[0] == "c":
            pts += [it[1], it[4]]
        elif it[0] == "qu":
            q = it[1]; pts += [q.ul, q.ur, q.lr, q.ll]
        elif it[0] == "re":
            q = it[1]; pts += [q.tl, q.tr, q.br, q.bl]
    xy = []
    for q in pts:
        c = [round(q.x + ORIGIN[0], 2), round(q.y + ORIGIN[1], 2)]
        if not xy or xy[-1] != c:
            xy.append(c)
    path = cadpdf.path_d(d)
    if fill is None and len(d["items"]) > 10:
        if xy[0] != xy[-1]:
            xy.append(xy[0])
        out["boundary"] = xy
    elif fill is not None and fill[2] > fill[0]:                  # blue: ponds
        cx = (r.x0 + r.x1) / 2 + ORIGIN[0]
        # the pond beside the campus is the proposed retention pond (confirmed by the architect)
        out["ponds"].append({"kind": "proposed retention" if 1100 < cx < 1350 else "existing", "d": path, "pts": xy})
    elif fill is not None and fill[0] > 0.5 and len(d["items"]) >= 3:   # red: structures (skip stray single strokes)
        key = tuple(round(v) for v in r)
        if key in seen:
            continue
        seen.add(key)
        out["structures"].append({"d": path, "pts": xy, "bbox": [round(v + o, 1) for v, o in zip(r, ORIGIN * 2)]})
json.dump(out, open(os.path.join(ROOT, "drawings", "data", "site-edits.json"), "w"), indent=1)
print("boundary vertices:", len(out["boundary"]), "| ponds:", [p["kind"] for p in out["ponds"]], "| structures:", len(out["structures"]))
