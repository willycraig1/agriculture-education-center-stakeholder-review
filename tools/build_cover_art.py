"""Cover illustration: a hand-drawn-style perspective of the barnyard (architect's request, 2026-10-15).

Not a rendering: an SVG sketch in the deck's palette, drawn from the site photos (photos/barn.jpeg: the existing
barn, weathered board-and-batten with four roll-up doors and a lean-to on its west side) and the reference project's
photos (Seibert Architects, MMS Ag Farm: open-sided gable arena canopy on timber posts, white metal livestock barns
with a raised monitor roof). Foreground: a 4-H student leading a heifer on a halter. Back left: the arena. Beyond:
the new barns and a tractor. A watercolour look comes from SVG filters (wobbled edges, paper grain).

Writes drawings/cover-perspective.svg. Run: python tools/build_cover_art.py
"""
import json, math, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
pal = json.load(open(os.path.join(ROOT, "design", "palette.json")))
P = pal["program"]
rnd = random.Random(2601)
W, H = 960, 1080
HZ = 612                                     # horizon / ground line of the background buildings
out = []
add = out.append


def poly(pts, fill, stroke="none", sw=0, extra=""):
    add(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def line(x1, y1, x2, y2, col, sw=1, extra=""):
    add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{sw}" stroke-linecap="round" {extra}/>')


def blob(cx, cy, r, fill, n=9, jit=.28, op=1):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        rr = r * (1 + rnd.uniform(-jit, jit))
        pts.append((cx + rr * math.cos(a), cy + rr * .72 * math.sin(a)))
    d = "M" + " ".join(f"{(pts[i][0] + pts[(i + 1) % n][0]) / 2:.1f},{(pts[i][1] + pts[(i + 1) % n][1]) / 2:.1f} Q{pts[(i + 1) % n][0]:.1f},{pts[(i + 1) % n][1]:.1f}" for i in range(n))
    add(f'<path d="{d} Z" fill="{fill}" opacity="{op}"/>')


INK = "#3a352d"
add(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#8fb0c9"/><stop offset=".55" stop-color="#cfdde3"/><stop offset=".9" stop-color="#f3e2c3"/></linearGradient>
  <linearGradient id="field" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#9fb47a"/><stop offset=".45" stop-color="#8aa565"/><stop offset="1" stop-color="#6f8e4c"/></linearGradient>
  <linearGradient id="drive" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#e6ddc9"/><stop offset="1" stop-color="#d3c7ad"/></linearGradient>
  <filter id="wc" x="-5%" y="-5%" width="110%" height="110%">
    <feTurbulence type="fractalNoise" baseFrequency=".018" numOctaves="3" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="7" xChannelSelector="R" yChannelSelector="G" result="d"/>
    <feGaussianBlur in="d" stdDeviation=".6"/></filter>
  <filter id="pen" x="-5%" y="-5%" width="110%" height="110%">
    <feTurbulence type="fractalNoise" baseFrequency=".05" numOctaves="2" seed="3" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="2.2" xChannelSelector="R" yChannelSelector="G"/></filter>
  <filter id="paper"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="11"/>
    <feColorMatrix values="0 0 0 0 .45  0 0 0 0 .4  0 0 0 0 .32  0 0 0 .55 0"/></filter>
  <radialGradient id="sun" cx=".18" cy=".54" r=".5"><stop offset="0" stop-color="#fff3d6" stop-opacity=".9"/><stop offset="1" stop-color="#fff3d6" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{W}" height="{H}" fill="#f7f1e4"/>
<g filter="url(#wc)">''')

# ---- sky and clouds
add(f'<rect width="{W}" height="{HZ + 10}" fill="url(#sky)"/>')
add(f'<rect width="{W}" height="{HZ + 10}" fill="url(#sun)"/>')
for cx, cy, r in [(640, 170, 90), (720, 150, 70), (560, 190, 60), (220, 260, 55), (290, 245, 70), (850, 300, 50)]:
    blob(cx, cy, r, "#ffffff", op=.55)

# ---- far hammock: oaks and cabbage palms
for i in range(46):
    x = i * 22 - 10 + rnd.uniform(-8, 8)
    blob(x, HZ - 30 + rnd.uniform(-14, 10), rnd.uniform(26, 44), rnd.choice(["#6f8a68", "#62805e", "#7a9472"]), op=.95)
for x in (140, 410, 470, 760, 905):
    h = rnd.uniform(70, 110); top = HZ - 40 - h
    line(x, HZ - 20, x + rnd.uniform(-6, 6), top, "#5d6b52", 3)
    for k in range(9):
        a = math.pi * (1.05 + k * .11)
        line(x, top, x + 30 * math.cos(a) * rnd.uniform(.8, 1.1) * (-1 if k > 4 else 1) ** 0, top + 26 * math.sin(a) * -.6 + 10, "#56704f", 4)

# ---- ground
poly([(0, HZ), (W, HZ), (W, H), (0, H)], "url(#field)")

# ---- beyond: white metal barns with monitor roofs, and a tractor (vanishing toward the right)
def metal_barn(x0, x1, base, eave, ridge, mon=True):
    mid = (x0 + x1) / 2
    poly([(x0, base), (x1, base), (x1, eave), (x0, eave)], "#f4f2ec", INK, .8)
    poly([(x0 - 6, eave), (x1 + 6, eave), (x1 + 6, eave - (ridge - 2) * .5), (x0 - 6, eave - (ridge - 2) * .5)], "#c9ccc9", INK, .8)
    if mon:
        poly([(x0 + (x1 - x0) * .3, eave - ridge * .5), (x0 + (x1 - x0) * .7, eave - ridge * .5), (x0 + (x1 - x0) * .7, eave - ridge), (x0 + (x1 - x0) * .3, eave - ridge)], "#dfe1dd", INK, .7)
    for k in range(int((x1 - x0) / 10)):
        line(x0 + 5 + k * 10, eave + 3, x0 + 5 + k * 10, base - 2, "#b8bab4", .5)
metal_barn(250, 446, HZ + 4, HZ - 34, 20)
metal_barn(850, 1000, HZ + 6, HZ - 36, 22)

# ---- arena, back left: open-sided gable canopy on timber posts, steel trusses
ax0, ax1, ab, ae, ar = 170, 500, HZ + 14, HZ - 66, HZ - 106
poly([(ax0 - 10, ae), ((ax0 + ax1) / 2, ar), (ax1 + 10, ae), (ax1 + 4, ae + 6), ((ax0 + ax1) / 2, ar + 7), (ax0 - 4, ae + 6)], "#a7aca8", INK, 1.2)
for k in range(11):
    x = ax0 + k * (ax1 - ax0) / 10
    line(x, ae + 5, x, ab, "#7a5a37", 4)
for k in range(10):                                       # truss webs under the roof
    xa = ax0 + k * (ax1 - ax0) / 10; xb = xa + (ax1 - ax0) / 10
    ya = ae + 6 - (1 - abs((xa - (ax0 + ax1) / 2) / ((ax1 - ax0) / 2))) * 31
    yb = ae + 6 - (1 - abs((xb - (ax0 + ax1) / 2) / ((ax1 - ax0) / 2))) * 31
    line(xa, ya, xb, ae + 12, INK, .6); line(xa, ae + 12, xb, ae + 12, INK, .6)
poly([(ax0, ab - 2), (ax1, ab - 2), (ax1, ab + 2), (ax0, ab + 2)], "#d8d2c2")
for k in range(16):                                       # rail fence inside the arena
    line(ax0 + 6 + k * 19.5, ab - 14, ax0 + 6 + k * 19.5, ab - 2, INK, .7)
line(ax0 + 6, ab - 12, ax1 - 6, ab - 12, INK, .7); line(ax0 + 6, ab - 7, ax1 - 6, ab - 7, INK, .7)

# ---- tractor, out by the arena
tx, ty = 300, HZ + 40
poly([(tx, ty - 22), (tx + 30, ty - 22), (tx + 32, ty - 6), (tx - 2, ty - 6)], "#4f7a3a", INK, .8)
poly([(tx + 18, ty - 44), (tx + 34, ty - 44), (tx + 34, ty - 22), (tx + 18, ty - 22)], "none", INK, 1.2)
add(f'<circle cx="{tx + 28}" cy="{ty - 4}" r="13" fill="#2f2c27"/><circle cx="{tx + 28}" cy="{ty - 4}" r="6" fill="#d8c25a"/>')
add(f'<circle cx="{tx + 2}" cy="{ty}" r="8" fill="#2f2c27"/><circle cx="{tx + 2}" cy="{ty}" r="3.5" fill="#d8c25a"/>')

# ---- the drive: aggregate apron in front of the barn, running out to the foreground
poly([(560, 650), (930, 650), (W + 40, H), (360, H)], "url(#drive)")

# ---- existing barn: weathered board-and-batten, metal roof, four roll-up doors, lean-to on the west
bx0, bx1, bb, be, brg = 452, 842, 660, 532, 452
side_dx = 74                                              # the east wall, seen receding to the right
poly([(bx1, bb), (bx1 + side_dx, bb - 16), (bx1 + side_dx, be - 6), (bx1, be)], "#6d5c48", INK, 1.1)
poly([(bx1, be), ((bx0 + bx1) / 2, brg), ((bx0 + bx1) / 2 + side_dx, brg - 12), (bx1 + side_dx + 6, be - 8)], "#8c8e8a", INK, 1.1)
for k in range(1, 14):
    x = bx1 + k * side_dx / 14
    line(x, be - 6 * k / 14 + 2, x, bb - 16 * k / 14 - 2, "#4f4234", .7)
poly([(bx0, bb), (bx1, bb), (bx1, be), ((bx0 + bx1) / 2, brg), (bx0, be)], "#7d6a52", INK, 1.3)
poly([(bx0 - 10, be + 2), ((bx0 + bx1) / 2, brg - 9), (bx1 + 10, be + 2), (bx1 + 6, be + 7), ((bx0 + bx1) / 2, brg - 2), (bx0 - 6, be + 7)], "#9a9c97", INK, 1)
for k in range(1, 48):                                    # boards
    x = bx0 + k * (bx1 - bx0) / 48
    ytop = be - (1 - abs((x - (bx0 + bx1) / 2) / ((bx1 - bx0) / 2))) * (be - brg)
    line(x, ytop + 3, x, bb - 2, rnd.choice(["#5e4e3c", "#6a5843", "#8d7a61"]), .8)
for (dx0, dx1, dtop) in [(474, 548, 590), (566, 652, 570), (668, 754, 570), (770, 832, 596)]:   # roll-up doors
    poly([(dx0, bb), (dx1, bb), (dx1, dtop), (dx0, dtop)], "#f1efe9", INK, 1)
    for y in range(int(dtop) + 6, bb, 6):
        line(dx0 + 2, y, dx1 - 2, y, "#c9c6bd", .6)
line(bx1 - 70, 548, bx1 - 64, 548, INK, 1.4)               # light fixture
lx0 = 352                                                  # lean-to with gate
poly([(lx0, bb), (bx0, bb), (bx0, 572), (lx0, 590)], "#5f503e", INK, 1)
poly([(lx0 - 8, 590), (bx0 + 2, 566), (bx0 + 2, 572), (lx0 - 6, 596)], "#9a9c97", INK, 1)
poly([(lx0 + 8, bb - 2), (bx0 - 6, bb - 2), (bx0 - 6, 600), (lx0 + 8, 610)], "#3b332a", "none")
for k in range(5):
    y = 614 + k * 9
    line(lx0 + 18, y, lx0 + 74, y - 2, "#d9cfb9", 2)
line(lx0 + 18, 612, lx0 + 74, 650, "#d9cfb9", 2); line(lx0 + 18, 612, lx0 + 18, 652, "#d9cfb9", 2); line(lx0 + 74, 608, lx0 + 74, 650, "#d9cfb9", 2)
for k in range(9):                                         # board fence running west
    x = 70 + k * 34
    line(x, 646 + k * .6, x, 676 + k * .6, "#7a6a55", 2.4)
line(66, 652, lx0, 657, "#8c7c64", 2); line(66, 666, lx0, 669, "#8c7c64", 2)

# ---- framing trees: a live oak at right, a cabbage palm at left
for i in range(26):
    blob(W - 30 + rnd.uniform(-90, 60), 230 + rnd.uniform(-120, 260), rnd.uniform(40, 70), rnd.choice(["#4f6b48", "#5b7752", "#46623f", "#6a845c"]), op=.92)
add(f'<path d="M{W - 22},{H + 10} C{W - 46},{800} {W - 26},{640} {W - 64},{420}" stroke="#4a3d30" stroke-width="46" fill="none" stroke-linecap="round"/>')
add(f'<path d="M{W - 58},{470} C{W - 90},{420} {W - 120},{380} {W - 150},{330}" stroke="#4a3d30" stroke-width="20" fill="none" stroke-linecap="round"/>')
for i in range(14):                                        # Spanish moss under the canopy
    x = W - 150 + i * 11 + rnd.uniform(-5, 5)
    add(f'<path d="M{x:.1f},{440 + rnd.uniform(-20, 20):.1f} q{rnd.uniform(-4, 4):.1f},22 {rnd.uniform(-3, 3):.1f},{rnd.uniform(30, 56):.1f}" stroke="#a5ab92" stroke-width="2" fill="none" opacity=".8"/>')
px, ptop = 36, 330
add(f'<path d="M{px + 10},{H - 220} C{px + 4},{560} {px + 18},{440} {px},{ptop}" stroke="#6b5c48" stroke-width="13" fill="none" stroke-linecap="round"/>')
for k in range(15):
    a = math.radians(-170 + k * 24)
    add(f'<path d="M{px},{ptop} q{70 * math.cos(a) * .5:.1f},{70 * math.sin(a) * .5 - 14:.1f} {80 * math.cos(a):.1f},{80 * math.sin(a) * .7 + 18:.1f}" stroke="{rnd.choice(["#4e6a44", "#5c7a50", "#3f5a38"])}" stroke-width="7" fill="none" stroke-linecap="round"/>')

# ---- grass texture in the foreground
for i in range(520):
    x = rnd.uniform(0, W); y = rnd.uniform(680, H)
    if 360 + (y - H) * -0.55 < x < 960 and y > 680 + (x - 560) * 0:
        if x > 360 + (H - y) * (200 / (H - 650)) and x < W + 40 - (H - y) * (110 / (H - 650)):
            continue                                       # leave the drive bare
    h = 6 + (y - 680) * .05
    line(x, y, x + rnd.uniform(-3, 3), y - h, rnd.choice(["#5f7d42", "#7d9a58", "#9bb470", "#557238"]), 1.3)
add('</g>')

# ---- foreground figures (crisper: pen filter only): a 4-H student leading a heifer on a halter
add('<g filter="url(#pen)">')
add('<ellipse cx="600" cy="980" rx="270" ry="20" fill="#3a352d" opacity=".18"/>')
# heifer, walking left (rust with a white blaze, after reference photo 019)
cow, cowd = "#8a4b2e", "#6b3822"
add(f'<path d="M776,906 L768,972 L784,972 L792,904 Z M640,910 L634,972 L650,972 L656,912 Z" fill="{cowd}" stroke="{INK}" stroke-width="1.6"/>')     # far legs
add(f'<path d="M585,800 C640,786 730,786 790,800 C812,808 822,830 816,860 C812,880 806,892 800,902 L798,972 L782,972 L776,912 '
    f'C740,922 660,924 628,914 L620,972 L604,972 L598,904 C586,896 576,880 572,862 C566,840 568,816 585,800 Z" fill="{cow}" stroke="{INK}" stroke-width="2"/>')
add(f'<path d="M812,822 C826,840 830,880 826,930" stroke="{cow}" stroke-width="6" fill="none" stroke-linecap="round"/><path d="M822,926 l8,18 l-12,-3 z" fill="#3a2a20"/>')   # tail
add(f'<path d="M604,964 l18,0 l0,10 l-18,0 z M782,964 l18,0 l0,10 l-18,0 z" fill="#2f241c"/>')                                                    # hooves
add(f'<path d="M598,806 C576,794 550,792 536,800 C522,808 512,826 506,844 C502,856 504,868 514,872 C526,876 540,870 552,864 C566,858 580,850 590,846 Z" fill="{cow}" stroke="{INK}" stroke-width="2"/>')
add(f'<path d="M540,802 C528,812 518,830 512,850 C516,862 528,864 534,856 C536,838 540,818 546,804 Z" fill="#f2ece2"/>')                            # blaze
add(f'<path d="M530,808 C520,800 508,798 498,802 C506,810 518,814 530,812 Z M552,800 C560,790 570,786 578,788 C574,798 564,802 554,804 Z" fill="{cowd}" stroke="{INK}" stroke-width="1.2"/>')   # ears
add(f'<circle cx="531" cy="824" r="2.6" fill="{INK}"/><circle cx="509" cy="863" r="1.8" fill="{INK}"/>')
add(f'<path d="M506,848 C516,844 532,846 542,852 M542,852 L550,808" stroke="#2f4f86" stroke-width="3.2" fill="none" stroke-linecap="round"/>')      # halter
# student: 4-H green shirt, jeans, boots, cap; walking backward-left, holding the lead
add(f'<path d="M532,858 C500,876 470,868 446,848" stroke="#c9a24a" stroke-width="2.6" fill="none"/>')                     # lead rope
add(f'<path d="M388,966 L398,880 L420,880 L414,968 Z" fill="#3f5878" stroke="{INK}" stroke-width="1.6"/>')
add(f'<path d="M418,880 L440,880 L452,964 L432,968 Z" fill="#46617f" stroke="{INK}" stroke-width="1.6"/>')
add(f'<path d="M384,962 L414,962 L416,976 L378,976 Z M430,962 L454,960 L460,974 L428,976 Z" fill="#4a3424" stroke="{INK}" stroke-width="1.4"/>')
add(f'<path d="M392,884 C390,850 392,800 404,786 C418,778 436,780 444,792 C452,814 450,856 444,886 Z" fill="{P["pasture"]["base"]}" stroke="{INK}" stroke-width="1.8"/>')
add(f'<path d="M440,800 C452,816 456,834 446,848" stroke="{P["pasture"]["base"]}" stroke-width="13" fill="none" stroke-linecap="round"/><circle cx="446" cy="848" r="6.5" fill="#d9a77e" stroke="{INK}" stroke-width="1"/>')
add(f'<path d="M398,800 C388,826 390,850 396,866" stroke="{P["pasture"]["base"]}" stroke-width="12" fill="none" stroke-linecap="round"/><circle cx="397" cy="868" r="6" fill="#d9a77e" stroke="{INK}" stroke-width="1"/>')
add(f'<path d="M412,782 l8,-12 l12,0 l6,12 z" fill="#d9a77e"/>')
add(f'<ellipse cx="424" cy="756" rx="17" ry="20" fill="#d9a77e" stroke="{INK}" stroke-width="1.6"/>')
add(f'<path d="M404,752 C404,730 444,728 446,750 L460,754 L446,758 C430,744 414,744 404,756 Z" fill="#f1ede4" stroke="{INK}" stroke-width="1.4"/>')    # cap
add(f'<path d="M408,758 C406,770 410,778 416,780" stroke="#5a4130" stroke-width="5" fill="none" stroke-linecap="round"/>')                          # hair
add(f'<path d="M406,812 l12,0 l-6,-8 z" fill="#ffffff" opacity=".9"/>')                                                                           # clover badge
add('</g>')

# paper grain over everything, and a soft vignette into the slide's paper colour on the left edge
add(f'<rect width="{W}" height="{H}" filter="url(#paper)" opacity=".22"/>')
PAPER = pal["neutral"]["paper"]                          # the slide's paper colour, so the fade has no seam
add(f'<linearGradient id="fade" x1="0" y1="0" x2="1" y2="0"><stop offset=".1" stop-color="{PAPER}" stop-opacity="1"/><stop offset=".26" stop-color="{PAPER}" stop-opacity="0"/></linearGradient>')
add(f'<rect width="{W}" height="{H}" fill="url(#fade)"/>')
add("</svg>")
open(os.path.join(ROOT, "drawings", "cover-perspective.svg"), "w").write("\n".join(out))
print("cover-perspective.svg written,", sum(len(s) for s in out) // 1024, "KB")
