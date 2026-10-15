// Investment Levels by program element. Hand-maintained: Owner/architect direction recorded in NOTES.md.
// confirmed: false marks a placement proposed by Claude, shown on the slide with a dashed "to confirm" outline.
// Pasture CE values come from pasture-capacity.js (generated from the worksheet), not from here.
window.LEVELS = {
  levels: [
    { n: 1, name: "Level 1", title: "Lightest touch", note: "Reuse every existing building with minimum renovation" },
    { n: 2, name: "Level 2", title: "Better management", note: "Rotational grazing and first new facilities" },
    { n: 3, name: "Level 3", title: "Best case", note: "Full program, sized to best-case pasture capacity" },
  ],
  // pen module: 7 pens; a new barn is 14 pens (2 modules). Existing 7 pens stay in use at every Level.
  pens: {
    module: 7, barn: 14, pen_ft: [12, 24], aisle_ft: 14, aisle_confirmed: true,
    existing: 7,
    byLevel: [
      { level: 1, newBarns: 0, confirmed: true },
      { level: 2, newBarns: 1, confirmed: true },
      { level: 3, newBarns: 2, confirmed: true },
    ],
  },
  rows: [
    // Civil (2026-10-14): permitting, stormwater and floodplain compensation are done for the whole plan up front;
    // only the buildings and programs inside the site are phased by Level.
    { key: "water", label: "Site work: stormwater, floodplain compensation", cells: [
      { text: "All of it, permitted and built up front", confirmed: true },
      { text: "Same as Level 1", confirmed: true },
      { text: "Same as Level 1", confirmed: true } ] },
    { key: "pasture", label: "Pasture (Beginning Rancher herd)", cells: [
      { text: "Site pasture, conservative management", ce: 1, confirmed: true },
      { text: "Rotational grazing on site pasture", ce: 2, confirmed: true },
      { text: "Add the bonus pasture", ce: 3, confirmed: true } ] },
    { key: "cattle", label: "4-H cow & calf pens", cells: [
      { text: "Reuse the 7 existing pens", pens: 1, confirmed: true },
      { text: "Add one 14-pen barn", pens: 2, confirmed: true },
      { text: "Add a second 14-pen barn", pens: 3, confirmed: true } ] },
    { key: "cattle", label: "Pasture-stock handling", cells: [
      { text: "Holding pens 1 to 5, Bud Box, chute and scale", confirmed: true },
      { text: "Same as Level 1", confirmed: true },
      { text: "Same as Level 1", confirmed: true } ] },
    // Swine and small animals share one row: they use the same kinds of pens and barns (architect, 2026-10-13).
    { key: "swine", label: "Swine & small animals", cells: [
      { text: "Hogs move into the existing barn, about 32 pens; the 10 old hog pens give way to the site improvements", confirmed: true },
      { text: "Small animal barn A, 32 pens: a clean swap that frees the existing barn for storage", confirmed: true },
      { text: "Small animal barn B: extend south to the code limit, 5,500 sf", confirmed: true } ] },
    // Poultry is not a "small animal" here: it is housed in the unfinished barn from Level 1 and stays there (architect, 2026-10-13).
    { key: "small_animal", label: "Poultry", cells: [
      { text: "In the unfinished barn", confirmed: true },
      { text: "Same as Level 1", confirmed: true },
      { text: "Same as Level 1", confirmed: true } ] },
    { key: "arena", label: "Arena / demonstration", cells: [
      { text: "None (use the turnout yards)", confirmed: true },
      { text: "Grooming area", confirmed: true },
      { text: "Arena, built out from the grooming area", confirmed: true } ] },
    { key: "education", label: "Red House", cells: [
      { text: "Renovate: classroom, conference, 4 offices, demo kitchen", confirmed: true },
      { text: "Add Office 5, men's & women's restrooms", confirmed: true },
      { text: "Add event space / classroom addition + equipment carport", confirmed: true } ] },
    // The residence beside the horticulture area is a Level 3 element; before that the spot has camper / RV hookups (architect, 2026-10-13).
    { key: "education", label: "Residence", cells: [
      { text: "Hookups for a camper or RV", confirmed: true },
      { text: "Same as Level 1", confirmed: true },
      { text: "Residence", confirmed: true } ] },
    { key: "horticulture", label: "Horticulture", cells: [
      { text: "Raised beds and pots", confirmed: true },
      { text: "Beds with irrigation", confirmed: true },
      { text: "Structured shade area, planting tables, irrigation", confirmed: true } ] },
  ],
};
