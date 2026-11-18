"""One register of the plan's figures, for the report, the sheets, and pricing.

Reads the generated site data and writes:
  drawings/data/report-data.json   every figure with its value, unit, status, and source
  docs/reference/figures.md        the same register as tables, for reading

Each figure carries a status (see docs/reference/report-data-framework.md):
  directed       given by the owner or the architect
  measured       taken from the survey or the drawings
  assumed        a planning assumption that civil still has to confirm
  estimate       calculated from the concept; rough until civil designs it
  needs-recheck  calculated before the stormwater concept and not yet updated for it

Run after build_stormwater_concept.py and build_capacity_data.py:  python tools/build_report_data.py
"""
import json, math, os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def load_js(*path):
    text = open(os.path.join(ROOT, *path), encoding="utf8").read()
    if text.startswith("//"):
        text = text[text.index("\n") + 1:]
    return json.loads(text[text.index("=") + 1:].rstrip().rstrip(";"))


SW = load_js("drawings", "data", "stormwater-concept.js")
SM = load_js("slides", "data", "site-map.js")
CAP = load_js("slides", "data", "pasture-capacity.js")
FT = SM["ft_per_unit"]
E, A, Q = SW["elevations"], SW["areas_ac"], SW["earthwork_cy"]
CONCEPT = "drawings/data/stormwater-concept.js"
INPUTS = "tools/stormwater_inputs.py"


def length_ft(pts):
    return sum(math.dist(p, q) for p, q in zip(pts, pts[1:])) * FT


def area_ac(ring):
    twice = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(ring, ring[1:]))
    return abs(twice) / 2 * FT * FT / 43560


fill = Q["fill_in_basin"] + Q["fill_pad"] + Q["fill_high_ground"]
culvert_names = {"Path A": "Path A culvert", "Path B": "Path B culvert", "Path C": "Path C culvert", "Road": "Pond outlet under the road",
                 "Entry drive": "Entry drive culvert", "Outfall": "Link to the existing outfall"}
GROUPS = [
    ("Site", [
        ("site.parcel_published", "Main parcel, as published by the Property Appraiser", 60.83, "ac", "directed", "SCPA, per the architect"),
        ("site.parcel_measured", "Main parcel, as drawn", SM["site_acres_footprint"], "ac", "measured", "slides/data/site-map.js"),
        ("site.canopy", "Woods on the main parcel", SM["canopy_acres"], "ac", "measured", "slides/data/site-map.js"),
        ("site.pasture_fenced", "Fenced pasture", A["pasture_fenced"], "ac", "measured", CONCEPT),
    ]),
    ("Elevations", [
        ("el.bfe", "Base flood elevation, modelled 100-year", E["bfe"], "ft", "directed", INPUTS),
        ("el.pad", "Raised building pad, BFE + 1'", E["pad"], "ft", "directed", INPUTS),
        ("el.high_ground", "High ground, paths, and top of bank", E["high_ground"], "ft", "assumed", INPUTS),
        ("el.nwl", "Retention pond normal water level", E["nwl"], "ft", "assumed", INPUTS),
        ("el.shelf", "Littoral shelf", E["shelf"], "ft", "assumed", INPUTS),
        ("el.pond_bottom", "Retention pond bottom", E["pond_bottom"], "ft", "assumed", INPUTS),
        ("el.tri_nwl", "North triangle pond normal water level", E["tri_nwl"], "ft", "assumed", INPUTS),
        ("el.tri_bottom", "North triangle pond bottom", E["tri_bottom"], "ft", "assumed", INPUTS),
        ("el.outlet_invert", "Swale invert where the triangle pond discharges", SW["outlet_invert_at_bend"], "ft", "estimate", CONCEPT),
        ("slope.swale", "Typical swale bank, horizontal to 1 vertical", E["swale_side"], ":1", "assumed", INPUTS),
        ("slope.pond", "Pond bank, horizontal to 1 vertical", E["pond_side"], ":1", "assumed", INPUTS),
    ]),
    ("Areas", [
        ("area.open_pasture", "Open pasture", A["open_pasture"], "ac", "measured", CONCEPT),
        ("area.swale_in_open", "Open pasture that becomes swale", A["swale_in_open"], "ac", "estimate", CONCEPT),
        ("area.high_in_open", "Open pasture that stays high ground", A["high_ground_in_open"], "ac", "estimate", CONCEPT),
        ("area.swale_share", "Swale share of open pasture (owner's target: 70%)", round(SW["swale_share_of_open"] * 100), "%", "estimate", CONCEPT),
        ("area.swale_total", "Swale, all areas", A["swale_total"], "ac", "estimate", CONCEPT),
        ("area.pad", "Raised pad", A["pad"], "ac", "estimate", CONCEPT),
        ("area.pad_slopes", "Raised pad with its slopes", A["pad_with_slopes"], "ac", "estimate", CONCEPT),
        ("area.pond", "Retention pond", A["pond"], "ac", "estimate", CONCEPT),
        ("area.tri_pond", "North triangle pond", round(area_ac(SW["tri_pond"]["outer"]), 2), "ac", "estimate", CONCEPT),
        ("area.woods_trimmed", "Woods edge trimmed for the swale", SW["woods_cleared_ac"], "ac", "estimate", CONCEPT),
    ]),
    ("Paths", [(f"path.{p['name'][-1].lower()}", f"{p['name']}: {p['what']}", round(length_ft(p["line"]), -1), "ft", "estimate", CONCEPT) for p in SW["paths"]]),
    ("Culverts", [(f"culvert.{c['name'].lower().replace(' ', '_')}", culvert_names[c["name"]], c["ft"], "ft", "estimate", CONCEPT) for c in SW["culvert_check"]]),
    ("Earthwork", [
        ("earth.cut", "Cut, swales and ponds", Q["cut_swale_and_pond"], "cy", "estimate", CONCEPT),
        ("earth.fill_banks", "Fill, swale banks", Q["fill_in_basin"], "cy", "estimate", CONCEPT),
        ("earth.fill_pad", "Fill, raised pad", Q["fill_pad"], "cy", "estimate", CONCEPT),
        ("earth.fill_high", "Fill, high ground and paths", Q["fill_high_ground"], "cy", "estimate", CONCEPT),
        ("earth.fill_total", "Fill, total", fill, "cy", "estimate", CONCEPT),
        ("earth.import", "Imported fill", -Q["net_cut"], "cy", "estimate", CONCEPT),
        ("earth.storage_lost", "Floodplain storage lost", Q["storage_lost_below_bfe"], "cy", "estimate", CONCEPT),
        ("earth.storage_gained", "Floodplain storage gained", Q["storage_gained_below_bfe"], "cy", "estimate", CONCEPT),
        ("earth.unsurveyed", "Share of the swale with no survey spots", round(SW["survey_gap"]["share_of_swale_unsurveyed"] * 100), "%", "measured", CONCEPT),
    ]),
    ("Pasture capacity", [(f"capacity.level{L['level']}", f"{L['name']} herd, planning figure", L["ce_planning"], "CE", "needs-recheck", "slides/data/pasture-capacity.js") for L in CAP["levels"]]),
]

figures = [{"id": i, "group": g, "label": lab, "value": v, "unit": u, "status": st, "source": src} for g, rows in GROUPS for i, lab, v, u, st, src in rows]
paddocks = [{"paddock_ac": p["acres"], "open_ac": p["open"], "high_ground_pct": p["high_pct"]} for p in SW["by_paddock"]]
json.dump({"note": "Generated by tools/build_report_data.py. Do not edit by hand.", "figures": figures, "paddocks": paddocks},
          open(os.path.join(ROOT, "drawings", "data", "report-data.json"), "w", encoding="utf8"), indent=1)


def show(v, unit):
    text = f"{v:,.0f}" if isinstance(v, (int, float)) and abs(v) >= 1000 else f"{v:g}"
    if unit == "ft" and isinstance(v, float) and abs(v) < 40:
        text = f"{v:.2f}'"
        return text
    return {"ac": f"{text} ac", "%": f"{text}%", ":1": f"{text}:1", "ft": f"{text} ft", "cy": f"{text} cy", "CE": f"{text} CE"}[unit]


out = ["# Figures register", "", "Generated by `tools/build_report_data.py`. Do not edit by hand. Status terms are defined in `report-data-framework.md`.", ""]
for g, rows in GROUPS:
    out += [f"## {g}", "", "| ID | Figure | Value | Status |", "|---|---|---|---|"]
    out += [f"| `{i}` | {lab} | {show(v, u)} | {st} |" for i, lab, v, u, st, _ in rows] + [""]
out += ["## High ground left in each paddock", "", "| Paddock | Open ground | Stays high |", "|---|---|---|"]
out += [f"| {p['paddock_ac']} ac | {p['open_ac']} ac | {p['high_ground_pct']}% |" for p in sorted(paddocks, key=lambda p: -p["paddock_ac"])] + [""]
os.makedirs(os.path.join(ROOT, "docs", "reference"), exist_ok=True)
open(os.path.join(ROOT, "docs", "reference", "figures.md"), "w", encoding="utf8", newline="\n").write("\n".join(out))
print("figures", len(figures), "| statuses", {s: sum(f["status"] == s for f in figures) for s in sorted({f["status"] for f in figures})})
