"""Cache-busting: stamp every slide's links to its data files, styles and scripts with ?v=<stamp>.

Browsers keep data/*.js and design/* files cached across visits, so after a rebuild a viewer can see an old
drawing on a new page. Run this after the build tools (and before committing): it rewrites src/href values in
index.html and slides/*.html that point at data/, ../design/ or design/ to carry ?v=<current time>, and sets
BUILD in index.html so each slide page itself is loaded as slides/<name>.html?v=<time>.

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
# the deck shell loads each slide in a frame: give those URLs the same version
_ix = os.path.join(ROOT, "index.html")
_s = open(_ix).read()
_t = re.sub(r'const BUILD = "[^"]*";', f'const BUILD = "{v}";', _s)
if _t != _s:
    open(_ix, "w").write(_t)
print("stamped", n, "links with v =", v)
