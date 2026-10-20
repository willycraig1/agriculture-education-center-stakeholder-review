"""Syntax-check the inline scripts of every slide, and of index.html, with Node.

A single bad line (such as a comment that swallows the rest of a line) stops a slide's script, and the slide comes up
blank with no visible error. Run this after editing slides or rebuilding data: python tools/check_slides.py
Needs: node on the PATH.
"""
import glob, os, re, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
bad = 0
for f in sorted(glob.glob(os.path.join(ROOT, "slides", "*.html"))) + [os.path.join(ROOT, "index.html")]:
    for k, m in enumerate(re.finditer(r"<script>(.*?)</script>", open(f).read(), re.S)):
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as t:
            t.write(m.group(1))
        r = subprocess.run(["node", "--check", t.name], capture_output=True, text=True)
        os.unlink(t.name)
        if r.returncode:
            bad += 1
            err = next((l for l in r.stderr.splitlines() if "Error" in l), r.stderr.strip())
            print(f"{os.path.relpath(f, ROOT)} (script {k + 1}): {err}")
print("all slide scripts parse" if not bad else f"{bad} script(s) with errors")
sys.exit(1 if bad else 0)
