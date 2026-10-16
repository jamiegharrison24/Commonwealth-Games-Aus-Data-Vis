/* Top of the Table — embeds every Vega-Lite spec on the page.
   Each chart lives in its own readable JSON file in js/specs/.
   Two shared themes keep typography and colour consistent:
   LIGHT for charts on the paper-coloured chapters, DARK for the "stadium night" chapters. */

const BASE = {
  background: null,
  font: 'Barlow',
  padding: 4,
  view: { stroke: null },
  title: { font: 'Barlow Condensed', fontSize: 18, fontWeight: 600, anchor: 'start' },
  text: { font: 'Barlow', fontSize: 12 }
};

const LIGHT = {
  ...BASE,
  axis: {
    labelFont: 'Barlow', labelFontSize: 12, labelColor: '#5d5b55',
    titleFont: 'Barlow', titleFontSize: 12, titleFontWeight: 600, titleColor: '#5d5b55', titlePadding: 8,
    domainColor: '#b9b5aa', tickColor: '#b9b5aa', gridColor: '#e9e5dc', gridDash: [2, 3]
  },
  legend: {
    labelFont: 'Barlow', labelFontSize: 12, labelColor: '#3b3a36',
    titleFont: 'Barlow', titleFontSize: 12, titleFontWeight: 600, titleColor: '#3b3a36', symbolStrokeWidth: 1.5
  },
  header: { labelFont: 'Barlow Semi Condensed', labelFontSize: 13, labelFontWeight: 600, labelColor: '#1d1d1b' },
  title: { ...BASE.title, color: '#1d1d1b', subtitleColor: '#5d5b55' },
  text: { ...BASE.text, color: '#3b3a36' }
};

const DARK = {
  ...BASE,
  axis: {
    labelFont: 'Barlow', labelFontSize: 12, labelColor: '#a9b4bb',
    titleFont: 'Barlow', titleFontSize: 12, titleFontWeight: 600, titleColor: '#a9b4bb', titlePadding: 8,
    domainColor: '#3a4a56', tickColor: '#3a4a56', gridColor: '#22323e', gridDash: [2, 3]
  },
  legend: {
    labelFont: 'Barlow', labelFontSize: 12, labelColor: '#e9ecee',
    titleFont: 'Barlow', titleFontSize: 12, titleFontWeight: 600, titleColor: '#a9b4bb', symbolStrokeWidth: 1.5
  },
  header: { labelFont: 'Barlow Semi Condensed', labelFontSize: 13, labelFontWeight: 600, labelColor: '#ffffff' },
  title: { ...BASE.title, color: '#ffffff', subtitleColor: '#a9b4bb' },
  text: { ...BASE.text, color: '#e9ecee' }
};

const CHARTS = [
  ['#vis-hero', '00_medal_skyline'],
  ['#vis-hosts', '01_host_cities_map'],
  ['#vis-flows', '02_flow_map'],
  ['#vis-britain', '02b_britain_inset'],
  ['#vis-distance', '02c_distance_line'],
  ['#vis-bump', '03_rank_bump_chart'],
  ['#vis-gap', '04_athlete_vs_medal_share_gap'],
  ['#vis-home', '05_home_advantage_dumbbell'],
  ['#vis-heatmap', '06_sport_heatmap'],
  ['#vis-mekko', '07_sport_marimekko'],
  ['#vis-greats', '08_greats_timeline'],
  ['#vis-strip', '09_athletics_strip_plot'],
  ['#vis-matrix', '10_olympic_standard_matrix'],
  ['#vis-units', '11_olympians_unit_chart'],
  ['#vis-waffle', '12_glasgow_waffle'],
  ['#vis-choropleth', '13_per_capita_choropleth']
];

window.__vizStatus = {};
window.__views = {};

CHARTS.forEach(([sel, file]) => {
  const el = document.querySelector(sel);
  if (!el) return;
  const dark = !!el.closest('.dark');
  const opts = {
    mode: 'vega-lite',
    config: dark ? DARK : LIGHT,
    renderer: 'svg',
    actions: { export: true, source: false, compiled: false, editor: true },
    tooltip: { theme: dark ? 'custom dark' : 'custom' }
  };
  vegaEmbed(sel, (window.INLINE_SPECS && window.INLINE_SPECS[file]) || `js/specs/${file}.vg.json`, opts)
    .then(res => { window.__vizStatus[file] = 'ok'; window.__views[file] = res.view; })
    .catch(err => { window.__vizStatus[file] = 'error: ' + err.message; console.error(file, err); });
});

/* Gentle reveal of figures as they scroll into view (skipped if the reader prefers reduced motion). */
(function reveal() {
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const items = document.querySelectorAll('.reveal');
  if (reduce || !('IntersectionObserver' in window)) { items.forEach(i => i.classList.add('in')); return; }
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });
  items.forEach(i => io.observe(i));
})();
