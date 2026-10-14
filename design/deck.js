// Shared slide runtime: scales the 1920x1080 stage to the window and runs build steps.
// Keys: → / space / click = next step, ← = previous step, R = replay, S = show all.
// URL: ?static shows the finished slide (for PDF export and thumbnails); ?play autoplays;
//      ?end opens on the last build step (used by the deck when stepping backwards).
// Inside the deck (index.html, slide in an iframe): when there are no more steps in a direction the
// slide asks the deck to change slides via postMessage, and the deck can drive it the same way.
(function () {
  const stage = document.querySelector(".stage");
  const params = new URLSearchParams(location.search);
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const root = document.documentElement;
  const inDeck = window.parent !== window;

  function fit() {
    const s = Math.min(innerWidth / 1920, innerHeight / 1080);
    stage.style.transform = `translate(${-960 * s}px, ${-540 * s}px) scale(${s})`;
  }
  addEventListener("resize", fit);
  fit();

  const steps = () => [...new Set([...document.querySelectorAll("[data-step]")].map(e => +e.dataset.step))].sort((a, b) => a - b);
  let current = 0;
  const hooks = [];
  const tell = msg => { if (inDeck) parent.postMessage(Object.assign({ deck: true }, msg), "*"); };

  function show(n) {
    current = Math.max(0, Math.min(n, Math.max(0, ...steps())));
    document.querySelectorAll("[data-step]").forEach(e => e.classList.toggle("in", +e.dataset.step <= current));
    hooks.forEach(h => h(current));
    const all = steps();
    tell({ type: "step", index: all.indexOf(current), count: all.length });
  }
  // next/prev return false when the slide has no more steps in that direction
  const next = () => { const s = steps().find(s => s > current); if (s === undefined) return false; show(s); return true; };
  const prev = () => { const s = steps().reverse().find(s => s < current); if (s === undefined) return false; show(s); return true; };
  const all = () => show(Math.max(0, ...steps()));
  const forward = () => { if (!next()) tell({ type: "next-slide" }); };
  const back = () => { if (!prev()) tell({ type: "prev-slide" }); };

  function play(delay = 700) {
    show(0);
    steps().forEach((s, i) => setTimeout(() => show(s), 400 + i * delay));
  }

  addEventListener("keydown", e => {
    if (e.key === "ArrowRight" || e.key === " " || e.key === "PageDown") { e.preventDefault(); forward(); }
    else if (e.key === "ArrowLeft" || e.key === "PageUp") { e.preventDefault(); back(); }
    else if (e.key.toLowerCase() === "r") play();
    else if (e.key.toLowerCase() === "s") all();
    else if (inDeck && (e.key.toLowerCase() === "f" || e.key === "Escape" || e.key === "Home" || e.key === "End")) tell({ type: "key", key: e.key });
  });
  stage.addEventListener("click", forward);
  addEventListener("message", e => {
    const d = e.data || {};
    if (d.cmd === "next") forward();
    else if (d.cmd === "prev") back();
    else if (d.cmd === "replay") play();
  });

  window.Deck = {
    onStep: f => hooks.push(f), show, next, prev, all, play,
    // The four design drivers (slides/drivers.html). A slide that a driver shapes carries its icon at the top right.
    drivers: {
      pasture: ["Pasture is scarce", `<circle cx="24" cy="24" r="23" fill="var(--pasture-tint)"/><path fill="none" stroke="var(--pasture)" stroke-width="3" stroke-linecap="round" d="M14 36c0-7 1-12 4-17M22 36c0-9 0-15 2-22M30 36c0-8 2-13 6-17M18 36c-1-5-3-8-6-10M34 36c1-4 3-6 6-8"/>`],
      reuse: ["Reuse first", `<circle cx="24" cy="24" r="23" fill="var(--education-tint)"/><path fill="none" stroke="var(--education)" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" d="M11 25l13-11 13 11M15 23v12h18V23M21 35v-7h6v7"/>`],
      module: ["Grow by module", `<circle cx="24" cy="24" r="23" fill="var(--cattle-tint)"/><g fill="none" stroke="var(--cattle)" stroke-width="3" stroke-linejoin="round"><rect x="10" y="20" width="8" height="14"/><rect x="20" y="20" width="8" height="14"/><rect x="30" y="20" width="8" height="14" stroke-dasharray="3 3"/></g><path d="M34 11v8M30 15h8" stroke="var(--cattle)" stroke-width="3" stroke-linecap="round"/>`],
      water: ["Protect the water", `<circle cx="24" cy="24" r="23" fill="var(--water-tint)"/><path fill="none" stroke="var(--water)" stroke-width="3" stroke-linecap="round" d="M10 20c4-4 7 4 11 0s7 4 11 0 5 2 6 1M10 29c4-4 7 4 11 0s7 4 11 0 5 2 6 1"/>`],
    },
    driverTags() {
      const keys = (document.body.dataset.drivers || "").split(/\s+/).filter(k => this.drivers[k]), stage = document.querySelector(".stage");
      if (!keys.length || !stage || stage.querySelector(".driver-tags")) return;
      stage.insertAdjacentHTML("beforeend", `<div class="driver-tags" data-step="0">${keys.map(k =>
        `<span class="driver-tag"><svg viewBox="0 0 48 48" aria-hidden="true">${this.drivers[k][1]}</svg>${this.drivers[k][0]}</span>`).join("")}</div>`);
    },
    start() {
      this.driverTags();
      if (params.has("static") || reduced) { root.classList.add("static"); all(); }
      else if (params.has("play")) play();
      else if (params.has("end")) all();
      else show(0);
    },
  };
})();
