"""Export the site plan as Arch D (36" x 24") vector PDF sheets.

AS-0: the existing site on the aerial at 1" = 100'. AS-1: the main property at Level 3, 1" = 100'.
AS-2: the campus at Level 3, 1" = 40'.
Serves the repo locally and prints tools/sheet.html with headless Google Chrome (--print-to-pdf; the page sets
@page to 36 x 24 in, so the output is vector with text kept). Layers and colours follow slides/site-plan.html at Level 3.

Writes exports/site-plan-AS-0.pdf, -AS-1.pdf, and -AS-2.pdf (or only the sheets named: existing, site, campus).
Run: python tools/export_sheets.py [--date YYYY-MM-DD] [sheet ...]   (after tools/build_site_map.py)
Needs: Google Chrome.
"""
import argparse, datetime, functools, http.server, os, socket, subprocess, tempfile, threading, time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CHROME = next((c for c in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                            r"C:\Program Files\Google\Chrome\Application\chrome.exe") if os.path.exists(c)), "google-chrome")
OUT = os.path.join(ROOT, "exports")
SHEETS = [("existing", "site-plan-AS-0.pdf"), ("site", "site-plan-AS-1.pdf"), ("campus", "site-plan-AS-2.pdf")]
ap = argparse.ArgumentParser(); ap.add_argument("--date", default=datetime.date.today().isoformat()); ap.add_argument("sheets", nargs="*")
ap.add_argument("--option", choices=["meander"], help="print an option to its own PDFs (AS-1 and AS-2), leaving the base sheets alone")
ARGS = ap.parse_args()
if ARGS.option: SHEETS = [(k, n.replace(".pdf", f"-option-{ARGS.option}.pdf")) for k, n in SHEETS if k != "existing"]
OPTION = f"&option={ARGS.option}" if ARGS.option else ""

s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
handler.log_message = lambda *a: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()

os.makedirs(OUT, exist_ok=True)
date = ARGS.date
for key, name in SHEETS:
    if ARGS.sheets and key not in ARGS.sheets: continue
    path = os.path.join(OUT, name)
    if os.path.exists(path): os.remove(path)                # so a sheet that fails to print cannot pass for a new one
    subprocess.run([CHROME, "--headless=new", f"--user-data-dir={tempfile.mkdtemp(prefix='sheetpdf-')}",
                    "--force-color-profile=srgb", "--no-pdf-header-footer", "--window-size=3456,2304",
                    "--virtual-time-budget=8000", f"--print-to-pdf={path}",
                    f"http://127.0.0.1:{port}/tools/sheet.html?sheet={key}&date={date}{OPTION}"],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
    # On Windows chrome.exe hands off to a child process and returns at once: wait for the finished file.
    last, deadline = -1, time.time() + 180
    while time.time() < deadline:
        size = os.path.getsize(path) if os.path.exists(path) else -1
        if size > 0 and size == last: break
        last = size; time.sleep(2)
    else:
        raise SystemExit(f"{name} did not finish printing")
    print("wrote", path, round(os.path.getsize(path) / 1e6, 1), "MB")
srv.shutdown()
