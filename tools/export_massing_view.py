"""Export a still of the 3D massing viewer (massing/index.html) as a PNG, with headless Google Chrome.

Serves the repo locally and screenshots tools/massing-shot.html, which frames the viewer without its control rail
from the camera given here. Views are named below; the size sets the aspect ratio.

Run: python tools/export_massing_view.py [view ...] [--size WxH] [--labels] [--level 3]
     -> exports/massing-<view>.png (git-ignored)
Needs: Google Chrome.
"""
import argparse, functools, http.server, os, socket, subprocess, tempfile, threading

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "exports")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# name -> (camera position, target, vertical fov, default size), scene feet (x east, y north, z up); the same cameras
# as the viewer's presets in massing/index.html where they share a name
VIEWS = {
    # "Over the pens" pulled back and widened to take in the unfinished (poultry) barn and the classroom building
    # (owner, 2026-10-20); 2.4:1 or wider
    "over-the-pens-wide": ((600, 30, 170), (300, -250, 0), 42, "4800x2000"),
    # eye level: a student leading a steer at cattle barn B (the viewer's "Leading a steer")
    "leading-a-steer": ((166, -201, 5.5), (136, -153, 6), 44, "3840x2160"),
}

ap = argparse.ArgumentParser()
ap.add_argument("views", nargs="*", default=list(VIEWS))
ap.add_argument("--size", help="WxH; default per view")
ap.add_argument("--labels", action="store_true")
ap.add_argument("--level", default="3")
a = ap.parse_args()

handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
with socket.socket() as s:
    s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]
srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
os.makedirs(OUT, exist_ok=True)
try:
    for name in a.views:
        pos, tgt, fov, size = VIEWS[name]
        w, h = (int(v) for v in (a.size or size).split("x"))
        path = os.path.join(OUT, f"massing-{name}.png")
        url = (f"http://127.0.0.1:{port}/tools/massing-shot.html?pos={','.join(map(str, pos))}&tgt={','.join(map(str, tgt))}"
               f"&fov={fov}&level={a.level}&labels={1 if a.labels else 0}")
        subprocess.run([CHROME, "--headless=new", f"--user-data-dir={tempfile.mkdtemp(prefix='massingshot-')}",
                        "--force-color-profile=srgb", "--hide-scrollbars", "--enable-unsafe-swiftshader",
                        f"--window-size={w},{h}", "--virtual-time-budget=20000", f"--screenshot={path}", url],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
        print(path)
finally:
    srv.shutdown()
