"""Export sheet A-1, the Red House at Levels 1 to 3 with program colours, as Arch D PDF and layered SVG.

Prints tools/red-house-sheet.html with headless Google Chrome (36 x 24 in, vector) and saves the page's SVG, whose
top-level groups (Program_colors, Plans, Room_names, Plan_titles, Titleblock) open in Illustrator as named layers.

Writes exports/red-house-A-1.pdf and exports/red-house-A-1.svg.
Run: python tools/export_red_house_sheet.py [--date YYYY-MM-DD]   (after tools/build_red_house.py)
"""
import argparse, datetime, functools, http.server, os, re, socket, subprocess, tempfile, threading

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = os.path.join(ROOT, "exports")
ap = argparse.ArgumentParser(); ap.add_argument("--date", default=datetime.date.today().isoformat()); ARGS = ap.parse_args()

s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
handler.log_message = lambda *a: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
os.makedirs(OUT, exist_ok=True)
url = f"http://127.0.0.1:{port}/tools/red-house-sheet.html?date={ARGS.date}"
base = [CHROME, "--headless=new", "--force-color-profile=srgb", "--no-pdf-header-footer", "--window-size=3456,2304", "--virtual-time-budget=8000"]
pdf = os.path.join(OUT, "red-house-A-1.pdf")
subprocess.run(base + [f"--user-data-dir={tempfile.mkdtemp(prefix='rhpdf-')}", f"--print-to-pdf={pdf}", url],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
dom = subprocess.run(base + [f"--user-data-dir={tempfile.mkdtemp(prefix='rhsvg-')}", "--dump-dom", url],
                     check=True, capture_output=True, text=True, timeout=180).stdout
svg = re.search(r'<svg id="sheet".*?</svg>(?=\s*<script)', dom, re.S).group(0)
open(os.path.join(OUT, "red-house-A-1.svg"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n' + svg)
print("wrote", pdf, "and red-house-A-1.svg")
srv.shutdown()
