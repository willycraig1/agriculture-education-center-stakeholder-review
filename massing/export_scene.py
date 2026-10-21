"""Export the watercolor massing (Watercolor_Rendering_Working/scripts/scene.py) for the 3D viewer.

scene.py stays the one source of geometry: the watercolor pipeline renders it, this script dumps it to
massing/scene-data.js (window.SCENE = {...}) for massing/index.html. Materials come from render.py's MAT table;
Levels and program follow the deck's barnyard data (slides/data/ag-area.js ids noted beside each entry).

    .venv/bin/python massing/export_scene.py
"""
import ast, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SCRIPTS = os.path.join(ROOT, 'Watercolor_Rendering_Working', 'scripts')
sys.path.insert(0, SCRIPTS)
import scene  # noqa: E402


def render_constants():
    """MAT, CAM, COW_AT and TRACTOR_AT read from render.py without running it."""
    tree = ast.parse(open(os.path.join(SCRIPTS, 'render.py')).read())
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name == 'MAT':
                out['MAT'] = ast.literal_eval(node.value)
            elif name == 'CAM':
                kw = {k.arg: ast.literal_eval(k.value) for k in node.value.keywords if k.arg in ('pos', 'target', 'hfov_deg')}
                out['CAM'] = kw
            elif name in ('COW_AT', 'TRACTOR_AT'):
                out[name] = ast.literal_eval(node.value.args[0])
    return out


# name -> (label, program, level, ag-area id). Level 0 = existing building kept as is.
META = {
    'cattleA':   ("Cattle barn A", 'cattle', 2, 'cattle-a'),
    'cattleB':   ("Cattle barn B", 'cattle', 3, 'cattle-b'),
    'cattleA_gates': ("Cattle barn A", 'cattle', 2, 'cattle-a'),
    'swineA_n_pens': ("Small animal barn A, north wing", 'swine', 2, 'small-a'),
    'swineA_s_pens': ("Small animal barn A, south wing", 'swine', 2, 'small-a2'),
    'smallB_pens':   ("Small animal barn B", 'swine', 3, 'small-b'),
    'cattleB_gates': ("Cattle barn B", 'cattle', 3, 'cattle-b'),
    'arena':     ("Covered arena", 'arena', 3, 'arena'),
    'grooming':  ("Grooming area", 'arena', 2, 'grooming'),
    'arenarail': ("Arena rail", 'arena', 3, 'arena'),
    'bleachers': ("Arena bleachers", 'arena', 3, 'arena'),
    'swineA_n':  ("Small animal barn A, north wing", 'swine', 2, 'small-a'),
    'swineA_s':  ("Small animal barn A, south wing", 'swine', 2, 'small-a2'),
    'smallB':    ("Small animal barn B", 'swine', 3, 'small-b'),
    'dogtrot':   ("Small animal barn A, dogtrot", 'swine', 2, 'dogtrot'),
    'feed':      ("Feed storage", 'circulation', 2, 'feed'),
    'bedding':   ("Bedding storage", 'circulation', 2, 'bedding'),
    'exbarn':    ("Existing barn", 'existing', 0, 'existing-barn'),
    'leanto':    ("Existing pens shed roof", 'existing', 0, 'existing-pens'),
    'excover':   ("Existing barn, covered concrete", 'existing', 0, 'existing-barn'),
    'expens':    ("Existing cattle pens", 'existing', 0, 'existing-pens'),
    'compost':   ("Compost bins", 'circulation', 1, 'compost'),
    'dumpsters': ("Dumpster enclosure", 'circulation', 1, 'dumpster'),
    'chute':     ("Handling chute", 'cattle', 1, 'handling'),
    'alleygate': ("Holding pens, alley gate", 'cattle', 1, 'holding'),
}
PENS = ["Holding pen"] * 5 + ["Handling yard"]

# turnouts in scene order (scene.build's `tos` list)
TURNOUTS = [("Cattle turnout B", 3), ("Cattle turnout A", 2), ("Small animal turnout A", 2), ("Small animal turnout A", 2),
            ("Small animal turnout B", 3)]       # barn A's turnout is two yards, divided at the dogtrot


def animals():
    """Scale figures for the viewer (owner, 2026-10-19): a student leading a steer south of cattle barn B and another in
    the arena; a cow in every cattle pen (barns A and B, the 7 existing pens, and holding pens 1 to 5); pigs in the small animal barn and
    its turnout. Each: [x, y, heading (radians, 0 = facing east), level]."""
    S, R = scene.S, scene.R
    rng = np.random.default_rng(9)
    jit = lambda v=0.6: float(rng.uniform(-v, v))
    cows, pigs, students = [], [], []
    for (x1, y1, x2, y2), lvl in ((R(645, 270, 893, 460), 2), (R(322, 270, 572, 460), 3)):
        ym = (y1 + y2) / 2; ai = 8.0 * (y2 - y1) / 64.0
        bay = (x2 - x1) / 7
        for i in range(7):
            x = x1 + (i + 0.5) * bay
            for side in (-1, 1):            # anywhere in its 12' x 24' pen, any way round (owner, 2026-10-19)
                head = float(rng.uniform(0, 2 * np.pi))
                along = abs(np.cos(head)) > 0.7                      # lying along the pen's 12' width: keep it in the middle
                xx = x + jit(0.6 if along else 2.5)
                d = float(rng.uniform(5, 20))                        # distance from the aisle edge into the pen
                cows.append([round(xx, 2), round(ym + side * (ai + d), 2), round(head, 2), lvl])
    ex1, ex2, eyn = 983 / S, 1220 / S, -775 / S
    for i in range(7):                                                 # existing pens: at the feeders on the aisle
        cows.append([round(ex1 + (i + 0.5) * (ex2 - ex1) / 7 + jit(1), 2), round(eyn + 14 + jit(2), 2), round(-np.pi / 2 + jit(.4), 2), 0])
    for rc in (R(983, 270, 1109, 415), R(983, 415, 1109, 555), R(1132.6, 270, 1258.5, 415),
               R(1132.6, 415, 1258.5, 555), R(1132.6, 555, 1258.5, 680)):   # one in each holding pen (pens 1 to 5)
        hx1, hy1, hx2, hy2 = rc
        cows.append([round(float(rng.uniform(hx1 + 6, hx2 - 6)), 2), round(float(rng.uniform(hy1 + 6, hy2 - 6)), 2),
                     round(float(rng.uniform(0, 2 * np.pi)), 2), 1])
    sxm = (245 / S + 353 / S) / 2
    for y_px, n in ((560, 2), (610, 1), (650, 1), (740, 1), (800, 1)):    # pigs in barn A's pens, both wings
        for k in range(n):
            side = 1 if (y_px + k) % 2 else -1
            pigs.append([round(sxm + side * 9 + jit(1.5), 2), round(-y_px / S + jit(1.5), 2), round(float(rng.uniform(0, 6.28)), 2), 2])
    tx1, ty1, tx2, ty2 = R(138, 537, 245, 697.85)
    for _ in range(4):                                                 # and a few out in its north turnout
        pigs.append([round(float(rng.uniform(tx1 + 5, tx2 - 5)), 2), round(float(rng.uniform(ty1 + 6, ty2 - 6)), 2), round(float(rng.uniform(0, 6.28)), 2), 2])
    bx1, by1, bx2, by2 = R(322, 270, 572, 460)                         # south of cattle barn B, in the 24' gap
    students.append([round((bx1 + bx2) / 2 - 10, 2), round(by1 - 12, 2), 0.0, 0])
    ax1, ay1, ax2, ay2 = R(645, 530, 893, 680)                         # in the arena
    students.append([round((ax1 + ax2) / 2 + 6, 2), round((ay1 + ay2) / 2 - 4, 2), 3.14, 3])
    # a pickup with a 16' stock trailer on the lane between the arena and the Bud Box, heading north (owner, 2026-10-19)
    hx1, hy1, hx2, hy2 = R(983, 555, 1109, 680)
    lane_x = ((893 / S + 3.0) + hx1) / 2                              # between the arena's east overhang and the yard
    vehicles = [[round(lane_x, 2), round(hy2 - 4, 2), round(np.pi / 2, 3), 1]]
    return dict(cows=cows, pigs=pigs, students=students, vehicles=vehicles)


def r(v, n=2):
    return [round(float(x), n) for x in v]


def ground_meta(face, mat):
    """Level for a ground face: turnouts, pen dirt and the arena floor phase with what they serve."""
    c = face['p'].mean(0)
    if mat == 'turnout':
        for k, rc in enumerate([scene.R(245, 162, 608, 270), scene.R(612, 162, 983, 270),
                                scene.R(138, 537, 245, 697.85), scene.R(138, 697.85, 245, 858.5), scene.R(138, 858.5, 245, 1001.3)]):
            if rc[0] <= c[0] <= rc[2] and rc[1] <= c[1] <= rc[3]:
                return TURNOUTS[k][0], TURNOUTS[k][1]
    if mat == 'arenadirt':
        return "Arena floor", 3
    if mat == 'dirt':   # sand: the compost pad, the existing pens, cattle barns A and B, or the holding pens
        for label, lvl, rc in [("Compost pad", 1, scene.R(983, 935, 1128, 995)), ("Existing cattle pens", 0, scene.R(983, 680, 1220, 775)),
                               ("Cattle barn A", 2, scene.R(645, 270, 893, 460)), ("Cattle barn B", 3, scene.R(322, 270, 572, 460))]:
            if rc[0] - 1 <= c[0] <= rc[2] + 1 and rc[1] - 1 <= c[1] <= rc[3] + 1:
                return label, lvl
        return "Holding pens", 1
    return None, 0


def main():
    rc = render_constants()
    objs = scene.build()
    out_objs, ground = [], []
    for o in objs:
        if o.ground:
            for f in o.faces:
                label, lvl = ground_meta(f, f['mat'])
                ground.append(dict(p=[r(p) for p in f['p']], m=f['mat'], level=lvl, label=label))
            continue
        name = o.name
        faces = o.faces
        if name == 'arena':  # the grooming box is drawn inside the arena object (bias 200); split it out
            groom = [f for f in faces if f['bias'] == 200.0]
            faces = [f for f in faces if f['bias'] != 200.0]
            out_objs.append(pack('grooming', groom, []))
        if name.startswith('pen'):
            i = int(name[3:].split('_')[0])
            label, prog, lvl, gid = PENS[i], 'cattle', 1, 'holding'
            out_objs.append(pack(name, faces, o.lines, (label, prog, lvl, gid), group='pens'))
            continue
        if name.startswith('to') and name[2:].isdigit():
            out_objs.append(pack(name, faces, o.lines, ("Turnout fence", 'pasture', 0, ''), group='turnoutfence'))
            continue
        out_objs.append(pack(name, faces, o.lines))

    # turnout fences take the Level of the turnout they bound
    tos = [scene.R(245, 162, 608, 270), scene.R(612, 162, 983, 270), scene.R(138, 537, 245, 697.85), scene.R(138, 697.85, 245, 858.5), scene.R(138, 858.5, 245, 1001.3)]
    for ob in out_objs:
        if ob.get('group') == 'turnoutfence':
            p = np.array([q for ln in ob['lines'] for q in ln['p']])
            c = p.mean(0)
            for k, t in enumerate(tos):
                if t[0] - 1 <= c[0] <= t[2] + 1 and t[1] - 1 <= c[1] <= t[3] + 1:
                    ob['label'] = TURNOUTS[k][0] + " fence"; ob['level'] = TURNOUTS[k][1]
                    break

    data = dict(
        about="Generated by massing/export_scene.py from Watercolor_Rendering_Working/scripts/scene.py. Do not edit.",
        units="feet; x east, y north, z up",
        sun=r(scene.SUN, 4),
        mat={k: r(v, 3) for k, v in rc['MAT'].items()},
        camera=rc['CAM'],
        cow=list(rc['COW_AT']), tractor=list(rc['TRACTOR_AT']),
        animals=animals(),
        ground=ground,
        objects=out_objs,
        trees=[dict(x=round(x, 1), y=round(y, 1), kind=k, s=round(s, 2)) for x, y, k, s in scene.trees()],
    )
    path = os.path.join(HERE, 'scene-data.js')
    with open(path, 'w') as fh:
        fh.write('// ' + data['about'] + '\nwindow.SCENE = ')
        json.dump(data, fh, separators=(',', ':'))
        fh.write(';\n')
    stamp_viewer(path)
    nf = sum(len(o['faces']) for o in out_objs)
    nl = sum(len(o['lines']) for o in out_objs)
    print(f"{path}: {len(out_objs)} objects, {nf} faces, {nl} lines, {len(ground)} ground, "
          f"{os.path.getsize(path) / 1024:.0f} KB")


def pack(name, faces, lines, meta=None, group=None):
    label, prog, lvl, gid = meta or META.get(name, (name, 'existing', 0, ''))
    allp = np.vstack([f['p'] for f in faces] + [l['p'] for l in lines]) if (faces or lines) else np.zeros((1, 3))
    lo, hi = allp.min(0), allp.max(0)
    d = dict(name=name, label=label, program=prog, level=lvl, id=gid,
             bbox=[r(lo), r(hi)],
             faces=[dict(p=[r(p) for p in f['p']], m=f['mat']) for f in faces],
             lines=[dict(p=[r(p) for p in l['p']], m=l['mat'], w=round(l['w'], 2)) for l in lines])
    if group:
        d['group'] = group
    return d


def stamp_viewer(path):
    """Version the viewer's script tag for this data file with its content hash, so a reload never runs stale data."""
    import hashlib, re
    name = os.path.basename(path)
    v = hashlib.sha1(open(path, 'rb').read()).hexdigest()[:10]
    html = os.path.join(HERE, 'index.html')
    s = open(html).read()
    open(html, 'w').write(re.sub(r'src="' + re.escape(name) + r'(\?v=\w+)?"', f'src="{name}?v={v}"', s))


if __name__ == '__main__':
    main()
