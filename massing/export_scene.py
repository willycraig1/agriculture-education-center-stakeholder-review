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
    'arena':     ("Covered arena", 'arena', 3, 'arena'),
    'grooming':  ("Grooming area", 'arena', 2, 'grooming'),
    'arenarail': ("Arena rail", 'arena', 3, 'arena'),
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
}
PENS = ["Holding pen"] * 5 + ["Handling yard"]

# turnouts in scene order (scene.build's `tos` list)
TURNOUTS = [("Cattle turnout B", 3), ("Cattle turnout A", 2), ("Small animal turnout A", 2), ("Small animal turnout B", 3)]


def r(v, n=2):
    return [round(float(x), n) for x in v]


def ground_meta(face, mat):
    """Level for a ground face: turnouts, pen dirt and the arena floor phase with what they serve."""
    c = face['p'].mean(0)
    if mat == 'turnout':
        for k, rc in enumerate([scene.R(245, 168, 608, 275), scene.R(612, 168, 965, 275),
                                scene.R(138, 537, 245, 868), scene.R(138, 868, 245, 990)]):
            if rc[0] <= c[0] <= rc[2] and rc[1] <= c[1] <= rc[3]:
                return TURNOUTS[k][0], TURNOUTS[k][1]
    if mat == 'arenadirt':
        return "Arena floor", 3
    if mat == 'dirt':
        return ("Compost pad", 1) if c[1] < -310 else ("Holding pens", 1)
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
    tos = [scene.R(245, 168, 608, 275), scene.R(612, 168, 965, 275), scene.R(138, 537, 245, 868), scene.R(138, 868, 245, 990)]
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
        ground=ground,
        objects=out_objs,
        trees=[dict(x=round(x, 1), y=round(y, 1), kind=k, s=round(s, 2)) for x, y, k, s in scene.trees()],
    )
    path = os.path.join(HERE, 'scene-data.js')
    with open(path, 'w') as fh:
        fh.write('// ' + data['about'] + '\nwindow.SCENE = ')
        json.dump(data, fh, separators=(',', ':'))
        fh.write(';\n')
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


if __name__ == '__main__':
    main()
