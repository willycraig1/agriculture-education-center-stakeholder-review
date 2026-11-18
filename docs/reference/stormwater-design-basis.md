# Stormwater design basis

How the owner's direction of 2026-11-18 is drawn, and which input controls each part. All inputs are in `tools/stormwater_inputs.py`. Values are in `figures.md`, and the history is in `../log/09-stormwater-concept.md`.

North is to the left on the sheets, so east is up and south is to the right.

## Owner's direction

| # | Direction | How it is drawn | Inputs |
|---|---|---|---|
| 1 | Raise holding pens, new barns, turnout yards, and working spaces to BFE + 1' | One L-shaped pad in the barnyard's grid | `BFE`, `PAD_EL`, `PAD_OUTLINE`, `PAD_TOE` |
| 2 | Tie the retention pond to the historic slough bed | The pond and swale are one graded surface | `NWL`, `SHELF_EL`, `POND_BOTTOM`, `MAIN_FLOOR` |
| 3 | Expand the slough with wide radii, leaving about 30% of open pasture high | Swale along the bed's centerlines, sized to the target | `TARGET_SWALE`, `MAIN`, `BRANCHES`, `RADIUS`, `ARM` |
| 4 | Connect under the road to a similar swale in the north triangle | Triangle swale drains to its own pond, then under the road | `BRANCHES`, `TRI_POND_POINTS`, `TRI_NWL`, `TRI_FLOOR`, `ROAD_CULVERT` |
| 5 | Add high-ground paths to the gates, with culverts as required | Paths A, B, and C at the high-ground elevation | `PATH_W`, `BARN_AXIS`, `PATH_B_POINTS`, `PATH_C_POINTS` |

## Architect's refinements

| Refinement | Inputs |
|---|---|
| Pond holds its designed edge on the east | Geometry in `tools/build_stormwater_concept.py` (`east_zone`) |
| Pond's top of bank stays 10' off the south fence | `SOUTH_FENCE`, `SOUTH_HOLD` |
| Path A runs on the centerline between the cattle barns | `BARN_AXIS` |
| Path A ramps gently down from the pad | `RAMP_LEN`, `RAMP_HW` |
| Swale bottom swings wide of cattle barn B | `BARN_B_BEND` |
| Eased banks at the barn B corner and north of Pen 5 | `SOFT_CIRCLES` |
| Swale arm carried north to Path B | `PATH_B_ARM_LINE`, `PATH_B_ARM_HALF` |
| Path corners rounded where they meet the top of bank | `PATH_FILLET` |

## How the surface is graded

1. The top of bank is the high-ground elevation all the way around.
2. Banks fall at the typical swale slope to a floor that drops gently along the flow toward each pond.
3. A low-flow line follows every centerline, so narrow arms still reach an invert.
4. No swale bank is steeper than 5:1, which keeps the 21' contour clear of the 22' line.
5. Culverts run straight from invert to invert.

## Before changing an input

- **Floodplain storage:** storage gained must stay at or above storage lost. Check `earth.storage_gained` and `earth.storage_lost` after every rebuild.
- **Standing water:** the north triangle's floor must stay above its pond's water level, or the pasture reads as a pond.
- **Drainage:** every swale piece must connect to a pond through a culvert. The build reports any stranded piece in `stranded_swale_ac`.
- **Outlet:** the triangle pond's water level must stay above `el.outlet_invert`.
