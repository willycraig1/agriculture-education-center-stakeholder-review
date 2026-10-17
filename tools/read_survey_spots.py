"""Read the survey's spot elevations -> drawings/data/survey-spots.json

The survey sheet (source/Survey + Soils Map Info.pdf) carries about 1,265 spot elevations, each an "x" mark with a
label such as 25.19. The labels are CAD text exported as stroked vector glyphs, not PDF text, so they are read here
by shape: every glyph near a mark is rotated to the label's baseline, drawn into a small bitmap, and matched to the
nearest template in tools/survey_glyphs/centers.npy (cluster centres of the sheet's own glyphs, each named below).
Labels with a glyph that matches no digit, or that do not parse as dd.dd, are skipped: about 930 are read.

Spot-checked against the sheet (e.g. 25.19 and 19.7x beside State Road 72 at the entry). Elevations are as surveyed
(datum per the survey). Output points are in survey PDF points and in the site map's presentation frame.

    .venv/bin/python tools/read_survey_spots.py
"""
import json, math, os, re
import numpy as np
import pymupdf
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SURVEY = os.path.join(ROOT, 'source', 'Survey + Soils Map Info.pdf')
CENTERS = np.load(os.path.join(HERE, 'survey_glyphs', 'centers.npy'))
NAMES = '2 3 2 ? 2 2 1 0 7 5 4 ? 3 9 1 3 1 4 9 6 8 . 5 3 8 5'.split()   # one per template; ? = not a digit

reg = json.load(open(os.path.join(HERE, 'registration.json')))
M_SF, T_SF = complex(*reg['survey_to_fence']['m']), complex(*reg['survey_to_fence']['t'])
CX, CY = 1220, 860   # presentation frame: the fencing sheet turned 180 degrees about the view centre (siteframe.py)


def is_label_ink(dd):
    c = dd.get('color')
    return c and abs(c[0] - .4) < .02 and abs(dd.get('width', 0) - .42) < .05


def segs_of(dd):
    return [((it[1].x, it[1].y), (it[2].x, it[2].y)) if it[0] == 'l' else ((it[1].x, it[1].y), (it[4].x, it[4].y))
            for it in dd['items'] if it[0] in 'lc']


def main():
    D = pymupdf.open(SURVEY)[0].get_drawings()
    # marks: two single-stroke diagonals sharing one small bounding box
    boxes = {}
    for i, dd in enumerate(D):
        if not is_label_ink(dd) or len(dd['items']) != 1 or dd['items'][0][0] != 'l': continue
        r = dd['rect']
        if .2 < r.width < .6 and .2 < r.height < .6:
            boxes.setdefault((round(r.x0, 2), round(r.y0, 2), round(r.x1, 2), round(r.y1, 2)), []).append(i)
    marks = [((k[0] + k[2]) / 2, (k[1] + k[3]) / 2, v) for k, v in boxes.items() if len(v) == 2]
    used = {i for *_, v in marks for i in v}
    P = np.array([[x, y] for x, y, _ in marks])
    glyphs = [[] for _ in marks]
    for j, dd in enumerate(D):
        if j in used or not is_label_ink(dd): continue
        r = dd['rect']
        if r.width > 1.2 or r.height > 1.2: continue
        s = segs_of(dd)
        if not s: continue
        c = np.array([(r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2])
        d2 = ((P - c) ** 2).sum(1); k = int(d2.argmin())
        if d2[k] < 3.2 ** 2: glyphs[k].append(s)

    out = []
    for (x, y, _), gl in zip(marks, glyphs):
        gl.sort(key=lambda g: math.dist(np.mean([q for s in g for q in s], 0), (x, y)))
        cs = [np.mean([q for s in g for q in s], 0) for g in gl]
        if len(cs) < 3: continue
        v = cs[-1] - cs[0]; a = math.atan2(v[1], v[0]); ca, sa = math.cos(-a), math.sin(-a)
        rot = lambda q: ((q[0] - x) * ca - (q[1] - y) * sa, (q[0] - x) * sa + (q[1] - y) * ca)
        text = ''
        for g in gl:
            R = [(rot(p), rot(q)) for p, q in g]
            Q = np.array([q for s in R for q in s]); cx, cy = Q[:, 0].mean(), Q[:, 1].mean()
            im = Image.new('L', (32, 40), 0); dr = ImageDraw.Draw(im)
            for p, q in R:
                dr.line([((p[0] - cx) * 40 + 16, (p[1] - cy) * 40 + 20), ((q[0] - cx) * 40 + 16, (q[1] - cy) * 40 + 20)], fill=255, width=3)
            f = np.asarray(im, float).ravel() / 255
            ch = NAMES[int(((CENTERS - f) ** 2).sum(1).argmin())]
            if ch == '.' and max(np.ptp(Q[:, 0]), np.ptp(Q[:, 1])) > .12: ch = '?'
            text += ch
        if re.fullmatch(r'\d{1,2}\.\d{1,2}', text) and 3 < float(text) < 40:
            f = M_SF * complex(x, y) + T_SF
            out.append(dict(z=float(text), survey=[round(x, 2), round(y, 2)],
                            map=[round(2 * CX - f.real, 2), round(2 * CY - f.imag, 2)]))
    path = os.path.join(ROOT, 'drawings', 'data', 'survey-spots.json')
    json.dump(dict(note=__doc__.strip().split('\n')[0], read=len(out), marks=len(marks), spots=out), open(path, 'w'))
    zs = np.array([o['z'] for o in out])
    print(f'{path}: {len(out)} of {len(marks)} spot elevations read; z {zs.min():.2f}..{zs.max():.2f}, median {np.median(zs):.2f}')


if __name__ == '__main__':
    main()
