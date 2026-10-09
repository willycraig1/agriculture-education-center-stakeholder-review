// Shared slide runtime: scales the 1920x1080 stage to the window and runs build steps.
// Keys: → / space / click = next step, ← = previous step, R = replay, S = show all.
// URL: ?static shows the finished slide (for PDF export and thumbnails); ?play autoplays.
(function () {
  const stage = document.querySelector(".stage");
  const params = new URLSearchParams(location.search);
  const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const root = document.documentElement;

  function fit() {
    const s = Math.min(innerWidth / 1920, innerHeight / 1080);
    stage.style.transform = `translate(${-960 * s}px, ${-540 * s}px) scale(${s})`;
  }
  addEventListener("resize", fit);
  fit();

  const steps = () => [...new Set([...document.querySelectorAll("[data-step]")].map(e => +e.dataset.step))].sort((a, b) => a - b);
  let current = 0;
  const hooks = [];

  function show(n) {
    current = Math.max(0, Math.min(n, Math.max(0, ...steps())));
    document.querySelectorAll("[data-step]").forEach(e => e.classList.toggle("in", +e.dataset.step <= current));
    hooks.forEach(h => h(current));
  }
  const next = () => { const s = steps().find(s => s > current); if (s !== undefined) show(s); };
  const prev = () => { const s = steps().reverse().find(s => s < current); show(s === undefined ? 0 : s); };
  const all = () => show(Math.max(0, ...steps()));

  function play(delay = 700) {
    show(0);
    steps().forEach((s, i) => setTimeout(() => show(s), 400 + i * delay));
  }

  addEventListener("keydown", e => {
    if (e.key === "ArrowRight" || e.key === " " || e.key === "PageDown") next();
    else if (e.key === "ArrowLeft" || e.key === "PageUp") prev();
    else if (e.key.toLowerCase() === "r") play();
    else if (e.key.toLowerCase() === "s") all();
  });
  stage.addEventListener("click", next);

  window.Deck = {
    onStep: f => hooks.push(f), show, next, prev, all, play,
    start() {
      if (params.has("static") || reduced) { root.classList.add("static"); all(); }
      else if (params.has("play")) play();
      else show(0);
    },
  };
})();
