"""Export selected OCG layers of page 1 of a PDF as an SVG with one <g> per layer."""
import pymupdf, sys, json, hashlib
def path_d(d):
    out=[]; last=None
    for it in d['items']:
        k=it[0]
        if k=='l':
            a,b=it[1],it[2]
            if last is None or abs(last.x-a.x)>.01 or abs(last.y-a.y)>.01: out.append(f"M{a.x:.2f} {a.y:.2f}")
            out.append(f"L{b.x:.2f} {b.y:.2f}"); last=b
        elif k=='c':
            a,c1,c2,b=it[1:5]
            if last is None or abs(last.x-a.x)>.01 or abs(last.y-a.y)>.01: out.append(f"M{a.x:.2f} {a.y:.2f}")
            out.append(f"C{c1.x:.2f} {c1.y:.2f} {c2.x:.2f} {c2.y:.2f} {b.x:.2f} {b.y:.2f}"); last=b
        elif k=='re':
            r=it[1]; out.append(f"M{r.x0:.2f} {r.y0:.2f}H{r.x1:.2f}V{r.y1:.2f}H{r.x0:.2f}Z"); last=None
        elif k=='qu':
            q=it[1]; out.append(f"M{q.ul.x:.2f} {q.ul.y:.2f}L{q.ur.x:.2f} {q.ur.y:.2f}L{q.lr.x:.2f} {q.lr.y:.2f}L{q.ll.x:.2f} {q.ll.y:.2f}Z"); last=None
    if d.get('closePath'): out.append('Z')
    return ''.join(out)
def export(f, layers, clip=None, colors=None):
    p=pymupdf.open(f)[0]
    groups={}
    for d in p.get_drawings():
        L=d.get('layer') or '(none)'
        if layers and L not in layers: continue
        if clip and not pymupdf.Rect(d['rect']).intersects(clip): continue
        groups.setdefault(L,[]).append(d)
    return groups
def to_svg(groups, view, colors=None, width=0.6):
    x0,y0,x1,y1=view
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{(x1-x0)*2:.0f}" height="{(y1-y0)*2:.0f}"><rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="white"/>']
    pal=['#c00','#06c','#080','#a0a','#e70','#088','#555','#c06','#660']
    for i,(L,ds) in enumerate(groups.items()):
        c=(colors or {}).get(L, pal[i%len(pal)])
        s.append(f'<g id="{L}" fill="none" stroke="{c}" stroke-width="{width}">')
        for d in ds:
            dd=path_d(d)
            if dd: s.append(f'<path d="{dd}"/>')
        s.append('</g>')
    s.append('</svg>'); return '\n'.join(s)
