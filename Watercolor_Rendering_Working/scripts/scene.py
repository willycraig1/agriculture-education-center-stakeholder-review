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


# ---------- barn-kit builders (the pre-engineered system of the McIntosh Ag Center references) ----------
RT, JD = 0.5, 1.5          # roof: ~6" of 2x6 framing under metal panels and trim; bar joists 18" deep

def slab(o, top, t=RT, top_mat='roof', under='roofunder'):
    """A roof plane t thick: top polygon (3D), its underside t below, and its edges."""
    bot = [(x, y, z - t) for x, y, z in top]
    o.face(top, top_mat)
    o.face(bot[::-1], under, ink=False)
    n = len(top)
    for i in range(n):
        o.face([top[i], top[(i + 1) % n], bot[(i + 1) % n], bot[i]], top_mat)

def thick_wall(o, pts, normal, t=0.5, mat='cladding'):
    """A wall t thick, centred on the plane of pts (a vertical polygon); normal = (nx, ny) across it."""
    nx, ny = normal
    a = [(x - nx * t / 2, y - ny * t / 2, z) for x, y, z in pts]
    b = [(x + nx * t / 2, y + ny * t / 2, z) for x, y, z in pts]
    o.face(a, mat); o.face(b[::-1], mat)
    n = len(pts)
    for i in range(n):
        o.face([a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]], mat)

def bar_joist(o, a, b, depth=JD, panel=2.5, mat='joist', ext=None):
    """A bar joist following the roof: top chord a->b (just under the roof), bottom chord parallel, depth below,
    Warren webs at about panel spacing. ext: a point the top chord carries on to (an eave extension)."""
    a, b = np.array(a, float), np.array(b, float)
    d = np.array([0, 0, depth])
    o.line([tuple(a), tuple(b)], mat, 1.0)
    o.line([tuple(a - d), tuple(b - d)], mat, 1.0)
    n = max(2, int(round(np.linalg.norm((b - a)[:2]) / panel)))
    for k in range(n):
        p, q = a + (b - a) * k / n, a + (b - a) * (k + 1) / n
        o.line([tuple(p - d if k % 2 else p), tuple(q if k % 2 else q - d)], mat, 0.7)
    o.line([tuple(a), tuple(a - d)], mat, 0.7); o.line([tuple(b), tuple(b - d)], mat, 0.7)
    if ext is not None:
        o.line([tuple(a), tuple(ext)], mat, 1.0)

def kit_gable(o, x1, y1, x2, y2, z_col, axis, ovh_lo=3.0, ovh_hi=3.0, ovh_side=3.0, slope=4 / 12, joist_lines=(), roof=True):
    """A 4:12 gable on the kit system. z_col: roof top at the column (eave) lines. axis 'x': ridge runs E-W
    across y; 'y': ridge runs N-S across x. ovh_lo/hi: overhang at the low/high end along the ridge."""
    if axis == 'x':
        hs, ym = (y2 - y1) / 2, (y1 + y2) / 2
        zr = z_col + hs * slope; ze = z_col - ovh_side * slope
        lo, hi = x1 - ovh_lo, x2 + ovh_hi
        if roof:
            slab(o, [(lo, y1 - ovh_side, ze), (hi, y1 - ovh_side, ze), (hi, ym, zr), (lo, ym, zr)])
            slab(o, [(hi, y2 + ovh_side, ze), (lo, y2 + ovh_side, ze), (lo, ym, zr), (hi, ym, zr)])
        for x in joist_lines:
            for ye in (y1, y2):
                bar_joist(o, (x, ye, z_col - RT), (x, ym, zr - RT), ext=(x, ye + (ye - ym) / hs * ovh_side, ze - RT))
    else:
        hs, xm = (x2 - x1) / 2, (x1 + x2) / 2
        zr = z_col + hs * slope; ze = z_col - ovh_side * slope
        lo, hi = y1 - ovh_lo, y2 + ovh_hi
        if roof:
            slab(o, [(x1 - ovh_side, hi, ze), (x1 - ovh_side, lo, ze), (xm, lo, zr), (xm, hi, zr)])
            slab(o, [(x2 + ovh_side, lo, ze), (x2 + ovh_side, hi, ze), (xm, hi, zr), (xm, lo, zr)])
        for y in joist_lines:
            for xe in (x1, x2):
                bar_joist(o, (xe, y, z_col - RT), (xm, y, zr - RT), ext=(xe + (xe - xm) / hs * ovh_side, y, ze - RT))
    return zr

# ---------- scene ----------
def build():
    objs = []
    G = Obj('ground', cast_shadow=False, ground=True)
    # site grass (big) is drawn separately; paving and dirt here (order = paint order)
    # drive coming from south up to barn & service lane
    ground_poly(G, 303 / 1, -362, 333, -254, 'asphalt')            # service drive beside the existing barn, stopping short of the Red House (owner, 2026-10-19)
    ground_poly(G, 145.7, -455, 168.5, -246, 'asphalt')            # west parking drive, to the end of the lot's west leg (was carried on into the pasture)
    ground_poly(G, 83, -245.8, 303, -230.5, 'concrete')            # E-W lane south of arena
    ground_poly(G, 168.5, -254, 303, -245.8, 'grass')              # planting strip north of the parking, palms (owner, 2026-10-20)
    ground_poly(G, 168.5, -339, 300, -254, 'grasspark')            # grass parking
    ground_poly(G, 194, -230.5, 218.6, -93.6, 'concrete')          # lane between cattle barns
    ground_poly(G, 302.7, -254, 983 / S, -91.5, 'concrete')        # service lane east of arena, out to the barn front line (no grass strip)
    ground_poly(G, 329.5, -262.7, 499.6, -254.6, 'concrete')       # 8' walk north of barn, out to the unfinished barn (as the plan's walk)
    ground_poly(G, 333, -340, 420, -313.6, 'asphalt')              # apron in front of barn
    for r in [R(983, 270, 1109, 415), R(983, 415, 1109, 555), R(1132.6, 270, 1258.5, 415),
              R(1132.6, 415, 1258.5, 555), R(1132.6, 555, 1258.5, 680), R(983, 555, 1109, 680),
              R(1109, 270, 1132.6, 680)]:                                  # and the alley between the pen columns
        ground_poly(G, *r, 'dirt')
    ground_poly(G, *R(645, 530, 893, 680), 'arenadirt')            # arena floor
    ground_poly(G, *R(983, 935, 1128, 995), 'dirt')                # compost pad
    for r in [R(245, 162, 608, 270), R(612, 162, 983, 270), R(138, 537, 245, 697.85), R(138, 697.85, 245, 858.5), R(138, 858.5, 245, 1001.3)]:
        ground_poly(G, *r, 'turnout')
    # parking stall rows (light lines) handled as ground lines
    objs.append(G)

    # ---- Cattle barns A & B, after the McIntosh Ag Center cattle barn (source/Clark Farm Study Plan-A2.0 Cattle Barn
    # Reference.pdf, Bldg 19): 24' pen rows either side of a 16' tractor aisle (64' deep; owner, 2026-10-19), 84' long
    # (7 pens a side at 12'), columns at 12'. 1:12 shed roofs over the pens, about 10.4' at the outer columns and
    # 12.4' at the aisle; a 4:12 monitor over the aisle, about 16.3' at the eaves and 19' at the ridge (tops of roof).
    # Kit system: wood columns, black 18" bar joists on every column line following the roof, a 6" roof (2x6 framing,
    # metal panels and trim), 3' overhangs. Gable ends and monitor walls clad (red metal panel, or vertical wood
    # siding to match the existing barn), a 16' x 10' opening at each end of the aisle. Long sides open over pipe
    # gate panels. Sand bedding in the pens, concrete in the aisle. No tack or feed rooms.
    for nm, (x1, y1, x2, y2) in [('cattleA', R(645, 270, 893, 460)), ('cattleB', R(322, 270, 572, 460))]:
        o = Obj(nm)
        ym = (y1 + y2) / 2
        AI = 8.0 * (y2 - y1) / 64.0                     # half the aisle, in this frame's feet
        ya, yb = ym - AI, ym + AI                       # aisle edges = inner column lines
        Z_OUT, Z_IN, M_EAVE, M_RIDGE, OVH = 10.4, 12.4, 16.33, 19.0, 3.0
        zs = lambda d: Z_OUT + (Z_IN - Z_OUT) * d / (ya - y1)   # shed roof top, d = distance in from the outer line
        ground_poly(G, x1, y1, x2, ya, 'dirt')          # sand bedding (owner, 2026-10-19)
        ground_poly(G, x1, yb, x2, y2, 'dirt')
        ground_poly(G, x1, ya, x2, yb, 'concrete')      # heavy broom finish concrete aisle
        zo = zs(-OVH)
        slab(o, [(x1 - OVH, y1 - OVH, zo), (x2 + OVH, y1 - OVH, zo), (x2 + OVH, ya, Z_IN), (x1 - OVH, ya, Z_IN)])
        slab(o, [(x2 + OVH, y2 + OVH, zo), (x1 - OVH, y2 + OVH, zo), (x1 - OVH, yb, Z_IN), (x2 + OVH, yb, Z_IN)])
        mz = M_EAVE - (M_RIDGE - M_EAVE) / AI * OVH
        slab(o, [(x1 - OVH, ya - OVH, mz), (x2 + OVH, ya - OVH, mz), (x2 + OVH, ym, M_RIDGE), (x1 - OVH, ym, M_RIDGE)])
        slab(o, [(x2 + OVH, yb + OVH, mz), (x1 - OVH, yb + OVH, mz), (x1 - OVH, ym, M_RIDGE), (x2 + OVH, ym, M_RIDGE)])
        for yy in (ya, yb):                             # monitor walls, from the shed roofs to the monitor roof
            thick_wall(o, [(x1, yy, Z_IN - RT), (x2, yy, Z_IN - RT), (x2, yy, M_EAVE - RT), (x1, yy, M_EAVE - RT)], (0, 1))
        for xe in (x1, x2):                             # gable ends: pen bays, and the wall over the aisle opening
            thick_wall(o, [(xe, y1, 0), (xe, ya, 0), (xe, ya, Z_IN - RT), (xe, y1, Z_OUT - RT)], (1, 0))
            thick_wall(o, [(xe, yb, 0), (xe, y2, 0), (xe, y2, Z_OUT - RT), (xe, yb, Z_IN - RT)], (1, 0))
            thick_wall(o, [(xe, ya, 10.0), (xe, yb, 10.0), (xe, yb, M_EAVE - RT), (xe, ym, M_RIDGE - RT), (xe, ya, M_EAVE - RT)], (1, 0))
        xs = np.linspace(x1, x2, 8)
        for x in xs:                                    # bar joists on every column line
            bar_joist(o, (x, y1, Z_OUT - RT), (x, ya, Z_IN - RT), ext=(x, y1 - OVH, zo - RT))
            bar_joist(o, (x, y2, Z_OUT - RT), (x, yb, Z_IN - RT), ext=(x, y2 + OVH, zo - RT))
            bar_joist(o, (x, ya, M_EAVE - RT), (x, ym, M_RIDGE - RT), ext=(x, ya - OVH, mz - RT))
            bar_joist(o, (x, yb, M_EAVE - RT), (x, ym, M_RIDGE - RT), ext=(x, yb + OVH, mz - RT))
        posts_along(o, [(x, y) for x in xs for y in (y1, y2)], 0, Z_OUT - RT - JD, w=0.7, mat='timber')
        posts_along(o, [(x, y) for x in xs for y in (ya, yb)], 0, M_EAVE - RT - JD, w=0.7, mat='timber')
        objs.append(o)
        # pipe gate panels: along both open sides, along the aisle, and between pens (5 rails, 5.5' high)
        g = Obj(nm + '_gates', cast_shadow=False)
        RAILS = [5.4, 4.2, 3.0, 1.8, 0.7]
        for yy in (y1, ya, yb, y2):
            fence(g, x1, yy, x2, yy, 5.5, RAILS, 'pipe', post=12.0, w=0.9)
        for x in xs[1:-1]:
            fence(g, x, y1, x, ya, 5.5, RAILS, 'pipe', post=12.0, w=0.9)
            fence(g, x, yb, x, y2, 5.5, RAILS, 'pipe', post=12.0, w=0.9)
        objs.append(g)

    # ---- Arena: covered pavilion on the kit system, after the McIntosh Ag Center pavilion (source/Clark Farm Study
    # Plan-A2.0 Arena and SmAnimal Barn Reference.pdf: 96' x 50' clear span, 8 bays): ours is one bay shorter, 84' x 50',
    # 8x8 wood columns at 12' on both long sides, a 4:12 gable of bar joists spanning the 50', joists 14' clear at the
    # columns, a 6" roof, 3' overhangs (owner). Open all round. The grooming area (Level 2) sits inside the west end.
    x1, y1, x2, y2 = R(645, 530, 893, 680)
    o = Obj('arena')
    xs = np.linspace(x1, x2, 8)
    Z_COL = 14.0 + JD + RT                              # roof top at the column lines
    kit_gable(o, x1, y1, x2, y2, Z_COL, 'x', joist_lines=xs)
    posts_along(o, [(x, y1) for x in xs] + [(x, y2) for x in xs], 0, 14.0, w=0.75, mat='timber')
    objs.append(o)
    # grooming area (Level 2) at the arena's west end: not a building but an open wash area (owner, 2026-10-20), a
    # concrete pad with short pipe panels out from the west column line to tie animals to while they are hosed down
    # and blown out (no rail along the column line: the panels alone, room to work around them; owner)
    gx1, gy1, gx2, gy2 = R(650, 545, 683, 672)
    og = Obj('grooming')
    box(og, gx1, gy1, gx2, gy2, 0, 0.25, 'concrete', 'concrete')
    for k in range(1, 5):
        yk = gy1 + k * (gy2 - gy1) / 5
        fence(og, gx1 + 0.8, yk, gx1 + 5.8, yk, 4.5, [4.5, 2.5], 'pipe', post=5)
    objs.append(og)
    # arena rail, closed in on the west (between the arena and the grooming area)
    o3 = Obj('arenarail', cast_shadow=False)
    fence(o3, gx2 + 2, y1 + 3, x2 - 3, y1 + 3, 4.5, [4.5, 2.5, 0.8], 'pipe', post=10)
    fence(o3, gx2 + 2, y2 - 10, x2 - 3, y2 - 10, 4.5, [4.5, 2.5, 0.8], 'pipe', post=10)
    fence(o3, x2 - 3, y1 + 3, x2 - 3, y2 - 10, 4.5, [4.5, 2.5, 0.8], 'pipe', post=10)
    fence(o3, gx2 + 2, y1 + 3, gx2 + 2, y2 - 10, 4.5, [4.5, 2.5, 0.8], 'pipe', post=10)
    objs.append(o3)
    # two 4-row x 24' fixed aluminium bleachers along the north side, inside the columns (owner, 2026-10-19), 12' in
    # from each end with 12' between: rows about 1.75' deep stepping up 0.75' toward the columns, from a 1.3' seat
    ob = Obj('bleachers')
    for bx in (x1 + 12.0, x1 + 48.0):
        for r in range(4):
            ya_ = y2 - 0.5 - 7.0 + r * 1.75
            box(ob, bx, ya_, bx + 24.0, ya_ + 1.75, 0, 1.3 + 0.75 * r, 'alum', 'alum')
    objs.append(ob)

    # ---- Small animal barns on the kit system, after the McIntosh Ag Center Bldg 18 (same reference; 34' wide there,
    # 36' o.c. here to stay on the 12' module; owner): a 4:12 gable of bar joists on the column lines, joists 12' clear
    # at the columns, a 6" roof, 3' overhangs. Barn A is two wings either side of a 15' dogtrot under one continuous
    # roof, the wings' dividing walls on their column lines at the 12' dogtrot; barn B (Level 3) extends it south four
    # bays. Clad gable and dividing walls (an 8' aisle opening; an exhaust fan in each gable), roll-up clear curtains on
    # the long sides. 6' x 10' pens either side of an 8' aisle; concrete floor. No tack rooms, no A/C.
    sx1, sx2 = 245 / S, 353 / S
    sxm, shw = (sx1 + sx2) / 2, (sx2 - sx1) / 2
    Z_COL = 12.0 + JD + RT
    zroof = lambda x: Z_COL + (shw - abs(x - sxm)) * 4 / 12          # roof top across the barn
    # (name, north line px, south line px, overhang north, overhang south, walls at north / south)
    # dogtrot one 12' bay, barn B four bays (owner, 2026-10-19); plan feet x 2.974 px in this traced frame
    segs = [('swineA_n', 537, 680, 3.0, 0.0, 'gable', 'divide'),
            ('dogtrot', 680, 715.7, 0.0, 0.0, None, None),
            ('swineA_s', 715.7, 858.5, 0.0, 3.0, 'divide', 'gable'),
            ('smallB', 858.5, 1001.3, -3.0, 3.0, None, 'gable')]                # B starts at A's south overhang
    for nm, pn, ps, on, os_, wn, ws in segs:
        yn, ysth = -pn / S, -ps / S
        o = Obj(nm)
        ground_poly(G, sx1, ysth, sx2, yn, 'concrete')
        lines = [] if nm == 'dogtrot' else list(np.arange(ysth, yn - 0.5, 12.0)) + [yn]
        if nm == 'smallB':
            lines = [y for y in lines if y < yn - 0.5]                    # its north line is barn A's south wall
        kit_gable(o, sx1, ysth, sx2, yn, Z_COL, 'y', ovh_lo=os_, ovh_hi=on, joist_lines=lines)
        if lines:
            posts_along(o, [(x, y) for y in lines for x in (sx1, sx2)], 0, 12.0, w=0.75, mat='timber')
        for yy, kind in ((yn, wn), (ysth, ws)):
            if not kind:
                continue
            prof = [(sx1, yy, 0), (sx2, yy, 0), (sx2, yy, Z_COL - RT), (sxm, yy, zroof(sxm) - RT), (sx1, yy, Z_COL - RT)]
            # wall with the aisle opening (8' x 9') cut out: two side panels and the gable above
            ai = 4.0
            thick_wall(o, [(sx1, yy, 0), (sxm - ai, yy, 0), (sxm - ai, yy, 9.0), (sx1, yy, 9.0)], (0, 1))
            thick_wall(o, [(sxm + ai, yy, 0), (sx2, yy, 0), (sx2, yy, 9.0), (sxm + ai, yy, 9.0)], (0, 1))
            thick_wall(o, [(sx1, yy, 9.0), (sx2, yy, 9.0), (sx2, yy, Z_COL - RT), (sxm, yy, zroof(sxm) - RT), (sx1, yy, Z_COL - RT)], (0, 1))
            if kind == 'gable':                                             # exhaust fan high in the gable
                side = 1 if yy == yn else -1
                o.face([(sxm - 2, yy + side * 0.3, 13.0), (sxm + 2, yy + side * 0.3, 13.0), (sxm + 2, yy + side * 0.3, 16.5), (sxm - 2, yy + side * 0.3, 16.5)], 'darkglass')
        if nm != 'dogtrot':
            for xx in (sx1, sx2):                                          # roll-up clear curtains on the column lines
                o.face([(xx, ysth, 0.5), (xx, yn, 0.5), (xx, yn, 12.0), (xx, ysth, 12.0)], 'curtain', ink=False)
        objs.append(o)
        if nm != 'dogtrot':
            # 6' x 10' pens either side of an 8' aisle (owner, 2026-10-19), a 4' strip between the pens and the
            # curtain line (the reference barn's drain strip); livestock panels at the pen backs and fronts
            g = Obj(nm + '_pens', cast_shadow=False)
            pb1, pf1, pf2, pb2 = sxm - 4.0 - 10.0, sxm - 4.0, sxm + 4.0, sxm + 4.0 + 10.0
            for xx in (pb1, pf1, pf2, pb2):
                fence(g, xx, ysth, xx, yn, 4.0, [3.9, 2.6, 1.3, 0.3], 'pipe', post=6.0, w=0.8)
            for y in np.arange(ysth + 6, yn - 0.5, 6.0):
                fence(g, pb1, y, pf1, y, 4.0, [3.9, 2.6, 1.3, 0.3], 'pipe', post=10.0, w=0.8)
                fence(g, pf2, y, pb2, y, 4.0, [3.9, 2.6, 1.3, 0.3], 'pipe', post=10.0, w=0.8)
            objs.append(g)

    # ---- Feed storage & bedding storage (small white sheds)
    o = Obj('feed'); x1, y1, x2, y2 = R(525, 560, 572, 680)
    gable(o, x1, y1, x2, y2, 9, 13, 'y', 'whitemetal', 'roof', ovh=1.0); objs.append(o)
    # bedding storage: two open bins like the compost bins, three-sided concrete walls 5' high, open to the south
    # (owner, 2026-10-19), with a pile of bedding in each
    # it fills the north end of the lane between cattle barn A's 3' overhang and the holding pens (on the barn front
    # line), its back wall just inside the turnout fence (owner, 2026-10-19)
    o = Obj('bedding')
    x1, x2 = 893 / S + 3.8, 983 / S - 1.0
    y2 = -270 / S - 1.0; y1 = y2 - 12.0
    ground_poly(G, x1, y1 - 4, x2, y2, 'concrete')
    for xx in (x1, (x1 + x2) / 2, x2):
        box(o, xx - 0.4, y1, xx + 0.4, y2, 0, 5.0, 'concrete_w', 'concrete_w')
    box(o, x1 - 0.4, y2 - 0.8, x2 + 0.4, y2, 0, 5.0, 'concrete_w', 'concrete_w')
    for bx0, bx1 in ((x1 + 1.2, (x1 + x2) / 2 - 1.2), ((x1 + x2) / 2 + 1.2, x2 - 1.2)):
        box(o, bx0, y1 + 2.5, bx1, y2 - 1.6, 0, 2.6, 'arenadirt', 'arenadirt')
    objs.append(o)

    # ---- Existing barn, from the architect's sheet "A2.0 Existing Barn" (Study Plan A2.1, 2025-08-20):
    # one-story wood-frame garage 80.4' x 50.4', symmetric gable E-W, eaves about 10.9', ridge about 19.6'
    # (about 4:12; heights scaled off the elevations). West gable end: four 10' roll-up doors, the outer two
    # 9' high, the centre two 14'. South side: three windows, a roll-up door, and a man door.
    x1, y1, x2, y2 = R(983, 775, 1220, 925)
    EAVE, RIDGE = 10.9, 19.6
    o = Obj('exbarn')
    gable(o, x1, y1, x2, y2, EAVE, RIDGE, 'x', 'oldwood', 'rustroof', ovh=1.0)
    ym, half = (y1 + y2) / 2, (y2 - y1) / 2
    k = (y2 - y1) / 51.6          # elevation drawn 51.6' wide for the 50.4' wall
    o.bias = -40.0
    def door(ya, yb, h):         # on the west gable, ya > yb (measured from the north wall)
        o.face([(x1 - 0.1, yb, 0.2), (x1 - 0.1, ya, 0.2), (x1 - 0.1, ya, h), (x1 - 0.1, yb, h)], 'doorwhite')
    for (a, b), h in zip([(2.0, 12.1), (14.5, 24.6), (26.9, 37.0), (39.2, 49.3)], (9.0, 14.0, 14.0, 9.0)):
        door(y2 - a * k, y2 - b * k, h)
    for dy in (-1.3, 1.3):       # gable vents
        o.face([(x1 - 0.1, ym + dy - .6, 16.3), (x1 - 0.1, ym + dy + .6, 16.3), (x1 - 0.1, ym + dy + .6, 17.9), (x1 - 0.1, ym + dy - .6, 17.9)], 'darkglass')
    kx = (x2 - x1) / 81.1        # south elevation drawn 81.1' long for the 80.4' wall
    def south(xa, xb, z0, z1, m):
        o.face([(x1 + xa * kx, y1 - 0.1, z0), (x1 + xb * kx, y1 - 0.1, z0), (x1 + xb * kx, y1 - 0.1, z1), (x1 + xa * kx, y1 - 0.1, z1)], m)
    for xa in (20.7, 40.5, 60.0):
        south(xa, xa + 3.5, 3.5, 8.0, 'darkglass')
    south(46.9, 57.0, 0.2, 9.2, 'doorwhite')
    south(69.0, 72.2, 0.2, 7.2, 'doorwhite')
    # vertical board lines (weathered siding)
    for xx in np.arange(x1 + 2.5, x2, 2.6):
        o.line([(xx, y1 - 0.15, 0.3), (xx, y1 - 0.15, EAVE - 0.4)], 'boardline', 0.6)
    for yy in np.arange(y1 + 2.5, y2, 2.6):
        ztop = EAVE + (RIDGE - EAVE) * (1 - abs(yy - ym) / half)
        o.line([(x1 - 0.15, yy, 0.3), (x1 - 0.15, yy, ztop - 0.4)], 'boardline', 0.6)
    o.bias = 0.0
    objs.append(o)
    # concrete pad along the west end (10.5' wide)
    ground_poly(G, x1 - 10.5, y1, x1, y2, 'concrete')

    # covered concrete off the east end, north corner: 14.3' x 17.5', shed roof falling east to 7.75' (owner)
    o = Obj('excover')
    cx1, cx2, cy1, cy2 = x2, x2 + 14.3, y2 - 17.5, y2
    ground_poly(G, cx1, cy1, cx2, cy2, 'concrete')
    o.face([(cx1, cy1 - .8, 9.6), (cx2 + .8, cy1 - .8, 7.75), (cx2 + .8, cy2 + .5, 7.75), (cx1, cy2 + .5, 9.6)], 'rustroof')
    posts_along(o, [(cx2, cy1), (cx2, (cy1 + cy2) / 2), (cx2, cy2)], 0, 7.75, w=0.6, mat='oldtimber')
    objs.append(o)

    # ---- North of the barn: an 8' aisle, then 7 covered dirt-floor pens (11.5' bays) to the back fence 32' off
    # the barn. One shed roof runs from the barn's north eave out 20.5' (the aisle and the pens' front 12.5'),
    # falling from about 10.6' to 7.6'. Over the pens it runs on 13' past the barn's east end (93.4' in all); over
    # the aisle it stops flush with the barn's east face, leaving the walkway there open (the sheet's dashed line).
    o = Obj('leanto')
    yr0, yr1, zr0, zr1 = y2 + 1.0, y2 + 20.5, EAVE - (RIDGE - EAVE) / half * 1.0, 7.6
    lx2 = x1 + 93.4
    zr = lambda y: zr0 + (zr1 - zr0) * (y - yr0) / (yr1 - yr0)
    o.face([(x1 - 0.5, yr0, zr0), (x2, yr0, zr0), (x2, yr1, zr1), (x1 - 0.5, yr1, zr1)], 'rustroof')
    o.face([(x2, y2 + 8.0, zr(y2 + 8.0)), (lx2, y2 + 8.0, zr(y2 + 8.0)), (lx2, yr1, zr1), (x2, yr1, zr1)], 'rustroof')
    bays = list(np.linspace(x1, x2, 8)) + [lx2 - 0.4]
    posts_along(o, [(x, y2 + 8.2) for x in bays], 0, zr(y2 + 8.2) - 0.2, w=0.6, mat='oldtimber')
    posts_along(o, [(x, y2 + 20.0) for x in bays], 0, zr(y2 + 20.0) - 0.2, w=0.6, mat='oldtimber')
    objs.append(o)

    o = Obj('expens')
    py0, py1 = y2 + 8.2, y2 + 32.1
    ground_poly(G, x1, py0, x2, py1, 'dirt')    # sand bedding, as in the holding pens (owner, 2026-10-19)
    RAILS = [5.0, 3.9, 2.8, 1.7, 0.6]     # pipe-rail panels throughout (owner)
    for x in np.linspace(x1, x2, 8):      # partitions
        fence(o, x, py0, x, py1, 5.0, RAILS, 'pipe', post=10.0, w=0.9)
    for xa, xb in zip(np.linspace(x1, x2, 8)[:-1], np.linspace(x1, x2, 8)[1:]):   # feeders and gates along the aisle
        o.line([(xa, py0, 4.2), (xb, py0, 4.2)], 'pipe', 0.8)
        o.line([(xa, py0, 2.4), (xb, py0, 2.4)], 'pipe', 0.8)
    fence(o, x1, py1, lx2, py1, 5.0, RAILS, 'pipe', post=10.0, w=0.9)   # back fence (the sheet's 6' wooden fence)
    objs.append(o)

    # ---- Outdoor pens 1–5 & chute: pipe fences, each segment its own object for sorting
    # pens 1 to 3 (the east column) run out to the existing pens' dog-ear, 93.4' from the barn front (1258.5 px;
    # deck commit b9f2bcf), and the 8' alley is centred in the block: columns 42.7' wide each (3f83b7e; owner 2026-10-20)
    pens = [R(983, 270, 1109, 415), R(983, 415, 1109, 555), R(1132.6, 270, 1258.5, 415),
            R(1132.6, 415, 1258.5, 555), R(1132.6, 555, 1258.5, 680), R(983, 555, 1109, 680)]
    for i, (x1, y1, x2, y2) in enumerate(pens):
        for j, seg in enumerate([(x1, y1, x2, y1), (x2, y1, x2, y2), (x2, y2, x1, y2), (x1, y2, x1, y1)]):
            f = Obj(f'pen{i}_{j}', cast_shadow=False)
            fence(f, *seg, 5.0, [5.0, 3.6, 2.2, 0.9], 'pipe', post=10.0, w=0.9)
            objs.append(f)
    # a pipe gate across the north end of the alley between the holding pen columns, where it meets the turnout line
    ax1, ay1, ax2, ay2 = R(1109, 270, 1132.6, 680)
    gt = Obj('alleygate', cast_shadow=False)
    for xx in (ax1, ax2):
        gt.line([(xx, ay2, 0), (xx, ay2, 5.6)], 'pipe', 1.6)
    for z in (0.8, 1.7, 2.6, 3.5, 4.4):
        gt.line([(ax1 + 0.4, ay2, z), (ax2 - 0.4, ay2, z)], 'pipe', 0.9)
    gt.line([(ax1 + 0.4, ay2, 0.8), (ax2 - 0.4, ay2, 4.4)], 'pipe', 0.8)
    objs.append(gt)
    # chute alley inside lead-up area
    x1, y1, x2, y2 = R(983, 555, 1109, 680)
    f = Obj('chute', cast_shadow=False)
    fence(f, x1 + 16, y1, x1 + 16, y2 - 8, 5.5, [5.5, 3.5, 1.5], 'pipe', post=6)
    fence(f, x1 + 20, y1, x1 + 20, y2 - 8, 5.5, [5.5, 3.5, 1.5], 'pipe', post=6)
    objs.append(f)

    # ---- Turnout board fences (wood, 3 rails), split into short segments
    tos = [R(245, 162, 608, 270), R(612, 162, 983, 270), R(138, 537, 245, 697.85), R(138, 697.85, 245, 858.5), R(138, 858.5, 245, 1001.3)]
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
    x1, y1, x2, y2 = R(983, 935, 1128, 995)
    o = Obj('compost')
    for i in range(4):
        xx = x1 + 4 + i * (x2 - x1 - 8) / 3
        box(o, xx - 0.5, y1 + 2, xx + 0.5, y2 - 2, 0, 4.5, 'concrete_w', 'concrete_w')
    box(o, x1 + 3.5, y2 - 3, x2 - 3.5, y2 - 2, 0, 4.5, 'concrete_w', 'concrete_w')
    objs.append(o)
    # dumpsters
    # one dumpster in a 12' x 12' C-shaped enclosure, weathered wood 6' high, open to the west toward the drive, its
    # west side on the existing barn's front line (owner, 2026-10-19)
    o = Obj('dumpsters'); x1, y1, x2, y2 = R(983, 1001, 1019, 1037)
    ground_poly(G, x1, y1, x2, y2, 'concrete')
    box(o, x1, y2 - 0.5, x2, y2, 0, 6.0, 'oldwood', 'oldwood')          # north
    box(o, x1, y1, x2, y1 + 0.5, 0, 6.0, 'oldwood', 'oldwood')          # south
    box(o, x2 - 0.5, y1, x2, y2, 0, 6.0, 'oldwood', 'oldwood')          # east (back)
    box(o, x2 - 7.4, y1 + 2.4, x2 - 1.0, y2 - 2.4, 0, 5.2, 'dumpster', 'dumpster')
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
