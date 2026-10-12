// Shared pan/zoom viewer for any inline SVG drawing on a slide.
//   const v = Viewer(svgElement, { ftPerUnit, presets: [{ label, box: [x, y, w, h] }], north: degrees });
//   v.flyTo([x, y, w, h], ms)   glide to a framing (used by build steps)
//   v.home([x, y, w, h])        change what "reset" returns to
// Mark SVG elements data-fixed (labels) or data-w="<width>" [data-dash="a b"] (strokes) to keep them near constant size on screen.
// Scroll = zoom toward the cursor · drag = pan · pinch = zoom · double-click = reset.
// A plain click (no drag) still falls through to the deck, so it advances the slide as usual.
// ftPerUnit adds a live scale bar. north (degrees clockwise from up, in screen terms) adds a north arrow.
(function () {
  const css = `
  .vw { position: relative; touch-action: none; cursor: grab; user-select: none; }
  .vw.drag { cursor: grabbing; }
  .vw-ui { position: absolute; right: 14px; top: 14px; display: flex; gap: 6px; align-items: center; flex-wrap: wrap; justify-content: flex-end; max-width: 70%; }
  .vw-ui button { all: unset; cursor: pointer; font: 600 14px/1 var(--sans, sans-serif); color: var(--ink, #222); background: rgba(255,255,255,.94);
                  border: 1.5px solid var(--line, #bbb); border-radius: 9px; padding: 8px 11px; }
  .vw-ui button:hover { background: #fff; border-color: var(--ink, #222); }
  .vw-ui button.sq { width: 16px; text-align: center; font-size: 17px; padding: 6px 9px; }
  .vw-ui .sep { width: 6px; }
  .vw-scale { position: absolute; right: 14px; bottom: 12px; background: rgba(255,255,255,.92); padding: 8px 12px 6px; border-radius: 8px;
              font: 500 13px/1 var(--sans, sans-serif); color: var(--muted, #777); pointer-events: none; }
  .vw-north { position: absolute; left: 14px; top: 14px; width: 54px; height: 54px; border-radius: 50%; background: rgba(255,255,255,.94);
              border: 1.5px solid var(--line, #bbb); display: grid; place-items: center; pointer-events: none; }
  .vw-hint { position: absolute; left: 50%; top: 14px; transform: translateX(-50%); font: 500 13px/1 var(--sans, sans-serif); color: var(--muted, #777);
             background: rgba(255,255,255,.9); padding: 7px 11px; border-radius: 8px; pointer-events: none; transition: opacity .6s; }
  .vw-hint.gone { opacity: 0; }`;
  if (!document.getElementById("vw-css")) {
    const st = document.createElement("style"); st.id = "vw-css"; st.textContent = css; document.head.appendChild(st);
  }

  window.Viewer = function (svg, opts) {
    opts = opts || {};
    const host = svg.parentNode;
    host.classList.add("vw");
    let vb = svg.getAttribute("viewBox").split(/[ ,]+/).map(Number);
    let homeBox = vb.slice(), raf, moved = false;
    const aspect = () => svg.clientWidth / svg.clientHeight;
    // grow a box to the element's aspect ratio so the drawing never letterboxes or jumps
    function fit(b) {
      const a = aspect(); let [x, y, w, h] = b;
      if (w / h < a) { const nw = h * a; x -= (nw - w) / 2; w = nw; } else { const nh = w / a; y -= (nh - h) / 2; h = nh; }
      return [x, y, w, h];
    }
    const listeners = [];
    // Elements marked data-fixed (labels, callouts) and data-w / data-dash (line weights, dash patterns) are
    // counter-scaled as you zoom, so they stay close to their on-screen size instead of ballooning.
    let baseW = null;
    const fixedEls = [...svg.querySelectorAll("[data-fixed]")], wEls = [...svg.querySelectorAll("[data-w]")];
    function set(b) {
      vb = b; svg.setAttribute("viewBox", b.map(v => +v.toFixed(2)).join(" "));
      if (baseW) {
        const inv = Math.pow(vb[2] / baseW, opts.damp === undefined ? 0.8 : opts.damp);
        svg.style.setProperty("--inv", inv);
        fixedEls.forEach(e => { e.style.transform = `scale(${inv})`; });
        wEls.forEach(e => { e.style.strokeWidth = e.dataset.w * inv;
          if (e.dataset.dash) e.style.strokeDasharray = e.dataset.dash.split(" ").map(v => v * inv).join(" "); });
      }
      listeners.forEach(f => f(vb));
    }
    function flyTo(b, ms) {
      cancelAnimationFrame(raf);
      const to = fit(b), from = vb.slice(), t0 = performance.now();
      if (!ms) return set(to);
      (function tick(t) {
        const k = Math.min(1, (t - t0) / ms), e = k < .5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2;
        set(from.map((v, i) => v + (to[i] - v) * e));
        if (k < 1) raf = requestAnimationFrame(tick);
      })(t0);
    }
    const unitsPerPx = () => vb[2] / svg.getBoundingClientRect().width;
    function point(ev) {
      const r = svg.getBoundingClientRect();
      return [vb[0] + (ev.clientX - r.left) / r.width * vb[2], vb[1] + (ev.clientY - r.top) / r.height * vb[3]];
    }
    function zoomAt(px, py, f) {
      const max = fit(homeBox)[2] * 1.25, min = fit(homeBox)[2] / 16;
      const w = Math.max(min, Math.min(max, vb[2] * f)), k = w / vb[2];
      cancelAnimationFrame(raf);
      set([px - (px - vb[0]) * k, py - (py - vb[1]) * k, w, vb[3] * k]);
    }
    svg.addEventListener("wheel", ev => {
      ev.preventDefault();
      const [px, py] = point(ev);
      zoomAt(px, py, Math.exp(ev.deltaY * (ev.ctrlKey ? 0.01 : 0.0016)));
      hint.classList.add("gone");
    }, { passive: false });

    const ptrs = new Map(); let pinch0 = null;
    svg.addEventListener("pointerdown", ev => {
      if (ev.button !== 0) return;
      ptrs.set(ev.pointerId, [ev.clientX, ev.clientY]); moved = false;
      svg.setPointerCapture(ev.pointerId);
      if (ptrs.size === 2) { const p = [...ptrs.values()]; pinch0 = Math.hypot(p[0][0] - p[1][0], p[0][1] - p[1][1]); }
    });
    svg.addEventListener("pointermove", ev => {
      if (!ptrs.has(ev.pointerId)) return;
      const prev = ptrs.get(ev.pointerId), dx = ev.clientX - prev[0], dy = ev.clientY - prev[1];
      ptrs.set(ev.pointerId, [ev.clientX, ev.clientY]);
      if (ptrs.size === 2 && pinch0) {
        const p = [...ptrs.values()], d = Math.hypot(p[0][0] - p[1][0], p[0][1] - p[1][1]);
        const mid = point({ clientX: (p[0][0] + p[1][0]) / 2, clientY: (p[0][1] + p[1][1]) / 2 });
        zoomAt(mid[0], mid[1], pinch0 / d); pinch0 = d; moved = true; return;
      }
      if (Math.abs(dx) + Math.abs(dy) < 1) return;
      if (!moved && Math.hypot(dx, dy) < 3) return;
      moved = true; host.classList.add("drag"); hint.classList.add("gone");
      const u = unitsPerPx(); cancelAnimationFrame(raf);
      set([vb[0] - dx * u, vb[1] - dy * u, vb[2], vb[3]]);
    });
    const up = ev => { ptrs.delete(ev.pointerId); if (ptrs.size < 2) pinch0 = null; host.classList.remove("drag"); };
    svg.addEventListener("pointerup", up); svg.addEventListener("pointercancel", up);
    // a drag must not count as a click on the slide (which would advance it)
    host.addEventListener("click", ev => { if (moved) { ev.stopPropagation(); moved = false; } }, true);
    svg.addEventListener("dblclick", ev => { ev.stopPropagation(); flyTo(homeBox, 600); });

    // controls
    const ui = document.createElement("div"); ui.className = "vw-ui";
    const btn = (label, fn, cls) => { const b = document.createElement("button"); b.textContent = label; if (cls) b.className = cls;
      b.addEventListener("click", ev => { ev.stopPropagation(); fn(); }); b.addEventListener("pointerdown", ev => ev.stopPropagation()); ui.appendChild(b); return b; };
    (opts.presets || []).forEach(p => btn(p.label, () => flyTo(p.box, 900)));
    if ((opts.presets || []).length) { const s = document.createElement("span"); s.className = "sep"; ui.appendChild(s); }
    const centre = () => [vb[0] + vb[2] / 2, vb[1] + vb[3] / 2];
    btn("+", () => { const c = centre(); zoomAt(c[0], c[1], 1 / 1.5); }, "sq").setAttribute("aria-label", "Zoom in");
    btn("−", () => { const c = centre(); zoomAt(c[0], c[1], 1.5); }, "sq").setAttribute("aria-label", "Zoom out");
    btn("Reset", () => flyTo(homeBox, 600));
    if (opts.uiStyle) ui.style.cssText = opts.uiStyle;
    host.appendChild(ui);
    const hint = document.createElement("div"); hint.className = "vw-hint"; hint.textContent = "Scroll to zoom · drag to pan · double-click to reset";
    host.appendChild(hint); setTimeout(() => hint.classList.add("gone"), 6000);

    if (opts.north !== undefined) {
      const n = document.createElement("div"); n.className = "vw-north";
      n.innerHTML = `<svg width="44" height="44" viewBox="-22 -22 44 44"><g transform="rotate(${opts.north})">
        <path d="M0 -18 L7 10 L0 5 L-7 10 Z" fill="var(--ink, #222)"/></g></svg>`;
      n.title = "North"; host.appendChild(n);
      const lab = document.createElement("div");
      lab.style.cssText = "position:absolute;left:74px;top:30px;font:700 15px/1 var(--sans,sans-serif);color:var(--ink,#222);pointer-events:none;" +
        "background:rgba(255,255,255,.9);padding:4px 7px;border-radius:6px";
      lab.textContent = "N"; host.appendChild(lab);
    }
    if (opts.ftPerUnit) {
      const sc = document.createElement("div"); sc.className = "vw-scale"; host.appendChild(sc);
      const draw = () => {
        const stagePxPerUnit = svg.clientWidth / vb[2];
        const nice = [5, 10, 20, 50, 100, 200, 250, 500, 1000, 2000];
        const ft = nice.reduce((best, n) => (n / opts.ftPerUnit * stagePxPerUnit <= 170 ? n : best), nice[0]);
        const w = ft / opts.ftPerUnit * stagePxPerUnit;
        sc.innerHTML = `<svg width="${w + 46}" height="24"><rect width="${w / 2}" height="6" fill="var(--ink,#222)"/>
          <rect x="${w / 2}" width="${w / 2}" height="6" fill="none" stroke="var(--ink,#222)"/>
          <text y="21" font-size="13" fill="currentColor">0</text><text x="${w}" y="21" font-size="13" text-anchor="middle" fill="currentColor">${ft} ft</text></svg>`;
      };
      listeners.push(draw); draw();
    }
    baseW = fit(opts.base || vb)[2];
    set(fit(vb));
    return { flyTo, home: b => { homeBox = b.slice(); }, reset: () => flyTo(homeBox, 600), onChange: f => listeners.push(f), get box() { return vb.slice(); } };
  };
})();
