"""3D massing of MMS Ag Farm Option B (Level 3) built from the site plan.
Units: feet. X east, Y north, Z up. Plan px -> ft: X = px/2.95, Y = -py/2.95
"""
import numpy as np

S = 2.95
def R(px1, py1, px2, py2):
    return (px1 / S, -py2 / S, px2 / S, -py1 / S)  # x1,y1,x2,y2 with y1<y2

# sun: direction TO the sun (from SSE, fairly high)
_az = np.radians(140.0)  # clockwise from north
_el = np.radians(48.0)
SUN = np.array([np.sin(_az) * np.cos(_el), np.cos(_az) * np.cos(_el), np.sin(_el)])

class Obj:
    """A depth-sortable object: list of faces (pts Nx3, mat) and lines (pts, mat, width)."""
    def __init__(self, name, cast_shadow=True, ground=False, key=None):
        self.name = name; self.faces = []; self.lines = []; self.cast = cast_shadow
        self.ground = ground; self.key = key; self.sprites = []
    bias = 0.0  # set temporarily by builders: added to sort distance (negative = drawn later)
    def face(self, pts, mat, ink=True, two_sided=False, g=None):
        self.faces.append(dict(p=np.array(pts, float), mat=mat, ink=ink, two=two_sided,
                               g=None if g is None else np.array(g, float), bias=self.bias))
    def line(self, pts, mat='ink', w=1.0):
        self.lines.append(dict(p=np.array(pts, float), mat=mat, w=w, bias=self.bias))
    def allpts(self):
        ps = [f['p'] for f in self.faces] + [l['p'] for l in self.lines]
        return np.vstack(ps) if ps else np.zeros((0, 3))

def quad(a, b, c, d):
    return [a, b, c, d]

# ---------- builders ----------
def box(o, x1, y1, x2, y2, z0, z1, wall, roof=None, ink=True):
    c = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    g = ((x1 + x2) / 2, (y1 + y2) / 2, (z0 + z1) / 2)
    for i in range(4):
        (ax, ay), (bx, by) = c[i], c[(i + 1) % 4]
        o.face([(ax, ay, z0), (bx, by, z0), (bx, by, z1), (ax, ay, z1)], wall, ink, g=g)
    if roof:
        o.face([(x1, y1, z1), (x2, y1, z1), (x2, y2, z1), (x1, y2, z1)], roof, ink, g=g)

def gable(o, x1, y1, x2, y2, eave, ridge, axis, wall, roof, end_wall=None, ovh=1.5,
          walls=True, ridge_off=0.0, eave2=None):
    """Gable building. axis='x': ridge runs E-W. ridge_off shifts ridge across the span."""
    end_wall = end_wall or wall
    eave2 = eave if eave2 is None else eave2
    if axis == 'x':
        ym = (y1 + y2) / 2 + ridge_off
        # walls: south (y1, eave2), north (y2, eave)
        if walls:
            o.face([(x1, y1, 0), (x2, y1, 0), (x2, y1, eave2), (x1, y1, eave2)], wall)
            o.face([(x2, y2, 0), (x1, y2, 0), (x1, y2, eave), (x2, y2, eave)], wall)
            o.face([(x1, y2, 0), (x1, y1, 0), (x1, y1, eave2), (x1, ym, ridge), (x1, y2, eave)], end_wall)
            o.face([(x2, y1, 0), (x2, y2, 0), (x2, y2, eave), (x2, ym, ridge), (x2, y1, eave2)], end_wall)
        # roofs with overhang (extend along slope)
        ds = ym - y1; dn = y2 - ym
        zs = eave2 - (ridge - eave2) / ds * ovh
        zn = eave - (ridge - eave) / dn * ovh
        o.face([(x1 - ovh, y1 - ovh, zs), (x2 + ovh, y1 - ovh, zs), (x2 + ovh, ym, ridge), (x1 - ovh, ym, ridge)], roof)
        o.face([(x2 + ovh, y2 + ovh, zn), (x1 - ovh, y2 + ovh, zn), (x1 - ovh, ym, ridge), (x2 + ovh, ym, ridge)], roof)
    else:
        xm = (x1 + x2) / 2 + ridge_off
        if walls:
            o.face([(x1, y2, 0), (x1, y1, 0), (x1, y1, eave), (x1, y2, eave)], wall)   # west
            o.face([(x2, y1, 0), (x2, y2, 0), (x2, y2, eave), (x2, y1, eave)], wall)   # east
            o.face([(x1, y1, 0), (x2, y1, 0), (x2, y1, eave), (xm, y1, ridge), (x1, y1, eave)], end_wall)
            o.face([(x2, y2, 0), (x1, y2, 0), (x1, y2, eave), (xm, y2, ridge), (x2, y2, eave)], end_wall)
        dw = xm - x1
        zo = eave - (ridge - eave) / dw * ovh
        o.face([(x1 - ovh, y2 + ovh, zo), (x1 - ovh, y1 - ovh, zo), (xm, y1 - ovh, ridge), (xm, y2 + ovh, ridge)], roof)
        o.face([(x2 + ovh, y1 - ovh, zo), (x2 + ovh, y2 + ovh, zo), (xm, y2 + ovh, ridge), (xm, y1 - ovh, ridge)], roof)

def posts_along(o, pts, z0, z1, w=0.9, mat='timber'):
    for (x, y) in pts:
        box(o, x - w / 2, y - w / 2, x + w / 2, y + w / 2, z0, z1, mat, None)

def fence(o, x1, y1, x2, y2, h, rails, mat='pipe', post=8.0, w=1.0):
    L = np.hypot(x2 - x1, y2 - y1); n = max(1, int(round(L / post)))
    for i in range(n + 1):
        t = i / n; x = x1 + (x2 - x1) * t; y = y1 + (y2 - y1) * t
        o.line([(x, y, 0), (x, y, h)], mat, w * 1.2)
    for r in rails:
        o.line([(x1, y1, r), (x2, y2, r)], mat, w)

def ground_poly(o, x1, y1, x2, y2, mat, z=0.0):
    o.face([(x1, y1, z), (x2, y1, z), (x2, y2, z), (x1, y2, z)], mat, ink=False)

# ---------- scene ----------
def build():
    objs = []
    G = Obj('ground', cast_shadow=False, ground=True)
    # site grass (big) is drawn separately; paving and dirt here (order = paint order)
    # drive coming from south up to barn & service lane
    ground_poly(G, 303 / 1, -520, 333, -254, 'asphalt')            # main service drive (from photo)
    ground_poly(G, 145.7, -600, 168.5, -246, 'asphalt')            # west parking drive (from entry road)
    ground_poly(G, 83, -245.8, 303, -230.5, 'concrete')            # E-W lane south of arena
    ground_poly(G, 168.5, -254, 303, -245.8, 'asphalt')
    ground_poly(G, 168.5, -339, 300, -254, 'grasspark')            # grass parking
    ground_poly(G, 194, -230.5, 218.6, -93.6, 'concrete')          # lane between cattle barns
    ground_poly(G, 302.7, -254, 329.5, -93.6, 'concrete')          # service lane east of arena
    ground_poly(G, 329.5, -262.7, 460, -254.2, 'concrete')         # 8' lane north of barn
    ground_poly(G, 333, -340, 420, -313.6, 'asphalt')              # apron in front of barn
    for r in [R(965, 276, 1072, 415), R(965, 415, 1072, 555), R(1097, 276, 1220, 415),
              R(1097, 415, 1220, 555), R(1097, 555, 1220, 680), R(965, 555, 1072, 680)]:
        ground_poly(G, *r, 'dirt')
    ground_poly(G, *R(645, 530, 893, 680), 'arenadirt')            # arena floor
    ground_poly(G, *R(995, 935, 1140, 995), 'dirt')                # compost pad
    for r in [R(245, 168, 608, 275), R(612, 168, 965, 275), R(138, 537, 245, 868), R(138, 868, 245, 990)]:
        ground_poly(G, *r, 'turnout')
    # parking stall rows (light lines) handled as ground lines
    objs.append(G)

    # ---- Cattle barns A & B: open pole barns, ridge E-W, white gable ends
    for nm, (x1, y1, x2, y2) in [('cattleA', R(645, 276, 893, 460)), ('cattleB', R(322, 276, 572, 460))]:
        o = Obj(nm)
        eave, ridge = 11.0, 20.0
        ym = (y1 + y2) / 2
        # interior shadow walls (open sides)
        o.face([(x1, y1, 0), (x2, y1, 0), (x2, y1, eave), (x1, y1, eave)], 'openshade')
        o.face([(x2, y2, 0), (x1, y2, 0), (x1, y2, eave), (x2, y2, eave)], 'openshade')
        # gable ends: white metal in the triangle + solid end bays
        for xe, sgn in [(x1, -1), (x2, 1)]:
            o.face([(xe, y1, 0), (xe, y1 + 10, 0), (xe, y1 + 10, eave), (xe, y1, eave)], 'whitemetal')
            o.face([(xe, y2 - 10, 0), (xe, y2, 0), (xe, y2, eave), (xe, y2 - 10, eave)], 'whitemetal')
            o.face([(xe, y1 + 10, 0), (xe, y2 - 10, 0), (xe, y2 - 10, eave), (xe, y1 + 10, eave)], 'openshade')
            o.face([(xe, y1, eave), (xe, ym, ridge), (xe, y2, eave)], 'whitemetal')
        gable(o, x1, y1, x2, y2, eave, ridge, 'x', 'whitemetal', 'roof', walls=False, ovh=2.0)
        # posts on long sides at 12' module
        xs = np.arange(x1, x2 + 0.1, 12.0)
        posts_along(o, [(x, y1 - 0.6) for x in xs] + [(x, y2 + 0.6) for x in xs], 0, eave - 0.3)
        # pipe gates across open bays
        for x in xs[:-1]:
            o.line([(x, y1 - 0.8, 4.2), (x + 12, y1 - 0.8, 4.2)], 'pipe', 1.0)
            o.line([(x, y1 - 0.8, 2.2), (x + 12, y1 - 0.8, 2.2)], 'pipe', 0.8)
        # ridge monitor
        o.face([(x1 + 6, ym - 4, ridge - 1.5), (x2 - 6, ym - 4, ridge - 1.5), (x2 - 6, ym - 4, ridge + 1.6), (x1 + 6, ym - 4, ridge + 1.6)], 'openshade')
        o.face([(x1 + 4, ym - 6, ridge + 1.2), (x2 - 4, ym - 6, ridge + 1.2), (x2 - 4, ym, ridge + 3.0), (x1 + 4, ym, ridge + 3.0)], 'roof')
        o.face([(x2 - 4, ym + 6, ridge + 1.2), (x1 + 4, ym + 6, ridge + 1.2), (x1 + 4, ym, ridge + 3.0), (x2 - 4, ym, ridge + 3.0)], 'roof')
        objs.append(o)

    # ---- Arena: covered pavilion, timber posts, ridge E-W
    x1, y1, x2, y2 = R(645, 530, 893, 680)
    o = Obj('arena')
    eave, ridge = 14.0, 25.0
    gable(o, x1, y1, x2, y2, eave, ridge, 'x', 'whitemetal', 'roof', walls=False, ovh=2.5)
    ym = (y1 + y2) / 2
    for xe in (x1, x2):
        o.face([(xe, y1, eave), (xe, ym, ridge), (xe, y2, eave)], 'trussend')
    xs = np.linspace(x1, x2, 8)
    # grooming bay inside (west) – enclosed white box, painted before the roof
    gx1, gy1, gx2, gy2 = R(650, 545, 683, 672)
    o.bias = 200.0
    box(o, gx1, gy1, gx2, gy2, 0, 10, 'whitemetal', 'roofflat')
    o.bias = 0.0
    posts_along(o, [(x, y1) for x in xs] + [(x, y2) for x in xs], 0, eave, w=1.1)
    objs.append(o)
    o3 = Obj('arenarail', cast_shadow=False)
    fence(o3, gx2 + 2, y1 + 3, x2 - 3, y1 + 3, 4.5, [4.5, 2.5, 0.8], 'pipe', post=10)
    fence(o3, gx2 + 2, y2 - 3, x2 - 3, y2 - 3, 4.5, [4.5, 2.5, 0.8], 'pipe', post=10)
    fence(o3, x2 - 3, y1 + 3, x2 - 3, y2 - 3, 4.5, [4.5, 2.5, 0.8], 'pipe', post=10)
    objs.append(o3)

    # ---- Small animal barns (swine A two parts, small animal B), ridge N-S, white
    for nm, r, mat in [('swineA_n', R(245, 537, 353, 680), 'whitemetal'),
                       ('swineA_s', R(245, 725, 353, 868), 'whitemetal'),
                       ('smallB', R(245, 868, 353, 990), 'whitemetal')]:
        x1, y1, x2, y2 = r
        o = Obj(nm)
        gable(o, x1, y1, x2, y2, 9.5, 16.5, 'y', mat, 'roof', ovh=1.5)
        # curtain openings on long sides
        o.bias = -30.0
        o.face([(x1 - 0.05, y2 - 3, 3.5), (x1 - 0.05, y1 + 3, 3.5), (x1 - 0.05, y1 + 3, 8.0), (x1 - 0.05, y2 - 3, 8.0)], 'openshade')
        o.face([(x2 + 0.05, y1 + 3, 3.5), (x2 + 0.05, y2 - 3, 3.5), (x2 + 0.05, y2 - 3, 8.0), (x2 + 0.05, y1 + 3, 8.0)], 'openshade')
        o.bias = 0.0
        objs.append(o)

    # ---- Feed storage & bedding storage (small white sheds)
    o = Obj('feed'); x1, y1, x2, y2 = R(525, 560, 572, 680)
    gable(o, x1, y1, x2, y2, 9, 13, 'y', 'whitemetal', 'roof', ovh=1.0); objs.append(o)
    o = Obj('bedding'); x1, y1, x2, y2 = R(893, 276, 965, 310)
    gable(o, x1, y1, x2, y2, 9, 12, 'x', 'whitemetal', 'roof', ovh=1.0); objs.append(o)

    # ---- Existing barn (weathered wood, rusty galv roof), asymmetric gable E-W
    x1, y1, x2, y2 = R(983, 775, 1220, 925)
    o = Obj('exbarn')
    gable(o, x1, y1, x2, y2, 13.5, 21.0, 'x', 'oldwood', 'rustroof', ridge_off=8.0, eave2=10.0, ovh=1.0)
    ym = (y1 + y2) / 2 + 8.0
    # roll-up doors on west gable end (x = x1), facing the drive
    def door(y_a, y_b, h):
        o.face([(x1 - 0.1, y_b, 0.2), (x1 - 0.1, y_a, 0.2), (x1 - 0.1, y_a, h), (x1 - 0.1, y_b, h)], 'doorwhite')
    o.bias = -40.0
    door(y2 - 4, y2 - 14, 12.0)
    door(y2 - 17, y2 - 27, 12.0)
    door(y1 + 16, y1 + 6, 8.5)
    # small windows + man door on south side
    for xw in (x1 + 44, x1 + 58):
        o.face([(xw, y1 - 0.1, 5), (xw + 3, y1 - 0.1, 5), (xw + 3, y1 - 0.1, 8.5), (xw, y1 - 0.1, 8.5)], 'darkglass')
    o.face([(x2 - 12, y1 - 0.1, 0.2), (x2 - 6, y1 - 0.1, 0.2), (x2 - 6, y1 - 0.1, 8), (x2 - 12, y1 - 0.1, 8)], 'doorwhite')
    # vertical board lines (weathered siding)
    for xx in np.arange(x1 + 2.5, x2, 2.6):
        o.line([(xx, y1 - 0.15, 0.3), (xx, y1 - 0.15, 9.7)], 'boardline', 0.6)
    for yy in np.arange(y1 + 2.5, y2, 2.6):
        ztop = 10 + (13.5 - 10) * 0 if yy < ym else 13.5
        o.line([(x1 - 0.15, yy, 0.3), (x1 - 0.15, yy, min(10 + (21 - 10) * (yy - y1) / (ym - y1) if yy < ym else 21 - (21 - 13.5) * (yy - ym) / (y2 - ym), 21) - 0.4)], 'boardline', 0.6)
    o.bias = 0.0
    objs.append(o)
    # lean-to on north side of existing barn (open, gates)
    o = Obj('leanto')
    lx1, ly1, lx2, ly2 = x1, y2, x1 + 30, y2 + 9
    o.face([(lx1, ly1, 0), (lx1, ly2, 0), (lx1, ly2, 8.5), (lx1, ly1, 11.5)], 'openshade')
    o.face([(lx1 - 1, ly1, 11.6), (lx2, ly1, 11.6), (lx2, ly2 + 0.8, 8.2), (lx1 - 1, ly2 + 0.8, 8.2)], 'rustroof')
    o.face([(lx2, ly2, 0), (lx1, ly2, 0), (lx1, ly2, 8.3), (lx2, ly2, 8.3)], 'openshade')
    posts_along(o, [(lx1, ly2), (lx1 + 10, ly2), (lx1 + 20, ly2), (lx2, ly2)], 0, 8.3, w=0.7, mat='oldtimber')
    fence(o, lx1 - 0.3, ly1 + 0.5, lx1 - 0.3, ly2, 4.5, [4.3, 2.8, 1.3], 'oldboard', post=4.5)
    objs.append(o)

    # ---- 7 existing cattle pens: low open shed, shed roof
    x1, y1, x2, y2 = R(972, 680, 1220, 750)
    o = Obj('expens')
    o.face([(x1, y1, 0), (x2, y1, 0), (x2, y1, 8.0), (x1, y1, 8.0)], 'openshade')
    o.face([(x1, y2, 0), (x1, y1, 0), (x1, y1, 8.0), (x1, y2, 10.5)], 'openshade')
    o.face([(x1 - 1, y1 - 1.5, 7.6), (x2 + 1, y1 - 1.5, 7.6), (x2 + 1, y2 + 1, 10.8), (x1 - 1, y2 + 1, 10.8)], 'rustroof')
    posts_along(o, [(x, y1 - 0.4) for x in np.linspace(x1, x2, 8)], 0, 7.8, w=0.7, mat='oldtimber')
    for x in np.linspace(x1, x2, 8)[:-1]:
        o.line([(x, y1 - 0.6, 4.0), (x + (x2 - x1) / 7, y1 - 0.6, 4.0)], 'pipe', 0.8)
    objs.append(o)

    # ---- Outdoor pens 1–5 & chute: pipe fences, each segment its own object for sorting
    pens = [R(965, 276, 1072, 415), R(965, 415, 1072, 555), R(1097, 276, 1220, 415),
            R(1097, 415, 1220, 555), R(1097, 555, 1220, 680), R(965, 555, 1072, 680)]
    for i, (x1, y1, x2, y2) in enumerate(pens):
        for j, seg in enumerate([(x1, y1, x2, y1), (x2, y1, x2, y2), (x2, y2, x1, y2), (x1, y2, x1, y1)]):
            f = Obj(f'pen{i}_{j}', cast_shadow=False)
            fence(f, *seg, 5.0, [5.0, 3.6, 2.2, 0.9], 'pipe', post=10.0, w=0.9)
            objs.append(f)
    # chute alley inside lead-up area
    x1, y1, x2, y2 = R(965, 555, 1072, 680)
    f = Obj('chute', cast_shadow=False)
    fence(f, x1 + 16, y1, x1 + 16, y2 - 8, 5.5, [5.5, 3.5, 1.5], 'pipe', post=6)
    fence(f, x1 + 20, y1, x1 + 20, y2 - 8, 5.5, [5.5, 3.5, 1.5], 'pipe', post=6)
    objs.append(f)

    # ---- Turnout board fences (wood, 3 rails), split into short segments
    tos = [R(245, 168, 608, 275), R(612, 168, 965, 275), R(138, 537, 245, 868), R(138, 868, 245, 990)]
    k = 0
    for (x1, y1, x2, y2) in tos:
        for seg in [(x1, y1, x2, y1), (x2, y1, x2, y2), (x2, y2, x1, y2), (x1, y2, x1, y1)]:
            L = np.hypot(seg[2] - seg[0], seg[3] - seg[1]); n = max(1, int(L // 40))
            for t in range(n):
                a = t / n; b = (t + 1) / n
                f = Obj(f'to{k}', cast_shadow=False); k += 1
                fence(f, seg[0] + (seg[2] - seg[0]) * a, seg[1] + (seg[3] - seg[1]) * a,
                      seg[0] + (seg[2] - seg[0]) * b, seg[1] + (seg[3] - seg[1]) * b,
                      4.5, [4.3, 2.9, 1.5], 'board', post=8.0, w=1.0)
                objs.append(f)

    # ---- compost bins (3 bays, low concrete walls)
    x1, y1, x2, y2 = R(995, 935, 1140, 995)
    o = Obj('compost')
    for i in range(4):
        xx = x1 + 4 + i * (x2 - x1 - 8) / 3
        box(o, xx - 0.5, y1 + 2, xx + 0.5, y2 - 2, 0, 4.5, 'concrete_w', 'concrete_w')
    box(o, x1 + 3.5, y2 - 3, x2 - 3.5, y2 - 2, 0, 4.5, 'concrete_w', 'concrete_w')
    objs.append(o)
    # dumpsters
    o = Obj('dumpsters'); x1, y1, x2, y2 = R(985, 1000, 1018, 1075)
    box(o, x1, y1 + 2, x2, y1 + 8.5, 0, 5, 'dumpster', 'dumpster'); box(o, x1, y1 + 11, x2, y1 + 17.5, 0, 5, 'dumpster', 'dumpster')
    objs.append(o)

    # ---- a few cars in the grass parking / paved drive
    rng = np.random.default_rng(7)
    carcols = ['car_white', 'car_silver', 'car_blue', 'car_white']
    spots = []
    for i, (cx, cy) in enumerate(spots):
        o = Obj(f'car{i}')
        m = carcols[i % len(carcols)]
        box(o, cx - 3.1, cy - 7.5, cx + 3.1, cy + 7.5, 0.6, 3.0, m, None)
        box(o, cx - 2.7, cy - 3.6, cx + 2.7, cy + 3.0, 3.0, 4.7, 'carglass', m)
        objs.append(o)
    return objs

# tree placements (x, y, kind, size)
def trees():
    rng = np.random.default_rng(11)
    T = []
    # live oaks framing west + north
    for x, y, s in [(20, -150, 1.2), (10, -230, 1.0), (25, -300, 1.1), (30, -40, 1.3), (110, -20, 1.0),
                    (170, -25, 1.25), (260, -15, 1.1), (360, -30, 1.3), (440, -60, 1.25), (450, -150, 1.1),
                    (455, -240, 1.0), (445, -300, 1.35), (470, -350, 1.15), (128, -428, 1.3), (380, -455, 1.3), (300, -470, 0.9)]:
        T.append((x + rng.normal(0, 4), y + rng.normal(0, 4), 'oak', s))
    # tall slash pines
    for x, y in [(70, -60), (230, 5), (300, -10), (395, -20), (465, -110), (40, -260), (480, -280), (150, 15)]:
        T.append((x, y, 'pine', 1.0 + rng.uniform(-0.15, 0.2)))
    # sabal palms near barn / entry
    for x, y in [(425, -330), (432, -322), (345, -350), (60, -395)]:
        T.append((x, y, 'palm', 1.0 + rng.uniform(-0.1, 0.15)))
    return T
