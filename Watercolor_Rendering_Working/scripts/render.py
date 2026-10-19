import sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
sys.path.insert(0, '/tmp/claude-0/-home-claude/b12376d0-599c-5a9c-b5ba-0049f182911a/scratchpad')
import scene, sprites
from cam import Camera

OUT = '/tmp/claude-0/-home-claude/b12376d0-599c-5a9c-b5ba-0049f182911a/scratchpad/'
W, H = int(sys.argv[1]) if len(sys.argv) > 1 else 1500, int(sys.argv[2]) if len(sys.argv) > 2 else 900
K = W / 3000.0  # scale factor for pixel-size constants
rng = np.random.default_rng(3)

CAM = Camera(pos=(188, -445, 30), target=(250, -205, -4), W=W, H=H, hfov_deg=72)

MAT = {
    'roof': (0.86, 0.88, 0.90), 'roofflat': (0.86, 0.87, 0.87), 'whitemetal': (0.97, 0.96, 0.93),
    'openshade': (0.44, 0.40, 0.40), 'cladding': (0.62, 0.24, 0.20), 'timber': (0.82, 0.64, 0.40), 'joist': (0.13, 0.13, 0.14), 'roofunder': (0.80, 0.70, 0.55), 'curtain': (0.86, 0.89, 0.91), 'alum': (0.80, 0.81, 0.82), 'trussend': (0.52, 0.47, 0.44),
    'oldwood': (0.78, 0.71, 0.62), 'oldtimber': (0.55, 0.47, 0.38), 'rustroof': (0.82, 0.79, 0.75),
    'doorwhite': (0.96, 0.96, 0.94), 'darkglass': (0.28, 0.30, 0.33), 'concrete_w': (0.84, 0.82, 0.78),
    'dumpster': (0.36, 0.48, 0.42), 'car_white': (0.96, 0.96, 0.95), 'car_silver': (0.76, 0.78, 0.81),
    'car_red': (0.74, 0.25, 0.20), 'car_blue': (0.30, 0.42, 0.66), 'car_dark': (0.30, 0.31, 0.33),
    'carglass': (0.36, 0.40, 0.46),
    'grass': (0.62, 0.72, 0.42), 'grass2': (0.66, 0.75, 0.45), 'turnout': (0.70, 0.76, 0.48), 'grasspark': (0.66, 0.74, 0.45),
    'asphalt': (0.74, 0.73, 0.71), 'concrete': (0.88, 0.86, 0.82), 'dirt': (0.83, 0.73, 0.57),
    'arenadirt': (0.84, 0.74, 0.58),
    'pipe': (0.28, 0.29, 0.31), 'board': (0.50, 0.40, 0.30), 'oldboard': (0.48, 0.42, 0.36),
    'boardline': (0.45, 0.39, 0.33),
    'cow_body': (0.62, 0.33, 0.20), 'cow_dark': (0.45, 0.24, 0.15), 'cow_white': (0.95, 0.92, 0.86),
    'cow_nose': (0.80, 0.62, 0.58), 'hoof': (0.25, 0.22, 0.20), 'halter': (0.15, 0.15, 0.18),
    'jeans': (0.40, 0.50, 0.66), 'jeans_dark': (0.30, 0.38, 0.52), 'boot': (0.42, 0.30, 0.20),
    'shirt': (0.30, 0.42, 0.62), 'shirt_dark': (0.22, 0.30, 0.46), 'belt': (0.30, 0.22, 0.15),
    'skin': (0.86, 0.68, 0.54), 'hair': (0.40, 0.28, 0.18), 'cap': (0.88, 0.80, 0.62),
    'tire': (0.22, 0.22, 0.23), 'rim': (0.90, 0.84, 0.66), 'tractor': (0.78, 0.33, 0.19), 'seat': (0.20, 0.20, 0.20),
    'rope': (0.55, 0.45, 0.30),
    'sky': (0.6, 0.75, 0.9),
    'oak_d': (0.24, 0.33, 0.22), 'oak_m': (0.38, 0.50, 0.28), 'oak_l': (0.58, 0.68, 0.36),
    'pine_d': (0.26, 0.36, 0.26), 'pine_l': (0.45, 0.56, 0.32), 'trunk': (0.38, 0.32, 0.27),
    'palm_d': (0.33, 0.45, 0.28), 'palm_l': (0.55, 0.64, 0.35), 'treeline': (0.50, 0.60, 0.52),
    'treeline2': (0.40, 0.50, 0.40),
}
MATS = list(MAT.keys()); MID = {m: i + 1 for i, m in enumerate(MATS)}
WHITE_MATS = {'roof', 'whitemetal', 'doorwhite', 'concrete', 'roofflat', 'car_white', 'cow_white'}

# --- canvases
col = Image.new('RGB', (W, H), (255, 255, 255)); dcol = ImageDraw.Draw(col)
ids = Image.new('I', (W, H), 0); did = ImageDraw.Draw(ids)
mat = Image.new('L', (W, H), 0); dmat = ImageDraw.Draw(mat)
SS = 2  # ink supersample
ink = Image.new('L', (W * SS, H * SS), 0); dink = ImageDraw.Draw(ink)
shd = Image.new('L', (W, H), 0); dshd = ImageDraw.Draw(shd)
NID = [1]

def c255(c): return tuple(int(max(0, min(1, v)) * 255) for v in c)

def shade_color(base, lit, mname):
    base = np.array(base)
    if mname in ('openshade', 'darkglass', 'trussend'):
        return base
    k = 0.62 + 0.38 * lit
    cool = np.array([0.93, 0.95, 1.05])
    c = base * k * (cool if lit < 0.35 else 1.0)
    return np.clip(c, 0, 1)

def fill(pts2, mname, color=None, erase_ink=True, erase_shadow=True, keep_id=None):
    pts = [tuple(p) for p in np.asarray(pts2)]
    if len(pts) < 3: return
    c = MAT[mname] if color is None else color
    dcol.polygon(pts, fill=c255(c))
    i = NID[0] if keep_id is None else keep_id
    if keep_id is None: NID[0] += 1
    did.polygon(pts, fill=i)
    dmat.polygon(pts, fill=MID[mname])
    if erase_ink: dink.polygon([(x * SS, y * SS) for x, y in pts], fill=0)
    if erase_shadow: dshd.polygon(pts, fill=0)
    return i

def wobble_line(p, q, width, val=255, overshoot=True, jit=0.6):
    p = np.array(p, float); q = np.array(q, float)
    d = q - p; L = np.hypot(*d)
    if L < 0.5: return
    u = d / L; n = np.array([-u[1], u[0]])
    os_ = (rng.uniform(1, 5) * K if overshoot else 0)
    p2 = p - u * os_ * rng.uniform(0.3, 1); q2 = q + u * os_ * rng.uniform(0.3, 1.2)
    k = max(2, int(L / (40 * K)))
    ts = np.linspace(0, 1, k + 1)
    off = np.cumsum(rng.normal(0, jit * K, k + 1)); off -= np.linspace(off[0], off[-1], k + 1)
    pts = [tuple(((p2 + (q2 - p2) * t) + n * o) * SS) for t, o in zip(ts, off)]
    dink.line(pts, fill=val, width=max(1, int(round(width * SS))))

def outline(pts2, width, val=230):
    n = len(pts2)
    for i in range(n):
        wobble_line(pts2[i], pts2[(i + 1) % n], width, val)

def ink_w(dist):
    return float(np.clip(3.2 * K * 120.0 / max(dist, 40), 0.8 * K * 1.4, 3.6 * K))

# ---------------- build draw list
objs = scene.build()
items = []  # (dist, kind, payload)
campos = CAM.pos
for o in objs:
    P = o.allpts()
    if len(P) == 0: continue
    c = P.mean(0)
    if o.ground:
        items.append((1e9, 'ground', o)); continue
    # nearest-ish distance: centroid distance minus a bit of size for big objects
    d = np.hypot(*(c[:2] - campos[:2]))
    items.append((d, 'obj', o))

# trees
def tree_shapes(x, y, kind, s):
    return dict(x=x, y=y, kind=kind, s=s)
for (x, y, kind, s) in scene.trees():
    items.append((np.hypot(x - campos[0], y - campos[1]), 'tree', tree_shapes(x, y, kind, s)))
# background oak rows (beyond site)
for i in range(150):
    side = rng.choice(['n', 'w', 'e'], p=[0.55, 0.2, 0.25])
    if side == 'n': x, y = rng.uniform(-250, 750), rng.uniform(20, 420)
    elif side == 'w': x, y = rng.uniform(-200, -20), rng.uniform(-420, 30)
    else: x, y = rng.uniform(490, 700), rng.uniform(-420, 30)
    kind = 'oak' if rng.random() < 0.8 else 'pine'
    items.append((np.hypot(x - campos[0], y - campos[1]), 'tree', tree_shapes(x, y, kind, rng.uniform(0.9, 1.4))))

# figures
COW_AT = np.array([210.0, -394.0])  # ground point of cow's front hooves
items.append((np.hypot(*(COW_AT - campos[:2])) + 1.0, 'cow', COW_AT))
items.append((np.hypot(*(COW_AT - campos[:2])) - 1.0, 'student', COW_AT))
TRACTOR_AT = np.array([425.0, -98.0])
items.append((np.hypot(*(TRACTOR_AT - campos[:2])), 'tractor', TRACTOR_AT))

items.sort(key=lambda t: -t[0])

# ---------------- sky + ground base
hy = CAM.horizon_y()
fill([(0, 0), (W, 0), (W, hy + 2), (0, hy + 2)], 'sky', erase_ink=False)
fill([(0, hy + 1), (W, hy + 1), (W, H), (0, H)], 'grass', erase_ink=False)
# distant tree line band along horizon (two layers)
for layer, (mname, hmax, off) in enumerate([('treeline', 26, 0), ('treeline2', 16, 5)]):
    xs = np.linspace(-20, W + 20, 420)
    nz = ndi.gaussian_filter1d(rng.normal(0, 1, len(xs)), 1.6)
    nz2 = ndi.gaussian_filter1d(rng.normal(0, 1, len(xs)), 0.8)
    top = hy + 3 * K - (hmax * K * (0.65 + 0.35 * nz / (np.abs(nz).max() + 1e-6)) + 6 * K * nz2) + off * K
    pts = [(xs[0], hy + 8 * K)] + list(zip(xs, top)) + [(xs[-1], hy + 8 * K)]
    fill(pts, mname, erase_ink=False)

# ---------------- shadows (cast from objects & trees) drawn before objects
sx, sy, sz = scene.SUN
def ground_shadow_of(P):
    Q = P[:, :2] - P[:, 2:3] * np.array([sx, sy]) / sz
    Q = np.vstack([Q, P[P[:, 2] < 0.5][:, :2]]) if np.any(P[:, 2] < 0.5) else Q
    # convex hull (monotone chain)
    pts = sorted(map(tuple, np.round(Q, 3)))
    if len(pts) < 3: return None
    def cross(o, a, b): return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0: lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0: up.pop()
        up.append(p)
    return np.array(lo[:-1] + up[:-1])

def draw_shadow_poly(xy):
    P = np.c_[xy, np.zeros(len(xy))]
    sp, _ = CAM.clip_poly(P)
    if sp is not None and len(sp) >= 3:
        dshd.polygon([tuple(p) for p in sp], fill=255)

def draw_ground_items():
    for d, kind, o in items:
        if kind == 'ground':
            for f in o.faces:
                sp, _ = CAM.clip_poly(f['p'])
                if sp is not None and len(sp) >= 3:
                    fill(sp, f['mat'], erase_ink=False)
    # parking stripes / drive edge lines (light ink)
    for x in np.arange(168.5, 300, 9.5):
        for (ya, yb) in [(-254, -270), (-292, -308), (-323, -339)]:
            a = CAM.proj(np.array([[x, ya, 0], [x, yb, 0]]))
            wobble_line(a[0], a[1], 0.8 * K, 90, overshoot=False)

# mowing stripes on the foreground lawn
for x0 in np.arange(170, 302, 14):
    P = np.array([(x0, -560, 0), (x0 + 7, -560, 0), (x0 + 7, -342, 0), (x0, -342, 0)], float)
    sp, _ = CAM.clip_poly(P)
    if sp is not None and len(sp) >= 3: fill(sp, 'grass2', erase_ink=False)
draw_ground_items()

# shadows of objects
for d, kind, o in items:
    if kind == 'obj' and o.cast:
        for f in o.faces:  # per-face shadow hull keeps concave shapes reasonable
            if f['p'][:, 2].max() < 0.3: continue
            h = ground_shadow_of(f['p'])
            if h is not None: draw_shadow_poly(h)
    elif kind == 'tree':
        t = o; s = t['s']
        hc = {'oak': 26, 'pine': 50, 'palm': 22}[t['kind']] * s
        rr = {'oak': 22, 'pine': 9, 'palm': 7}[t['kind']] * s
        cx, cy = t['x'] - hc * sx / sz, t['y'] - hc * sy / sz
        ang = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        rad = rr * (1 + 0.15 * rng.normal(size=24))
        draw_shadow_poly(np.c_[cx + rad * np.cos(ang) * 1.1, cy + rad * np.sin(ang) * 0.8])
        draw_shadow_poly(np.array([[t['x'] - 0.8, t['y']], [t['x'] + 0.8, t['y']], [cx + 0.8, cy], [cx - 0.8, cy]]))
    elif kind in ('cow', 'student'):
        pass

# figure shadows
def fig_shadow(at, length, h, w):
    base = np.array([at[0], at[1]])
    tip = base - h * np.array([sx, sy]) / sz
    q = np.array([base + [-w / 2, 0.0], base + [length + w / 2, 0.0], tip + [length + w / 2, 0], tip + [-w / 2, 0]])
    draw_shadow_poly(q)
fig_shadow(COW_AT + [0, 0.5], 7, 4.2, 1.5)
fig_shadow(COW_AT + [-2.7, 1.2], 1.4, 5.4, 0.8)
fig_shadow(TRACTOR_AT, 10, 6, 2)
# shadows from oaks just outside the frame (dappled foreground shade)
for (tx, ty, rr) in [(150, -452, 24), (300, -470, 20)]:
    for k in range(5):
        ang = np.linspace(0, 2 * np.pi, 30, endpoint=False)
        cx_, cy_ = tx + rng.normal(0, rr * 0.35), ty + rng.normal(0, rr * 0.3)
        rad = rr * rng.uniform(0.4, 0.7) * (1 + 0.18 * ndi.gaussian_filter1d(rng.normal(size=30), 1.5, mode='wrap'))
        draw_shadow_poly(np.c_[cx_ + rad * np.cos(ang) * 1.2, cy_ + rad * np.sin(ang) * 0.8])

# ---------------- objects
def face_visible(f, ocen):
    p = f['p']
    a, b, c = p[0], p[1], p[2]
    n = np.cross(b - a, c - a)
    if np.linalg.norm(n) < 1e-9:
        n = np.cross(p[2] - p[0], p[-1] - p[0])
    nn = np.linalg.norm(n)
    if nn < 1e-9: return False, 0, None
    n = n / nn
    g = f['g'] if f['g'] is not None else ocen
    fc = p.mean(0)
    if np.dot(n, fc - g) < 0: n = -n
    if abs(n[2]) > 0.99 and n[2] < 0: n = -n
    vis = np.dot(n, campos - fc) > 0
    lit = max(0.0, float(np.dot(n, scene.SUN)))
    return vis, lit, n

def draw_obj(o):
    P = o.allpts(); ocen = P.mean(0)
    # interior "ground" centroid lower for culling of open walls
    fs = []
    for f in o.faces:
        vis, lit, n = face_visible(f, ocen)
        if not vis: continue
        fs.append((np.linalg.norm(f['p'].mean(0) - campos) + f['bias'], f, lit))
    # lines also sorted by depth
    ls = [(np.linalg.norm(l['p'].mean(0) - campos) + l['bias'], None, l) for l in o.lines]
    allp = sorted(fs + ls, key=lambda t: -t[0])
    for d, f, x in allp:
        if f is not None:
            sp, _ = CAM.clip_poly(f['p'])
            if sp is None or len(sp) < 3: continue
            c = shade_color(MAT[f['mat']], x, f['mat'])
            fill(sp, f['mat'], color=c)
            if f['ink']:
                outline(sp, ink_w(d), 235)
        else:
            l = x
            sp, _ = CAM.clip_poly(l['p']) if len(l['p']) > 2 else (CAM.proj(l['p']) if CAM.cam(l['p'])[:, 2].min() > 2 else None, None)
            if sp is None: continue
            w = max(0.7 * K * 1.4, l['w'] * ink_w(d) * 0.9)
            m = l['mat']
            v = {'pipe': 210, 'board': 170, 'oldboard': 170, 'boardline': 120}.get(m, 200)
            for i in range(len(sp) - 1):
                wobble_line(sp[i], sp[i + 1], w, v, overshoot=False, jit=0.3)

def noisy_blob(cx, cy, r, n=40, rough=0.12, sy=1.0):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    nz = ndi.gaussian_filter1d(rng.normal(0, 1, n), 1.5, mode='wrap')
    nz /= (np.abs(nz).max() + 1e-6)
    rr = r * (1 + rough * nz + 0.05 * rng.normal(size=n))
    return np.stack([cx + rr * np.cos(t), cy - rr * np.sin(t) * sy], 1)

def draw_tree(t):
    base = np.array([t['x'], t['y'], 0.0])
    if CAM.cam(base)[0, 2] < 5: return
    sc = CAM.scale_at(base); bx, by = CAM.proj(base)[0]
    s = t['s']; kind = t['kind']
    if kind == 'oak':
        Hc, Wc = 34 * s, 50 * s
        # trunk + limbs
        tr = [(bx - 1.2 * sc, by), (bx + 1.2 * sc, by), (bx + 0.7 * sc, by - 12 * s * sc), (bx - 0.8 * sc, by - 12 * s * sc)]
        fill(tr, 'trunk')
        for ang in (-0.9, -0.3, 0.5, 1.0):
            L = rng.uniform(9, 14) * s * sc
            ex = bx + np.sin(ang) * L; ey = by - 11 * s * sc - np.cos(ang) * L * 0.7
            fill([(bx - 0.5 * sc, by - 10 * s * sc), (bx + 0.5 * sc, by - 10 * s * sc), (ex + 0.3 * sc, ey), (ex - 0.3 * sc, ey)], 'trunk')
        nl = rng.integers(6, 10)
        lobes = []
        for i in range(nl):
            a = rng.uniform(0, 2 * np.pi); rr = np.sqrt(rng.uniform(0.1, 1))
            lx = bx + np.cos(a) * rr * Wc * 0.36 * sc
            ly = by - (Hc * 0.62 + np.sin(a) * rr * Hc * 0.22) * sc
            lr = rng.uniform(0.32, 0.45) * Hc * 0.55 * sc
            lobes.append((lx, ly, lr))
        lobes.sort(key=lambda l: l[1])
        for lx, ly, lr in lobes:
            fill(noisy_blob(lx, ly + lr * 0.12, lr, sy=0.85), 'oak_d')
        for lx, ly, lr in lobes:
            fill(noisy_blob(lx + lr * 0.06, ly - lr * 0.1, lr * 0.82, sy=0.8), 'oak_m')
        for lx, ly, lr in lobes[: max(2, nl // 2)]:
            fill(noisy_blob(lx + lr * 0.18, ly - lr * 0.28, lr * 0.5, rough=0.2, sy=0.75), 'oak_l')
        # a few spanish-moss / branch scribbles
        for lx, ly, lr in lobes[-3:]:
            for k in range(3):
                x0 = lx + rng.uniform(-0.6, 0.6) * lr
                wobble_line((x0, ly + lr * 0.55), (x0 + rng.uniform(-2, 2) * K, ly + lr * (0.75 + rng.uniform(0, 0.25))), 0.9 * K, 110, False, 0.3)
    elif kind == 'pine':
        Ht = 58 * s
        fill([(bx - 0.6 * sc, by), (bx + 0.6 * sc, by), (bx + 0.3 * sc, by - Ht * sc), (bx - 0.3 * sc, by - Ht * sc)], 'trunk')
        cl = []
        for i in range(rng.integers(3, 6)):
            hh = rng.uniform(0.68, 1.0) * Ht; dx = rng.uniform(-9, 9) * s
            cl.append((bx + dx * sc, by - hh * sc, rng.uniform(4, 7) * s * sc))
            fill([(bx, by - (hh - 3) * sc), (bx + 0.2 * sc, by - (hh - 3) * sc), (bx + dx * sc, by - hh * sc + 1)], 'trunk')
        for x, y, r in cl:
            fill(noisy_blob(x, y, r * 1.5, rough=0.25, sy=0.45), 'pine_d')
            fill(noisy_blob(x + r * 0.25, y - r * 0.25, r * 0.9, rough=0.3, sy=0.4), 'pine_l')
    elif kind == 'palm':
        Ht = 22 * s
        lean = rng.uniform(-2, 2) * s
        tx, ty = bx + lean * sc, by - Ht * sc
        fill([(bx - 0.7 * sc, by), (bx + 0.7 * sc, by), (tx + 0.6 * sc, ty), (tx - 0.6 * sc, ty)], 'trunk')
        for i in range(16):
            a = np.pi * (i / 15.0) * 1.15 - 0.075 * np.pi + rng.normal(0, 0.08)
            L = rng.uniform(6, 9) * s * sc
            ex, ey = tx + np.cos(a) * L, ty - np.sin(a) * L * 0.75 + L * 0.25
            nx, ny = -np.sin(a) * L * 0.18, -np.cos(a) * L * 0.18
            fill([(tx, ty), (ex + nx, ey + ny), (ex - nx * 0.3, ey - ny * 0.3)], 'palm_d' if i % 3 else 'palm_l')

def place_sprite(at, polys, lines=(), flip=False, ink_on=True, z_ft=0.0):
    base = np.array([at[0], at[1], 0.0])
    sc = CAM.scale_at(base); bx, by = CAM.proj(base)[0]
    sgn = -1 if flip else 1
    def T(pts):
        pts = np.asarray(pts, float)
        return np.stack([bx + sgn * pts[:, 0] * sc, by - pts[:, 1] * sc], 1)
    for pts, m, has_ink in polys:
        sp = T(pts)
        fill(sp, m)
        if has_ink and ink_on:
            n = len(sp)
            dink.line([tuple(p * SS) for p in sp] + [tuple(sp[0] * SS)], fill=200, width=max(1, int(1.6 * K * SS * min(1.6, sc / 8))))
    for pts, m, wft in lines:
        sp = T(pts)
        dcol.line([tuple(p) for p in sp], fill=c255(MAT[m]), width=max(1, int(wft * sc)))
        dmat.line([tuple(p) for p in sp], fill=MID[m], width=max(1, int(wft * sc)))
        did.line([tuple(p) for p in sp], fill=NID[0], width=max(1, int(wft * sc))); NID[0] += 1
        dink.line([tuple(p * SS) for p in sp], fill=180, width=max(1, int(wft * sc * SS * 0.6)))
    return T

for d, kind, o in items:
    if kind == 'obj': draw_obj(o)
    elif kind == 'tree': draw_tree(o)
    elif kind == 'cow':
        place_sprite(o, sprites.cow(), sprites.cow_lines())
        place_sprite(o, sprites.tail_tuft())
    elif kind == 'student':
        sat = o + np.array([-2.75, 0.9])
        T = place_sprite(sat, sprites.student())
        # lead rope from hand to halter (sagging curve), in cow frame
        hand = T(sprites.student_hand()[None])[0]
        sc = CAM.scale_at(np.array([o[0], o[1], 0])); bx, by = CAM.proj(np.array([o[0], o[1], 0]))[0]
        hal = np.array([bx + (-0.55) * sc, by - 2.95 * sc])
        ts = np.linspace(0, 1, 20)
        pts = [(hand[0] + (hal[0] - hand[0]) * t, hand[1] + (hal[1] - hand[1]) * t + np.sin(np.pi * t) * 0.35 * sc) for t in ts]
        dink.line([(x * SS, y * SS) for x, y in pts], fill=230, width=max(1, int(0.09 * sc * SS)))
    elif kind == 'tractor':
        place_sprite(o, sprites.tractor(), sprites.tractor_lines())

np.save(OUT + 'L_col.npy', np.asarray(col)); np.save(OUT + 'L_id.npy', np.asarray(ids))
np.save(OUT + 'L_mat.npy', np.asarray(mat)); np.save(OUT + 'L_shd.npy', np.asarray(shd))
inkd = ink.resize((W, H), Image.LANCZOS); np.save(OUT + 'L_ink.npy', np.asarray(inkd))
np.save(OUT + 'L_meta.npy', np.array([hy]))
# flat preview
prev = np.asarray(col).astype(float) / 255
prev = prev * (1 - 0.35 * (np.asarray(shd)[..., None] / 255.0))
prev = prev * (1 - 0.85 * np.asarray(inkd)[..., None] / 255.0)
Image.fromarray((prev * 255).astype(np.uint8)).save(OUT + 'flat.png')
print('ok', W, H, 'horizon', hy, 'ids', NID[0])
