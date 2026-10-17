"""Watercolor pass over the layered render."""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, '/tmp/claude-0/-home-claude/b12376d0-599c-5a9c-b5ba-0049f182911a/scratchpad')
D = '/tmp/claude-0/-home-claude/b12376d0-599c-5a9c-b5ba-0049f182911a/scratchpad/'
OUTNAME = sys.argv[1] if len(sys.argv) > 1 else 'paint.png'
col = np.load(D + 'L_col.npy').astype(np.float32) / 255
ids = np.load(D + 'L_id.npy').astype(np.int64)
mat = np.load(D + 'L_mat.npy').astype(np.int32)
shd = np.load(D + 'L_shd.npy').astype(np.float32) / 255
ink = np.load(D + 'L_ink.npy').astype(np.float32) / 255
hy = float(np.load(D + 'L_meta.npy')[0])
H, W = ids.shape
K = W / 3000.0
rng = np.random.default_rng(21)

# material lookup (keep in sync with render.MAT order)
import importlib.util
src = open(D + 'render.py').read()
start = src.index('MAT = {'); end = src.index('}', src.index("'treeline2'")) + 1
ns = {}; exec(src[start:end], ns); MATS = list(ns['MAT'].keys())
MID = {m: i + 1 for i, m in enumerate(MATS)}
def is_mat(names):
    return np.isin(mat, [MID[n] for n in names])

def noise(sigma, amp=1.0, shape=None):
    shape = shape or (H, W)
    n = ndi.gaussian_filter(rng.normal(0, 1, shape).astype(np.float32), sigma * K if sigma * K > 0.6 else 0.6)
    n /= (n.std() + 1e-6)
    return n * amp

# ---------- 1. displacement (fills slip off the pen lines)
dx = noise(30, 3.2 * K) + noise(6, 1.2 * K)
dy = noise(30, 3.2 * K) + noise(6, 1.2 * K)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
cy, cx = yy + dy, xx + dx
def warp(a, order):
    if a.ndim == 3:
        return np.stack([ndi.map_coordinates(a[..., c], [cy, cx], order=order, mode='nearest') for c in range(a.shape[2])], -1)
    return ndi.map_coordinates(a, [cy, cx], order=order, mode='nearest')
col = warp(col, 1); ids = warp(ids, 0); mat = warp(mat, 0)
shd = warp(shd, 1)

# ---------- 2. absorbance
A = -np.log(np.clip(col, 0.03, 1.0))

# sky: graded wash with cloud holes
sky = mat == MID['sky']
t = np.clip(yy / max(hy, 1), 0, 1)
skycol = np.stack([0.50 + 0.40 * t, 0.68 + 0.26 * t, 0.88 + 0.09 * t], -1)
Asky = -np.log(skycol)
cl = noise(160, 1.0) + 0.45 * noise(55, 1.0) + 0.12 * noise(14, 1.0)
cl = cl + 1.6 * (yy / max(hy, 1) - 0.55)
cloudmask = np.clip((cl - 0.2) / 0.55, 0, 1) ** 1.3
cloudmask = np.maximum(cloudmask, np.clip((0.12 - yy / H) / 0.12, 0, 1))  # top fades to paper
cloudmask *= np.clip((hy - yy) / (60 * K), 0, 1)
Asky *= (1 - 0.92 * cloudmask)[..., None]
# soft grey cloud bellies
belly = np.clip((cl - 0.6) / 0.6, 0, 1) * cloudmask
Asky += belly[..., None] * np.array([0.05, 0.05, 0.03])
A = np.where(sky[..., None], Asky, A)

# ---------- 3. pigment density variation + granulation
low = noise(70, 1.0); mid = noise(18, 1.0); hf = noise(0.9, 1.0)
A *= (1.0 + 0.16 * low + 0.10 * mid)[..., None]
gran = np.full((H, W), 0.10, np.float32)
gran[is_mat(['dirt', 'arenadirt', 'asphalt', 'concrete'])] = 0.22
gran[is_mat(['oldwood', 'rustroof', 'oldtimber'])] = 0.14
gran[is_mat(['grass', 'grass2', 'grasspark', 'turnout'])] = 0.16
A *= (1.0 + gran * hf)[..., None]

# rust streaks on the existing barn roof
rust = is_mat(['rustroof'])
rs = np.clip(noise(4, 1.0) * 0.6 + ndi.gaussian_filter(rng.normal(0, 1, (H, W)).astype(np.float32), (1.0, 6 * K)) * 2.0, 0, None)
A[rust] += (rs[rust, None] * np.array([0.02, 0.06, 0.12]) + np.array([0.0, 0.03, 0.08]))

# grass: mottled warm/cool variation
grass = is_mat(['grass', 'grass2', 'grasspark', 'turnout'])
gv = noise(45, 1.0)
A[grass] += (gv[grass, None] * np.array([0.06, 0.02, 0.08]))

# ---------- 4. paper-white highlights (dry brush skips) on light surfaces
hl = is_mat(['roof', 'whitemetal', 'roofflat', 'concrete', 'doorwhite', 'car_white', 'cow_white'])
sk = ndi.gaussian_filter(rng.normal(0, 1, (H, W)).astype(np.float32), (1.2 * K + 0.5, 9 * K + 1))
sk /= sk.std()
skip = (sk + 0.6 * noise(25, 1.0)) > 1.7
A[hl & skip] *= 0.35
# lighten roofs overall (glare) toward paper
A[is_mat(['roof'])] *= 0.75

# ---------- 5. wet edges: pigment pools at region boundaries
b = np.zeros((H, W), bool)
b[:, 1:] |= ids[:, 1:] != ids[:, :-1]
b[1:, :] |= ids[1:, :] != ids[:-1, :]
e = ndi.gaussian_filter(b.astype(np.float32), 1.6 * K + 0.5)
e = np.clip(e / (e.max() * 0.5 + 1e-6), 0, 1)
A *= (1 + 0.45 * e)[..., None]

# ---------- 6. shadow glaze (separate transparent violet-blue wash)
s = ndi.gaussian_filter(shd, 1.0 * K + 0.4)
sb = np.abs(ndi.sobel(s, 0)) + np.abs(ndi.sobel(s, 1))
sb = np.clip(ndi.gaussian_filter(sb, 1.5) * 0.8, 0, 1)
Ash = -np.log(np.array([0.70, 0.70, 0.84]))
A += (s * (0.9 + 0.2 * mid) + 0.25 * sb)[..., None] * Ash[None, None, :] * (1 + 0.15 * hf)[..., None]

# ---------- 7. vignette: loose ragged edge fading to paper
u = (xx / W - 0.5) * 2; v = (yy / H - 0.47) * 2
r = np.sqrt((u * 0.92) ** 2 + (v * 1.0) ** 2)
rag = noise(70, 0.07) + noise(22, 0.025)
vm = np.clip((1.16 - r + rag) / 0.14, 0, 1)
vm *= np.clip((1.0 - (yy / H) + rag) / 0.16, 0, 1)
# foreground lawn gets a lighter, looser wash
fg = np.clip(((yy / H) - 0.68) / 0.3, 0, 1)
A[grass] *= (1 - 0.45 * fg[grass] * (0.7 + 0.3 * low[grass]))[..., None]
# keep foreground figures fully painted
figs = is_mat(['cow_body', 'cow_dark', 'cow_white', 'jeans', 'jeans_dark', 'shirt', 'shirt_dark', 'skin', 'boot', 'cap', 'hair', 'hoof', 'cow_nose', 'belt'])
fd = ndi.binary_dilation(figs, iterations=int(40 * K) + 1)
vm = np.maximum(vm, np.clip(ndi.gaussian_filter(fd.astype(np.float32), 22 * K) * 1.6, 0, 1) * 0.9)
vm = np.maximum(vm, figs.astype(np.float32))
vedge = np.clip(1 - np.abs(vm - 0.5) * 2, 0, 1)
A *= vm[..., None]
A *= (1 + 0.5 * vedge)[..., None]

paint = np.exp(-A)

# ---------- 8. ink (sepia), slightly broken
inkv = ink * np.clip(0.8 + 0.35 * noise(1.2, 1.0), 0.3, 1.1)
inkv *= np.clip(vm * 1.4, 0, 1)  # lines vanish where paint fades
inkc = np.array([0.20, 0.16, 0.13])
out = paint * (1 - inkv[..., None]) + inkc * inkv[..., None] * paint

# ---------- 9. paper
paper = 0.5 * noise(0.8, 1.0) + 0.5 * noise(3, 1.0)
pap = ndi.sobel(paper, 0) * 0.5 + ndi.sobel(paper, 1) * 0.5
out *= (np.array([0.995, 0.985, 0.955]) * (1 + 0.012 * pap)[..., None])
out = np.clip(out, 0, 1)
Image.fromarray((out * 255).astype(np.uint8)).save(D + OUTNAME)
print('saved', OUTNAME, W, H)
