# Clark Farm – Option B (Level 3) rough watercolor

Procedural pen-and-wash rendering built from the "Barnyard, Level by Level – Option B" site plan.

## Pipeline
1. `scripts/scene.py` – 3D massing in feet, traced from the plan (2.95 px/ft, plan north up).
   Cattle barns A/B, arena + grooming, small animal barns A/B, feed/bedding storage,
   pens 1–5 + chute, 7 existing pens, existing barn (asymmetric gable, 3 roll-up doors, lean-to),
   compost, turnouts, drives. Sun from SSE (az 140°, el 48°).
2. `scripts/render.py` – camera (SW of campus, 30 ft up, looking NNE), painter's-order
   rasterizer → color / region-ID / material / shadow / ink layers (.npy in scratch).
   Usage: `python3 render.py 3000 1800`
3. `scripts/paint.py` – watercolor pass: edge displacement, wet-edge pooling, granulation,
   dry-brush skips, shadow glaze, sky wash with clouds, ragged vignette, sepia ink, paper.
   Usage: `python3 paint.py out.png`
4. `scripts/sprites.py` – student leading Hereford-type steer, background tractor.

Edit the camera line in render.py (`CAM = Camera(...)`) or positions `COW_AT` / `TRACTOR_AT` to recompose.
Requires Python 3, numpy, scipy, Pillow. Scripts expect to live in one folder; update the
path constants (`OUT`, `D`, sys.path) at the top of render.py / paint.py.
