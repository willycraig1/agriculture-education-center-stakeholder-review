"""Export the campus site around the barnyard massing for the 3D viewer.

Reads the deck's generated site plan (slides/data/site-map.js, from tools/build_site_map.py) and barnyard plan
(slides/data/ag-area.js, from tools/build_ag_area.py) and writes massing/site-data.js (window.SITE = {...}) plus
massing/aerial.jpg, all in the massing's frame (scene.py feet: x east, y "plan north" up, z up).

Frames: site map (presentation units) -> barnyard diagram feet via site-map.js `diagram_to_presentation`;
diagram feet -> scene.py feet by a similarity fitted to ten barnyard footprints traced in both (residual < 0.6 ft).
Plan north is the diagram's up; true north is `north_cw_from_up` from it (ag-area.js).

Run after the deck's build tools:   .venv/bin/python massing/export_site.py
"""
import json, math, os, re
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from shapely.geometry import Polygon, MultiPolygon, Point, LineString, box
from shapely.ops import unary_union
import shapely
from svgelements import Path as SvgPath, Move, Close

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
S = 2.95   # scene.py's plan px per ft


def load_js(path):
    s = open(path).read()
    return json.loads(s[s.index('{'):s.rstrip().rstrip(';').rindex('}') + 1])


SM = load_js(os.path.join(ROOT, 'slides', 'data', 'site-map.js'))
AG = load_js(os.path.join(ROOT, 'slides', 'data', 'ag-area.js'))
ELEM = {e['id']: e for e in AG['elements']}

# ---------------------------------------------------------------- frames
M_DP = complex(*SM['barnyard']['diagram_to_presentation']['m'])
T_DP = complex(*SM['barnyard']['diagram_to_presentation']['t'])


def fit_diagram_to_scene():
    """Similarity (with the y flip) from diagram feet to scene.py feet, fitted on footprints traced in both."""
    pairs = [('cattle-a', (645, 270, 893, 460)), ('cattle-b', (322, 270, 572, 460)), ('arena', (645, 530, 893, 680)),
             ('small-a', (245, 537, 353, 680)), ('small-a2', (245, 715.7, 353, 858.5)), ('small-b', (245, 858.5, 353, 1001.3)),
             ('existing-barn', (983, 775, 1220, 925)), ('feed', (525, 560, 572, 680)),
             ('holding-1', (1132.6, 555, 1258.5, 680)), ('existing-pens', (983, 680, 1220, 750))]   # pens flush with the barn's west face
    A, B = [], []
    for k, (a, b, c, d) in pairs:
        e = ELEM[k]
        x0, y0, x1, y1 = e['x'], e['y'], e['x'] + e['w'], e['y'] + e['h']
        for (u, v), (p, q) in zip([(x0, y0), (x1, y0), (x0, y1), (x1, y1)], [(a, b), (c, b), (a, d), (c, d)]):
            A.append(complex(u, -v)); B.append(complex(p / S, -q / S))
    A, B = np.array(A), np.array(B)
    X = np.stack([A, np.ones_like(A)], 1)
    (m, t), *_ = np.linalg.lstsq(X, B, rcond=None)
    resid = np.abs(X @ np.array([m, t]) - B).max()
    return m, t, resid


M_DS, T_DS, RESID = fit_diagram_to_scene()


def d2s(x, y):
    """diagram feet -> scene feet"""
    z = M_DS * complex(x, -y) + T_DS
    return (round(z.real, 2), round(z.imag, 2))


def m2s(x, y):
    """site-map units -> scene feet"""
    q = (complex(x, y) - T_DP) / M_DP
    return d2s(q.real, q.imag)


# ---------------------------------------------------------------- site-map svg, walked with transforms
NS = '{http://www.w3.org/2000/svg}'


def parse_tf(t):
    M = np.eye(3)
    for name, args in re.findall(r'(\w+)\(([^)]*)\)', t or ''):
        a = [float(v) for v in re.split(r'[ ,]+', args.strip()) if v]
        if name == 'matrix':
            T = np.array([[a[0], a[2], a[4]], [a[1], a[3], a[5]], [0, 0, 1]])
        elif name == 'translate':
            T = np.array([[1, 0, a[0]], [0, 1, a[1] if len(a) > 1 else 0], [0, 0, 1]])
        elif name == 'rotate':
            r = np.radians(a[0]); c, s = np.cos(r), np.sin(r)
            T = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
            if len(a) == 3:
                T = np.array([[1, 0, a[1]], [0, 1, a[2]], [0, 0, 1]]) @ T @ np.array([[1, 0, -a[1]], [0, 1, -a[2]], [0, 0, 1]])
        elif name == 'scale':
            T = np.diag([a[0], a[1] if len(a) > 1 else a[0], 1])
        else:
            continue
        M = M @ T
    return M


ITEMS = []


def walk(e, M, layers, hidden):
    tag = e.tag.replace(NS, '')
    M = M @ parse_tf(e.get('transform'))
    hidden = hidden or e.get('display') == 'none'
    if tag in ('g', 'svg'):
        for c in e:
            walk(c, M, layers + ([e.get('id')] if e.get('id') else []), hidden)
    else:
        ITEMS.append(dict(tag=tag, e=e, M=M, layers=layers, hidden=hidden))


walk(ET.fromstring(SM['svg']), np.eye(3), [], False)


def items(layer, tag=None, sub=None):
    for it in ITEMS:
        ly = it['layers']
        if len(ly) > 1 and ly[1] == layer and not it['hidden'] and (tag is None or it['tag'] == tag) \
                and (sub is None or sub in ly[2:]):
            yield it


def apply(M, pts):
    P = np.c_[np.array(pts, float), np.ones(len(pts))] @ M.T
    return [m2s(x, y) for x, y in P[:, :2]]


def rings(it):
    """Closed rings (scene feet) of a path / polygon / polyline / rect."""
    e, M, tag = it['e'], it['M'], it['tag']
    if tag in ('polygon', 'polyline'):
        v = [float(a) for a in re.split(r'[ ,]+', e.get('points').strip())]
        return [apply(M, list(zip(v[::2], v[1::2])))]
    if tag == 'rect':
        x, y, w, h = (float(e.get(k, 0)) for k in ('x', 'y', 'width', 'height'))
        return [apply(M, [(x, y), (x + w, y), (x + w, y + h), (x, y + h)])]
    if tag == 'path':
        out, cur = [], []
        for seg in SvgPath(e.get('d')):
            if isinstance(seg, Move):
                if len(cur) > 2: out.append(cur)
                cur = [(seg.end.x, seg.end.y)]
            elif isinstance(seg, Close):
                if len(cur) > 2: out.append(cur)
                cur = []
            else:
                n = 1 if type(seg).__name__ == 'Line' else 8
                cur += [(seg.point(t / n).x, seg.point(t / n).y) for t in range(1, n + 1)]
        if len(cur) > 2: out.append(cur)
        return [apply(M, r) for r in out]
    return []


def to_polys(rs, evenodd=True, simplify=0.0):
    """Rings -> list of {o: outer, h: [holes]}, treating nested rings as holes (even-odd)."""
    geoms = [Polygon(r).buffer(0) for r in rs if len(r) > 2]
    geoms = [g for g in geoms if not g.is_empty]
    if evenodd and len(geoms) > 1:
        acc = geoms[0]
        for g in geoms[1:]:
            acc = acc.symmetric_difference(g)
        geoms = [acc]
    out = []
    for g in geoms:
        if simplify: g = g.simplify(simplify)
        for p in (g.geoms if isinstance(g, MultiPolygon) else [g]):
            if p.is_empty or p.area < 4: continue
            out.append(dict(o=rnd(p.exterior.coords), h=[rnd(i.coords) for i in p.interiors if Polygon(i).area > 4]))
    return out


def rnd(cs):
    cs = list(cs)
    if len(cs) > 1 and cs[0] == cs[-1]: cs = cs[:-1]
    return [[round(x, 1), round(y, 1)] for x, y in cs]


def line_pts(it):
    e = it['e']
    v = [float(a) for a in re.split(r'[ ,]+', e.get('points').strip())]
    return rnd(apply(it['M'], list(zip(v[::2], v[1::2]))))


def text_of(it):
    e = it['e']
    return ''.join(e.itertext()).strip()


def scene_objects():
    """The massing's objects (Watercolor_Rendering_Working/scripts/scene.py), for checks against what it already draws."""
    import sys
    sys.path.insert(0, os.path.join(ROOT, 'Watercolor_Rendering_Working', 'scripts'))
    import scene
    return scene.build()


# ---------------------------------------------------------------- unfinished barn
def frame_of(o):
    """The unfinished (poultry) barn's frame from its surveyed roof outline: centre, long-axis angle, and the
    architect's post-to-post size (sheet "A2.0 Unfinished Barn": 46'-8" x 35'-6", 2'-5 5/8" overhangs at the sides,
    2'-2 1/4" at the ends), in scene feet."""
    r = Polygon(o).minimum_rotated_rectangle
    cs = list(r.exterior.coords)[:4]
    edges = sorted(((math.dist(cs[i], cs[(i + 1) % 4]), cs[i], cs[(i + 1) % 4]) for i in range(4)), reverse=True)
    _, a, b = edges[0]
    k = abs(M_DS)
    return dict(c=[round(r.centroid.x, 2), round(r.centroid.y, 2)], ang=round(math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])), 2),
                L=round(46.667 * k, 2), W=round(35.5 * k, 2), ovs=round(2.47 * k, 2), ove=round(2.19 * k, 2),
                outline_ft=[round(edges[0][0], 1), round(edges[2][0], 1)])


# ---------------------------------------------------------------- road embankment
def road_embankment(roads, wet, elem):
    """State Road 72 on fill, from the survey's spot elevations (tools/read_survey_spots.py).

    The road-area is SR 72 plus the entry drive. SR 72 (the part wider than 14') is set at its surveyed average above
    the natural grade beside it, with 2:1 shoulders; the entry drive ramps down from the road over 60' and runs about
    a foot above grade (as surveyed) before easing to grade at the parking lot it now runs under.
    """
    spots = json.load(open(os.path.join(ROOT, 'drawings', 'data', 'survey-spots.json')))['spots']
    pts = [(Point(m2s(*s_['map'])), s_['z']) for s_ in spots]
    R = unary_union([Polygon(p['o'], p['h']).buffer(0) for p in roads])
    sr72 = R.buffer(-7, join_style='mitre').buffer(7, join_style='mitre').intersection(R)
    sr72 = unary_union([g for g in getattr(sr72, 'geoms', [sr72]) if g.area > 20000])
    on_road = [z for p, z in pts if sr72.contains(p)]
    near = sr72.buffer(150).difference(sr72.buffer(30))
    grade = [z for p, z in pts if near.contains(p)]
    road_z, grade_z = float(np.mean(on_road)), float(np.median(grade))
    H = round(road_z - grade_z, 1)
    lot = Polygon([d2s(x, y) for x, y in elem['parking']['outline']]).buffer(0)
    RAMP = 80.0                      # the entry drive ramps from the road to grade over its first 80' (owner, 2026-10-19)

    def surface(x, y):
        p = Point(x, y)
        d = sr72.distance(p)
        if d < .05: return H
        return H * (1 - d / RAMP) if d < RAMP else -0.04

    def surf(x, y):
        p = Point(x, y)
        z = surface(x, y)
        if lot.buffer(30).contains(p):   # ease to grade where the drive runs under the parking lot
            z *= min(1.0, max(0.0, lot.exterior.distance(p) / 30.0)) if not lot.contains(p) else 0.0
        return z

    def mesh(poly, zf, seg):
        verts, tris, index = [], [], {}
        for part in getattr(poly, 'geoms', [poly]):
            if part.geom_type != 'Polygon' or part.area < 1: continue
            for tri in shapely.constrained_delaunay_triangles(shapely.segmentize(part, seg)).geoms:
                ids = []
                for x, y in list(tri.exterior.coords)[:3]:
                    k = (round(x, 1), round(y, 1))
                    if k not in index:
                        index[k] = len(verts) // 3
                        verts += [k[0], k[1], round(zf(x, y), 2)]
                    ids.append(index[k])
                if len(set(ids)) == 3: tris += ids
        return dict(v=verts, t=tris)

    top = mesh(R, surf, 10.0)
    # shoulders: 2:1 off SR 72, a short slope off the drive; outer edge at grade; not into the water features
    band = sr72.buffer(2 * H).union(R.intersection(sr72.buffer(RAMP)).buffer(2.5)).difference(R).difference(wet).difference(lot)
    edge = R.boundary
    shoulder = mesh(band, lambda x, y: surf(*nearest_on(edge, x, y)) if edge.distance(Point(x, y)) < .05 else 0.0, 8.0)
    return dict(height_ft=H, road_elev=round(road_z, 2), grade_elev=round(grade_z, 2), n_road=len(on_road), n_grade=len(grade),
                top=top, shoulder=shoulder)


def nearest_on(line, x, y):
    q = line.interpolate(line.project(Point(x, y)))
    return q.x, q.y


# ---------------------------------------------------------------- layers
def main():
    out = dict(about="Generated by massing/export_site.py from slides/data/site-map.js and ag-area.js. Do not edit.",
               frame_fit_resid_ft=round(float(RESID), 2),
               north_cw_from_up=AG.get('north_cw_from_up', 0))

    # property boundary (the site ground) and surveyed property lines
    out['boundary'] = to_polys(rings(next(items('ground', 'path'))))
    out['property'] = [line_pts(it) for it in items('property', 'polyline')]

    # land areas and paddocks, with their labels
    out['areas'] = [dict(kind=it['e'].get('class').split()[1], polys=to_polys(rings(it), simplify=0.5))
                    for it in items('land', 'path', 'pasture-areas')]
    pads = []
    for it in items('paddocks', 'path', 'paddock-fills'):
        cls = it['e'].get('class').split()
        pads.append(dict(kind=cls[1], polys=to_polys(rings(it))))
    tags = []
    for it in items('paddocks', 'text'):
        p = apply(it['M'], [(float(it['e'].get('x', 0)), float(it['e'].get('y', 0)))])[0]
        t = text_of(it)
        if re.search(r'\d+(\.\d+)?\s*AC', t, re.I):
            tags.append(dict(t=t, p=list(p)))
    for pd in pads:   # pair each paddock with the acreage label inside it
        poly = Polygon(pd['polys'][0]['o'])
        hit = [t for t in tags if poly.buffer(30).contains(Point(t['p']))]
        pd['label'] = hit[0]['t'] if hit else ''
    out['paddocks'] = pads
    # fences: the bonus pasture's come in at Level 3 (levels.js pasture row); the rest at Level 1
    bonus = unary_union([Polygon(p['o']).buffer(25) for a in out['areas'] if a['kind'] == 'bonus' for p in a['polys']])
    out['fences'] = []
    for it in items('paddocks', 'polyline', 'fence-lines'):
        pts = line_pts(it)
        ln = LineString(pts)
        out['fences'].append(dict(id=it['e'].get('id'), p=pts,
                                  level=3 if ln.intersection(bonus).length > .6 * ln.length else 1))
    for pd in pads:
        pd['level'] = 3 if pd['kind'] == 'bonus' else 1

    # water
    water = []
    for it in items('water', 'path'):
        cid = it['e'].get('id') or it['e'].get('class') or ''
        if it['layers'][2:] and it['layers'][2] == 'historic-slough-floor':
            cid = 'historic-slough-floor'
        if cid in ('slough', 'historic-slough', 'pond existing', 'pond proposed', 'historic-slough-floor'):
            water.append(dict(kind=cid.replace(' ', '-'), polys=to_polys(rings(it), simplify=0.3)))
    out['water'] = water

    # Water features as banked basins: the drawn outline is the top of bank; the water stands 3' below it
    # (placeholder until the civil grading is in). The bank runs in about 4:1 (12'), less where a feature is narrow.
    TOB, DEPTH = -0.2, 3.0
    basins, wet = [], []
    for w in water:
        if w['kind'] not in ('slough', 'pond-existing', 'pond-proposed'): continue
        for pp in w['polys']:
            poly = Polygon(pp['o'], pp['h']).buffer(0)
            if poly.is_empty: continue
            wet.append(poly)
            inner = None
            for inset in (12, 10, 8, 6, 5, 4, 3):
                inner = poly.buffer(-inset, join_style='mitre').buffer(0)
                if not inner.is_empty and inner.area > .25 * poly.area: break
            band = poly.difference(inner)
            seg = 8.0 if poly.length > 3000 else 4.0
            verts, tris, index = [], [], {}
            edge = poly.boundary
            for part in (band.geoms if hasattr(band, 'geoms') else [band]):
                if part.geom_type != 'Polygon' or part.area < 1: continue
                for tri in shapely.constrained_delaunay_triangles(shapely.segmentize(part, seg)).geoms:
                    ids = []
                    for x, y in list(tri.exterior.coords)[:3]:
                        k = (round(x, 1), round(y, 1))
                        if k not in index:
                            index[k] = len(verts) // 3
                            z = TOB if edge.distance(Point(x, y)) < .05 else TOB - DEPTH
                            verts += [round(x, 2), round(y, 2), round(z, 2)]
                        ids.append(index[k])
                    if len(set(ids)) == 3: tris += ids
            surf = to_polys([list(inner.exterior.coords)] if inner.geom_type == 'Polygon' else [], evenodd=False) \
                if inner.geom_type == 'Polygon' else [q for g in inner.geoms for q in to_polys([list(g.exterior.coords)], evenodd=False)]
            basins.append(dict(kind=w['kind'], v=verts, t=tris, water=surf, inset=inset))
    out['basins'] = dict(tob=TOB, depth=DEPTH, list=basins)
    WET = unary_union(wet)

    def cut(polys):   # take the water features out of a ground layer
        g = unary_union([Polygon(p['o'], p['h']).buffer(0) for p in polys]).difference(WET)
        return [dict(o=rnd(q.exterior.coords), h=[rnd(i.coords) for i in q.interiors])
                for q in (g.geoms if hasattr(g, 'geoms') else [g]) if q.geom_type == 'Polygon' and q.area > 4]
    out['boundary'] = cut(out['boundary'])
    for pd in pads: pd['polys'] = cut(pd['polys']) or pd['polys']
    cx, cy = 245, -215
    out['outside'] = cut([dict(o=[[cx - 16000, cy - 16000], [cx + 16000, cy - 16000], [cx + 16000, cy + 16000], [cx - 16000, cy + 16000]], h=[])])

    # canopy, and trees scattered through it; surveyed trees as points
    canopy = cut(to_polys(rings(next(items('canopy', 'path'))), simplify=1.0))
    out['canopy'] = canopy

    # keep scattered trees off the barnyard, campus, roads, and buildings
    def el_poly(e):
        pts = e.get('outline') or [[e['x'], e['y']], [e['x'] + e['w'], e['y']], [e['x'] + e['w'], e['y'] + e['h']], [e['x'], e['y'] + e['h']]]
        return Polygon([d2s(x, y) for x, y in pts]).buffer(0)
    # Woods are cleared only under buildings, yards, and pens (and off the roads). Trees under the parking lot,
    # its swale island, walks, and turnouts stay: they stand there today, and the lot is being fitted around them.
    built = unary_union([el_poly(e) for e in AG['elements'] if e.get('kind') in ('building', 'yard', 'canopy')
                         and not e['id'].startswith('turnout')])
    roads = unary_union([Polygon(p['o'], p['h']).buffer(0) for it in items('campus', 'path') if it['e'].get('id') == 'road-area'
                         for p in to_polys(rings(it))])
    keep_out = [built.buffer(8).union(roads.buffer(-5))]   # trunks may stand at a drive's edge, as along the existing drive
    # The survey located every tree around the campus and the drive, so no filler trees there: none inside the surveyed
    # area (the hull of the surveyed trees) or within 30' of a surveyed tree (owner, 2026-10-19)
    from shapely.geometry import MultiPoint
    _sv_pts = [Point(*apply(it['M'], [(float(it['e'].get('cx')), float(it['e'].get('cy')))])[0]) for it in items('trees', 'circle')]
    if _sv_pts:
        keep_out.append(MultiPoint(_sv_pts).convex_hull.union(unary_union([q.buffer(30) for q in _sv_pts])))
    rng = np.random.default_rng(5)
    scatter = []
    # the north triangle pasture: the site area between SR 72 and Cowpen Slough, north of the campus
    north_tri = unary_union([Polygon(p['o']).buffer(40) for a in out['areas'] if a['kind'] == 'site' for p in a['polys']
                             if Polygon(p['o']).centroid.x < 0 and Polygon(p['o']).centroid.y > 600])
    for cp in canopy:
        poly = Polygon(cp['o'], cp['h']).buffer(-6)
        if poly.is_empty: continue
        x0, y0, x1, y1 = poly.bounds
        step = 30.0
        for gx in np.arange(x0, x1, step):
            for gy in np.arange(y0, y1, step):
                x, y = gx + rng.uniform(0, step), gy + rng.uniform(0, step)
                pt = Point(x, y)
                if poly.contains(pt) and not any(k.contains(pt) for k in keep_out):
                    u = rng.uniform()
                    if north_tri.contains(pt):   # slash pines: almost all in the north triangle pasture
                        kind = 1 if u < .62 else (0 if u < .9 else 2)
                    else:                         # live oak hammock with sabal (cabbage) palms mixed in
                        kind = 0 if u < .6 else (2 if u < .98 else 1)
                    scatter.append([round(x, 1), round(y, 1), round(float(rng.uniform(.75, 1.35)), 2), kind])   # 0 oak, 1 pine, 2 palm
    out['canopy_trees'] = scatter

    # a herd of 15 grazing the open pasture over the historic slough bed (owner, 2026-10-19): the largest open piece
    # of the bed inside the site paddocks, clear of the woods; head-to-tail spacing at least 9'
    hs = unary_union([Polygon(p['o'], p['h']).buffer(0) for w in water if w['kind'] == 'historic-slough' for p in w['polys']])
    site_pads = unary_union([Polygon(p['o'], p['h']).buffer(0) for pd in pads if pd['kind'] == 'site' for p in pd['polys']])
    graze = hs.intersection(site_pads).difference(unary_union([Polygon(c['o'], c['h']).buffer(0) for c in canopy]).buffer(10)).buffer(-6)
    herd = []
    if not graze.is_empty:
        g = max(getattr(graze, 'geoms', [graze]), key=lambda q: q.area)
        cx, cy = g.representative_point().coords[0]
        hrng = np.random.default_rng(21)
        for _ in range(4000):
            if len(herd) == 15: break
            x, y = cx + hrng.normal(0, 30), cy + hrng.normal(0, 30)
            if g.contains(Point(x, y)) and all(math.dist((x, y), h[:2]) > 9 for h in herd):
                herd.append([round(x, 1), round(y, 1), round(float(hrng.uniform(0, 6.283)), 2), int(hrng.uniform() < .3)])   # 1 = black
    out['herd'] = herd

    # surveyed trees: [x, y, flag]; flag 0 = under a new building or yard (removed after Existing),
    # 1 = stands in the parking paving (kept, a conflict to resolve), none = clear
    new_built = unary_union([el_poly(e) for e in AG['elements'] if e.get('kind') in ('building', 'yard')
                             and not e['id'].startswith(('existing', 'turnout'))])
    pk = ELEM['parking']
    paving = Polygon([d2s(x, y) for x, y in pk['outline']], [[d2s(x, y) for x, y in h] for h in pk.get('holes', [])]).buffer(0)
    stall_area = unary_union([Polygon([d2s(x, y) for x, y in q]).buffer(1.0) for q in pk.get('stalls_extra', [])])
    surveyed = []
    for it in items('trees', 'circle'):
        e = it['e']
        x, y = apply(it['M'], [(float(e.get('cx')), float(e.get('cy')))])[0]
        p = Point(x, y)
        # a tree standing in a drive aisle of the lot (not a stall) is removed (owner, 2026-10-19)
        in_aisle = paving.contains(p) and not stall_area.contains(p)
        flag = [0] if new_built.contains(p) or in_aisle else ([1] if paving.contains(p) else [])
        surveyed.append([round(x, 1), round(y, 1)] + flag)
    out['surveyed_trees'] = surveyed

    # campus: the survey's road area and buildings, plus the plan's campus elements
    out['roads'] = [p for it in items('campus', 'path') if it['e'].get('id') == 'road-area' for p in to_polys(rings(it))]
    out['road_fill'] = road_embankment(out['roads'], WET, ELEM)
    def outline(eid):
        e = ELEM[eid]
        pts = e.get('outline') or [[e['x'], e['y']], [e['x'] + e['w'], e['y']], [e['x'] + e['w'], e['y'] + e['h']], [e['x'], e['y'] + e['h']]]
        return [list(d2s(x, y)) for x, y in pts]

    # Surveyed structures. Ones the plan already models (Red House, existing barn and pens, unfinished barn,
    # porches, carport) are dropped; ones under a new plan element are existing structures the plan removes
    # (shown at Existing only, `until: 0`); the rest stay at every Level.
    modeled = unary_union([Polygon(outline(k)).buffer(4) for k in
                           ('existing-red-house', 'existing-barn', 'existing-pens', 'existing-poultry', 'existing-carport',
                            'existing-porch-nw', 'existing-porch-ne')])
    new = unary_union([Polygon(outline(e['id'])) for e in AG['elements']
                       if not e['id'].startswith('existing') and e['id'] not in ('residence', 'horticulture')])
    sheds = []
    def classify(o, kind, name):
        g = Polygon(o)
        if g.intersection(modeled).area > .5 * g.area: return
        d = dict(o=o, kind=kind, name=name)
        if g.intersects(new): d['until'] = 0
        sheds.append(d)
    for it in items('campus', 'path'):
        if it['e'].get('id'): continue
        for p in to_polys(rings(it), evenodd=False):
            bonus = 'bonus-buildings' in it['layers']
            classify(p['o'], 'building', 'Existing building' if bonus else 'Existing structure')
    for it in items('campus', 'polygon', 'canopies'):
        classify(to_polys(rings(it), evenodd=False)[0]['o'], 'canopy', 'Existing shed')
    out['survey_buildings'] = sheds

    pk = ELEM['parking']
    out['campus'] = dict(
        red_house=outline('existing-red-house'),
        porches=[outline('existing-porch-nw'), outline('existing-porch-ne')],
        carport=outline('existing-carport'),
        residence=outline('residence'),
        poultry=outline('existing-poultry'),
        poultry_frame=frame_of(outline('existing-poultry')),
        horticulture=outline('horticulture'),
        parking=dict(o=outline('parking'), h=[[list(d2s(x, y)) for x, y in h] for h in pk.get('holes', [])],
                     grass=[list(d2s(x, y)) for x, y in pk['grass']],
                     island=[list(d2s(x, y)) for x, y in pk['island_poly']]),
        walks=[dict(level=ELEM[w]['level'], o=outline(w)) for w in ('walk', 'walk-2')],
    )
    stalls = []
    for it in items('barnyard', 'polygon'):
        e = it['e']
        if e.get('fill') is None and e.get('class') is None:
            r = rings(it)[0]
            if 150 < Polygon(r).area < 260: stalls.append(rnd(r))
    out['campus']['stalls'] = stalls
    # Sabal palms framing the parking's north and west sides (owner, 2026-10-20), in scene feet. North: down the 8'
    # planting strip between the grass parking and the lane south of the arena (scene.py, x 168.5 to 303), on the
    # arena's 12' column grid so the trunks line up with its columns; the end palms are pulled in to sit inside the
    # strip. West: six about 19.4' apart in the grass west of the lot's west leg (x 145.7), from the lane south toward
    # the surveyed oak.
    ax1, ax2 = 645 / 2.95, 893 / 2.95                                       # arena column lines (scene.py, R(645, ...))
    step = (ax2 - ax1) / 7
    grid = [ax1 + k * step for k in range(-5, 8) if 168.5 < ax1 + k * step < 303]
    north = [min(max(x, 172.0), 300.0) for x in grid]
    out['campus']['palms'] = ([[round(x, 1), -249.9] for x in north] +
                              [[139.7, round(-252 - k * 19.4, 1)] for k in range(6)])

    # The Red House's Level 3 teaching space, as the massing models it (owner, 2026-10-20): 72' x 36' on the 12' grid,
    # near the study plan's addition but square to the barnyard (the diagram's axes) instead of true north,
    # entry centred on its west end. The walk is walk-3 from the plan, carried on to a landing at the new door.
    ao = ELEM['red-house-addition']['outline']
    acx, acy = sum(p[0] for p in ao) / 4, sum(p[1] for p in ao) / 4
    acx += 5.0                     # moved 5' east (owner): about 12.9' clear from its floor band to the Red House's north-east porch
    L, W = 72.0, 36.0
    c0, c1 = d2s(acx, acy), d2s(acx + 1, acy)
    wx = acx - L / 2                                                         # west wall line (diagram x)
    landing = [(wx - 6, acy - 5), (wx, acy - 5), (wx, acy + 5), (wx - 6, acy + 5)]
    w3 = ELEM['walk-3']['outline']
    end = [(220.8, 428.4), (223.5, 437.1)]                                   # walk-3's east end (its edge at the plan's canopy)
    link = [(wx - 6, acy + 5), (wx, acy + 5), end[1], end[0]]
    walk = unary_union([Polygon(w3).buffer(0), Polygon(landing), Polygon(link).buffer(0)]).buffer(0.05).buffer(-0.05)
    start = min(w3, key=lambda p: p[0])
    out['campus']['addition'] = dict(
        c=list(c0), ang=round(math.degrees(math.atan2(c1[1] - c0[1], c1[0] - c0[0])), 3), L=L, W=W,
        walk=[list(d2s(x, y)) for x, y in list(walk.exterior.coords)[:-1]],
        walk_from=list(d2s(*start)), walk_to=list(d2s(wx - 3, acy)))

    # the walk to the unfinished barn squares into its aisle in the deck's plan (tools/build_ag_area.py)
    walks_u = unary_union([Polygon(w['o']).buffer(0) for w in out['campus']['walks']])

    # fences stop at the pavement edge, with a pipe gate across the walk (owner, 2026-10-19)
    # Where a pasture fence runs along a fence the massing already models (turnout boards, pen and barn panels, the
    # existing pens' back fence), the wire fence is left out so the two don't overlap (owner, 2026-10-19).
    panels = []
    for o in scene_objects():
        if o.name.startswith(('pen', 'to')) or o.name in ('expens', 'chute', 'arenarail') or o.name.endswith(('_gates', '_pens')):
            for l in o.lines:
                p = np.asarray(l['p'], float)
                if len(p) >= 2 and p[:, 2].min() > 0.3 and np.ptp(p[:, 2]) < 0.3:
                    panels.append(LineString([tuple(q[:2]) for q in p]))
    zone = unary_union(panels).buffer(2.5) if panels else None
    # The site plan's pasture fence east of the barnyard runs slightly askew through the holding pens (an error carried
    # in from the fencing plan); nothing of it belongs inside the pens' pipe-rail block, so it is cut out there (owner).
    pen_pts = {}                                                    # each pen is drawn as four side objects, penN_k
    for o in scene_objects():
        if o.name.startswith('pen'):
            pen_pts.setdefault(o.name.split('_')[0], []).extend([q for l in o.lines for q in l['p']] + [q for f in o.faces for q in f['p']])
    pens = [box(p[:, 0].min(), p[:, 1].min(), p[:, 0].max(), p[:, 1].max()) for p in (np.asarray(v, float) for v in pen_pts.values()) if len(p)]
    if pens:
        zone = unary_union([zone, unary_union(pens).buffer(1.5)]) if zone is not None else unary_union(pens).buffer(1.5)
    if zone is not None:
        kept = []
        for f in out['fences']:
            rest = LineString(f['p']).difference(zone)
            parts = [g for g in getattr(rest, 'geoms', [rest]) if g.length > 4]
            for k, g in enumerate(parts):
                kept.append(dict(f, id=f['id'] if len(parts) == 1 else f"{f['id']}-p{k}", p=rnd(g.coords)))
        out['fences'] = kept
    gates, fences = [], []
    inner = walks_u.buffer(-0.3)        # cut only where a fence passes through a walk, not where it runs along an edge
    for f in out['fences']:
        ln = LineString(f['p'])
        if not ln.intersects(inner):
            fences.append(f); continue
        cross = ln.intersection(walks_u.boundary)   # where it enters and leaves the walk
        pts = sorted([(p.x, p.y) for p in getattr(cross, 'geoms', [cross]) if p.geom_type == 'Point'], key=lambda q: ln.project(Point(q)))
        rest = ln.difference(walks_u)
        for k, g in enumerate(getattr(rest, 'geoms', [rest])):
            if g.length > 1: fences.append(dict(id=f"{f['id']}-{k}", p=rnd(g.coords), level=f['level']))
    # run fence ends that stop just short of a walk on to its edge
    edge = walks_u.boundary
    for f in fences:
        for i in (0, -1):
            q = Point(f['p'][i])
            if 0.05 < walks_u.distance(q) < 12:
                e = edge.interpolate(edge.project(q))
                if i == 0: f['p'].insert(0, [round(e.x, 2), round(e.y, 2)])
                else: f['p'].append([round(e.x, 2), round(e.y, 2)])
    # a gate between each pair of fence ends facing each other across a walk
    ends = [(tuple(f['p'][i]), f['level']) for f in fences for i in (0, -1) if edge.distance(Point(f['p'][i])) < .3]
    used = set()
    for i, (p, lv) in enumerate(ends):
        if i in used: continue
        best = min(((math.dist(p, q), j) for j, (q, _) in enumerate(ends) if j != i and j not in used), default=None)
        if not best or not 3 < best[0] < 16: continue
        q = ends[best[1]][0]
        if LineString([p, q]).within(walks_u.buffer(.1)):
            used |= {i, best[1]}
            gates.append(dict(p=[list(p), list(q)], level=lv))
    out['fences'], out['gates'] = fences, gates

    # the aerial, as a parallelogram in scene feet (origin, +u corner, +v corner)
    img = next(it for it in ITEMS if it['tag'] == 'image' and it['layers'][1] == 'aerial')
    e = img['e']
    w, h = float(e.get('width')), float(e.get('height'))
    M = img['M']
    corners = [apply(M, [(0, 0)])[0], apply(M, [(w, 0)])[0], apply(M, [(0, h)])[0]]
    o_, u_, v_ = corners
    out['aerial'] = dict(src='aerial.jpg', o=list(o_), u=list(u_), v=list(v_),
                         polys=cut([dict(o=[list(o_), list(u_), [u_[0] + v_[0] - o_[0], u_[1] + v_[1] - o_[1]], list(v_)], h=[])]))
    src = os.path.join(ROOT, 'slides', e.get('href').replace('%20', ' '))
    Image.open(src).convert('RGB').save(os.path.join(HERE, 'aerial.jpg'), quality=84)

    path = os.path.join(HERE, 'site-data.js')
    with open(path, 'w') as fh:
        fh.write('// ' + out['about'] + '\nwindow.SITE = ')
        json.dump(out, fh, separators=(',', ':'))
        fh.write(';\n')
    stamp_viewer(path)
    allpts = np.array([q for b in out['boundary'] for q in b['o']])
    print(f"{path}: {os.path.getsize(path) / 1024:.0f} KB; frame fit {RESID:.2f} ft; "
          f"paddocks {len(pads)}, fences {len(out['fences'])}, canopy polys {len(canopy)}, canopy trees {len(scatter)}, "
          f"surveyed trees {len(surveyed)} ({sum(t[2:] == [0] for t in surveyed)} removed, {sum(t[2:] == [1] for t in surveyed)} in paving), stalls {len(stalls)}, survey buildings {len(sheds)} "
          f"({sum('until' in b for b in sheds)} removed by the plan); "
          f"road +{out['road_fill']['height_ft']}' ({out['road_fill']['road_elev']} on {out['road_fill']['n_road']} spots vs grade {out['road_fill']['grade_elev']} on {out['road_fill']['n_grade']}); "
          f"trees oak/pine/palm {[sum(t[3] == k for t in scatter) for k in (0, 1, 2)]}; basins {[(b['kind'], b['inset'], len(b['v']) // 3) for b in basins]}; "
          f"boundary x {allpts[:, 0].min():.0f}..{allpts[:, 0].max():.0f} y {allpts[:, 1].min():.0f}..{allpts[:, 1].max():.0f}")
    for pd in pads: print('  ', pd['kind'], pd['label'], round(Polygon(pd['polys'][0]['o']).area / 43560, 1), 'ac')


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
