"""Register the 1948 aerial to the map.

source/1948 Aerial of historic Slough Bed.jpg and the current County aerial are screenshots of the same web map
(north up, parcel lines drawn in yellow), so they differ only by a zoom and a shift. The zoom and shift are found
by sliding the 1948 image's yellow parcel lines over the current aerial's at a range of zooms and keeping the best
match. Chained with the current aerial's registration to the property lines (register_aerial.py), that places the
1948 image on the map. Writes "aerial_1948" into tools/registration.json.

The County's own placement of the 1948 photo under its parcel lines is approximate; treat positions read from
it as good to a few tens of feet.

Run:  python tools/register_aerial_1948.py   (needs numpy, scipy, pillow)
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage, signal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from siteframe import SRC, AERIAL, reg

OLD = os.path.join(SRC, "1948 Aerial of historic Slough Bed.jpg")

def yellow(im):
    a = np.asarray(im.convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return ((r > 200) & (g > 150) & (g < 215) & (b < 120) & (r - b > 90)).astype(np.float32)

A, B = Image.open(AERIAL), Image.open(OLD)
ma, mb_full = ndimage.gaussian_filter(yellow(A), 1.0), Image.fromarray((yellow(B) * 255).astype(np.uint8))

def match(f):
    w, h = int(round(B.size[0] * f)), int(round(B.size[1] * f))
    mb = ndimage.gaussian_filter(np.asarray(mb_full.resize((w, h), Image.BILINEAR)).astype(np.float32) / 255, 1.0)
    c = signal.fftconvolve(ma, mb[::-1, ::-1], mode="full")
    k = np.unravel_index(c.argmax(), c.shape)
    return float(c.max() / np.sqrt((mb ** 2).sum())), f, int(k[1] - (w - 1)), int(k[0] - (h - 1))

coarse = max(match(f) for f in np.arange(0.25, 1.26, 0.025))
score, f, dx, dy = max(match(f) for f in np.arange(coarse[1] - 0.02, coarse[1] + 0.0201, 0.0025))
(a, c, e), (b, d, g) = reg["map_to_aerial_affine"]["aerial_to_map"]
# 1948 pixel -> current aerial pixel (zoom f, shift dx, dy) -> map
m = [[a * f, c * f, a * dx + c * dy + e], [b * f, d * f, b * dx + d * dy + g]]
R = json.load(open(os.path.join(HERE, "registration.json")))
R["aerial_1948"] = {"source": os.path.basename(OLD), "image_size": list(B.size), "to_current_aerial": {"zoom": round(float(f), 4), "shift_px": [dx, dy], "match_score": round(score, 1), "next_best_zoom_score": round(coarse[0], 1)},
                    "to_map": [[round(v, 8) for v in row] for row in m]}
json.dump(R, open(os.path.join(HERE, "registration.json"), "w"), indent=2)
print("1948 aerial: zoom", round(float(f), 4), "shift", (dx, dy), "score", round(score, 1))
