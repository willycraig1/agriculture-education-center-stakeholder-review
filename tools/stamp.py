"""Cache-busting: stamp every slide's links to its data files, styles and scripts with ?v=<stamp>.

Browsers keep data/*.js and design/* files cached across visits, so after a rebuild a viewer can see an old
drawing on a new page. Run this after the build tools (and before committing): it rewrites src/href values in
index.html and slides/*.html that point at data/, ../design/ or design/ to carry ?v=<current time>.

Run:  python tools/stamp.py
"""
import glob, os, re, time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
v = time.strftime("%Y%m%d%H%M")
pat = re.compile(r'((?:src|href)=")((?:\.\./)?(?:data|design)/[^"?]+\.(?:js|css))(\?v=\d+)?(")')
n = 0
for f in [os.path.join(ROOT, "index.html")] + sorted(glob.glob(os.path.join(ROOT, "slides", "*.html"))):
    s = open(f).read()
    t, k = pat.subn(lambda m: f"{m.group(1)}{m.group(2)}?v={v}{m.group(4)}", s)
    if k:
        open(f, "w").write(t); n += k
print("stamped", n, "links with v =", v)
