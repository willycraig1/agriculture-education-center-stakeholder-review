"""The historical slough bed across the site, as one field from top of bank to top of bank.

Source: the survey's TOP OF BANK, TOE OF SLOPE and EDGE OF WATER layers. The old channel is the linework that
has a toe of slope (or a water edge) running inside it; the banks of the roadside ditches and of Cow Pen Slough
itself have none and are left out. The banks are drawn in pieces with gaps (culverts, drive crossings), so the
field is built by thickening every bank and toe line until the two banks meet, then shrinking back by the same
amount: what is left runs bank to bank and bridges the gaps along the toe.
Writes drawings/data/slough-bed.json (presentation frame). Run before build_site_map.py.

Run:  python tools/build_slough_bed.py
"""
import json, os, sys
import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from siteframe import OUT, SURVEY, cadpdf, M_SP, T_SP, M_FP, FT_PER_PT

unit_ft = FT_PER_PT / abs(M_FP)

def lines(layer):
    out = []
    for d in cadpdf.export(SURVEY, [layer]).get(layer, []):
        pts = []
        for it in d["items"]:
            if it[0] in ("l", "c"):
                e_ = it[2] if it[0] == "l" else it[4]
                if not pts:
                    pts.append(it[1])
                pts.append(e_)
        q = [M_SP * complex(p.x, p.y) + T_SP for p in pts]
        q = [(z.real, z.imag) for z in q]
        if len(q) >= 2 and LineString(q).length > 0.5:
            out.append(LineString(q))
    return out

tob, toe, water = lines("TOP OF BANK"), lines("TOE OF SLOPE"), lines("EDGE OF WATER")
core = unary_union(toe + water)
REACH = 60 / unit_ft                                   # a bank belongs to the channel when it runs within 60 ft of its toe
def near(g):
    d = [core.distance(g.interpolate(k, normalized=True)) for k in np.linspace(0, 1, 9)]
    return float(np.median(d)) < REACH
banks = [g for g in tob if near(g)]
# bank-to-toe distance sets how far to thicken: enough for the two banks to meet across the bed
d_bank = [core.distance(g.interpolate(k, normalized=True)) for g in banks for k in np.linspace(0, 1, 9)]
r = float(np.percentile(d_bank, 90)) * 1.15
# Thickening the toe lines alone to the usual bank distance gives the bed where a bank is missing; thickening
# banks and toes together and shrinking back gives it bank to bank where both are drawn.
typical = float(np.median(d_bank))
closed = unary_union([g.buffer(r) for g in banks + toe + water]).buffer(-r)
along_toe = unary_union(toe).buffer(typical, cap_style=2)
bed = unary_union([closed, along_toe] + [Polygon(g.coords) for g in water if len(g.coords) >= 4]).buffer(0.8).buffer(-0.8).simplify(0.35)
parts = [g for g in getattr(bed, "geoms", [bed]) if g.area * unit_ft ** 2 > 400]
out = {"source": "survey: TOP OF BANK, TOE OF SLOPE, EDGE OF WATER", "acres": round(sum(g.area for g in parts) * unit_ft ** 2 / 43560, 2),
       "typical_bank_to_toe_ft": round(typical * unit_ft), "bank_pieces_used": len(banks), "bank_pieces_total": len(tob),
       "parts": [{"outer": [[round(x, 1), round(y, 1)] for x, y in g.exterior.coords],
                  "holes": [[[round(x, 1), round(y, 1)] for x, y in h.coords] for h in g.interiors]} for g in parts]}
json.dump(out, open(os.path.join(OUT, "data", "slough-bed.json"), "w"))
print("bank pieces used", len(banks), "of", len(tob), "| toe lines", len(toe), "| water edges", len(water),
      "| bank to toe ft: typical", out["typical_bank_to_toe_ft"], "thicken", round(r * unit_ft), "| parts", len(parts), "| acres", out["acres"],
      "| widths ft:", [round(2 * g.area / g.length * unit_ft) for g in parts])
