"""Export the deck to a PDF for review (architect, 2026-10-15: the County web filter blocks github.io).

Serves the repo locally, drives headless Google Chrome over the DevTools protocol, and captures each slide at
1920 x 1080 (x1.3 for sharpness, small enough to email). Slides that tell their story in steps on a map or plan get one page per step;
the rest get one page at their last step.
Pages are JPEGs assembled into one PDF.

Writes exports/stakeholder-review-draft.pdf. Run: python tools/export_pdf.py
Needs: Google Chrome, websocket-client, pillow.
"""
import io, json, os, re, socket, subprocess, sys, tempfile, threading, time, base64, urllib.request
import functools, http.server
from PIL import Image
import websocket

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = os.path.join(ROOT, "exports")
STEPPED = {"site", "paddocks", "plan-logic", "ag-area", "bud-box", "site-plan", "water-site", "red-house"}     # one page per step
SCALE = 1.3


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


# ---- local server for the repo
port = free_port()
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
handler.log_message = lambda *a: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
threading.Thread(target=srv.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{port}/"

# ---- slide list and build stamp from index.html
idx = open(os.path.join(ROOT, "index.html")).read()
slides = re.findall(r'\{ file: "(slides/[^"]+)", title: "([^"]+)" \}', idx)
build = re.search(r'const BUILD = "([^"]+)"', idx).group(1)

# ---- headless Chrome
dport = free_port()
prof = tempfile.mkdtemp(prefix="deckpdf-")
chrome = subprocess.Popen([CHROME, "--headless=new", f"--remote-debugging-port={dport}", f"--user-data-dir={prof}",
                           "--hide-scrollbars", "--force-color-profile=srgb", f"--remote-allow-origins=http://127.0.0.1:{dport}", "--window-size=1920,1080", "about:blank"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for _ in range(60):
    try:
        tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{dport}/json")); break
    except Exception:
        time.sleep(.25)
ws_url = next(t["webSocketDebuggerUrl"] for t in tabs if t["type"] == "page")
ws = websocket.create_connection(ws_url, timeout=60, origin=f"http://127.0.0.1:{dport}")
_id = [0]


def cdp(method, **params):
    _id[0] += 1; ws.send(json.dumps({"id": _id[0], "method": method, "params": params}))
    while True:
        m = json.loads(ws.recv())
        if m.get("id") == _id[0]:
            if "error" in m: raise RuntimeError(m["error"])
            return m.get("result", {})


def js(expr):
    r = cdp("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
    return r.get("result", {}).get("value")


cdp("Page.enable"); cdp("Runtime.enable")
cdp("Emulation.setDeviceMetricsOverride", width=1920, height=1080, deviceScaleFactor=SCALE, mobile=False)


def load(url):
    cdp("Page.navigate", url=url)
    for _ in range(80):
        time.sleep(.25)
        if js("document.readyState") == "complete" and js("!!window.Deck"):
            break
    time.sleep(1.2)                                         # fonts, maps


def shot():
    data = cdp("Page.captureScreenshot", format="jpeg", quality=80)["data"]
    return Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB")


pages = []
for f, title in slides:
    name = os.path.basename(f)[:-5]
    load(f"{BASE}{f}?v={build}")
    last = js("Math.max(0, ...[...document.querySelectorAll('[data-step]')].map(e => +e.dataset.step || 0))") or 0
    steps = range(last + 1) if name in STEPPED else [last]
    for i in steps:
        js(f"Deck.show({i})"); time.sleep(2.6 if name == "bud-box" else 2.0)   # camera flights, fades, the cattle moves settle
        pages.append(shot()); print(f"{len(pages):3d}  {title}  step {i + 1}/{last + 1}")
    # the Red House opens with its program colours on (owner, 2026-10-19), so its stepped pages already show them

ws.close(); chrome.terminate(); srv.shutdown()
os.makedirs(OUT, exist_ok=True)
pdf = os.path.join(OUT, "stakeholder-review-draft.pdf")
pages[0].save(pdf, save_all=True, append_images=pages[1:], resolution=125, quality=80)
print("wrote", pdf, len(pages), "pages,", round(os.path.getsize(pdf) / 1e6, 1), "MB")
