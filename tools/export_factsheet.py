"""Print the project fact sheet (factsheet/index.html) to a two-page letter PDF, front and back.

Serves the repo locally (the site plan is drawn from slides/data/site-map.js) and prints with headless Google Chrome.
Writes exports/agriculture-education-center-fact-sheet.pdf. Run: python tools/export_factsheet.py
Needs: Google Chrome. Type is the deck's (Iowan Old Style, Avenir Next), installed with macOS.
"""
import functools, http.server, os, socket, subprocess, tempfile, threading

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = os.path.join(ROOT, "exports", "agriculture-education-center-fact-sheet.pdf")

s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass


handler = functools.partial(Quiet, directory=ROOT)
srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
subprocess.run([CHROME, "--headless=new", f"--user-data-dir={tempfile.mkdtemp(prefix='factsheet-')}", "--no-pdf-header-footer",
                "--force-color-profile=srgb", "--virtual-time-budget=15000", "--run-all-compositor-stages-before-draw",
                f"--print-to-pdf={OUT}", f"http://127.0.0.1:{port}/factsheet/index.html"],
               check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
srv.shutdown()
print("wrote", OUT, round(os.path.getsize(OUT) / 1e6, 1), "MB")
