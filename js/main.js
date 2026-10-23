/* Top of the Table — embeds every Vega-Lite spec on the page.
   Each chart lives in its own readable JSON file in js/specs/.
   Two shared themes keep typography and colour consistent:
   LIGHT for charts on the paper-coloured chapters, DARK for the "stadium night" chapters. */

const BASE = {
  background: null,
  font: 'Libre Franklin, Helvetica Neue, Arial, sans-serif',
  padding: 4,
  view: { stroke: null },
  title: { font: 'Libre Franklin, Helvetica Neue, Arial, sans-serif', fontSize: 17, fontWeight: 800, anchor: 'start' },
  text: { font: 'Libre Franklin, Helvetica Neue, Arial, sans-serif', fontSize: 12 }
};

const LIGHT = {
  ...BASE,
  axis: {
    labelFont: 'Libre Franklin, Helvetica Neue, Arial, sans-serif', labelFontSize: 12, labelColor: '#5d5b55',
    titleFont: 'Libre Franklin, Helvetica Neue, Arial, sans-serif', titleFontSize: 12, titleFontWeight: 600, titleColor: '#5d5b55', titlePadding: 8,
    domainColor: '#b9b5aa', tickColor: '#b9b5aa', gridColor: '#e9e5dc', gridDash: [2, 3]
  },
  legend: {
    labelFont: 'Libre Franklin, Helvetica Neue, Arial, sans-serif', labelFontSize: 12, labelColor: '#3b3a36',
    titleFont: 'Libre Franklin, Helvetica Neue, Arial, sans-serif', titleFontSize: 12, titleFontWeight: 600, titleColor: '#3b3a36', symbolStrokeWidth: 1.5
  },
  header: { labelFont: 'Libre Franklin, Helvetica Neue, Arial, sans-serif', labelFontSize: 13, labelFontWeight: 600, labelColor: '#1d1d1b' },
  title: { ...BASE.title, color: '#1d1d1b', subtitleColor: '#5d5b55' },
  text: { ...BASE.text, color: '#3b3a36' }
};

const DARK = {
  ...BASE,
  axis: {
    labelFont: 'Libre Franklin, Helvetica Neue, Arial, sans-serif', labelFontSize: 12, labelColor: '#a9b4bb',
    titleFont: 'Libre Franklin, Helvetica Neue, Arial, sans-serif', titleFontSize: 12, titleFontWeight: 600, titleColor: '#a9b4bb', titlePadding: 8,
    domainColor: '#3a4a56', tickColor: '#3a4a56', gridColor: '#22323e', gridDash: [2, 3]
  },
  legend: {
    labelFont: 'Libre Franklin, Helvetica Neue, Arial, sans-serif', labelFontSize: 12, labelColor: '#e9ecee',
    titleFont: 'Libre Franklin, Helvetica Neue, Arial, sans-serif', titleFontSize: 12, titleFontWeight: 600, titleColor: '#a9b4bb', symbolStrokeWidth: 1.5
  },
  header: { labelFont: 'Libre Franklin, Helvetica Neue, Arial, sans-serif', labelFontSize: 13, labelFontWeight: 600, labelColor: '#ffffff' },
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

const fontsReady = (document.fonts && document.fonts.ready) ? document.fonts.ready : Promise.resolve();

fontsReady.then(() => CHARTS.forEach(([sel, file]) => {
  const el = document.querySelector(sel);
  if (!el) return;
  const dark = !!el.closest('.dark');
  const opts = {
    mode: 'vega-lite',
    config: dark ? DARK : LIGHT,
    renderer: 'svg',
    actions: false, // spec links sit in each caption; the menu button broke the right-hand sight line
    tooltip: { theme: dark ? 'custom dark' : 'custom' }
  };
  vegaEmbed(sel, (window.INLINE_SPECS && window.INLINE_SPECS[file]) || `js/specs/${file}.vg.json`, opts)
    .then(res => { window.__vizStatus[file] = 'ok'; window.__views[file] = res.view; if (window.__pick) applyPick(res.view); })
    .catch(err => { window.__vizStatus[file] = 'error: ' + err.message; console.error(file, err); });
}));

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

/* Running-track spine: a track down the left margin with one marker per chapter.
   A runner moves with scroll progress; markers link to chapters. Wide screens only (see CSS). */
(function spine() {
  const hero = document.querySelector('header.hero');
  const chapters = [...document.querySelectorAll('section.chapter, section.closing')];
  if (!chapters.length) return;
  const nav = document.createElement('nav');
  nav.className = 'spine'; nav.setAttribute('aria-label', 'Chapters');
  nav.innerHTML = '<div class="track"></div><div class="runner" aria-hidden="true"></div>';
  document.body.appendChild(nav);
  const runner = nav.querySelector('.runner');
  let stops = [];
  function build() {
    nav.querySelectorAll('.stop').forEach(n => n.remove());
    const docH = document.documentElement.scrollHeight - innerHeight;
    stops = chapters.map(s => {
      const no = (s.querySelector('.chapter-no') || {}).textContent || '';
      const h = s.querySelector('h2');
      if (!s.id) s.id = 'closing';
      const a = document.createElement('a');
      a.className = 'stop'; a.href = '#' + s.id;
      a.dataset.name = h ? h.textContent.trim() : 'Wrap-up';
      a.innerHTML = '<span>' + (/^\d+$/.test(no.trim()) ? +no : '\u2605') + '</span>';
      const p = Math.min(1, Math.max(0, s.offsetTop / docH));
      a.style.top = (p * 100) + '%';
      nav.appendChild(a);
      return { el: a, p };
    });
  }
  function update() {
    const docH = document.documentElement.scrollHeight - innerHeight;
    const p = docH > 0 ? scrollY / docH : 0;
    nav.classList.toggle('on', hero ? scrollY > hero.offsetHeight * 0.6 : true);
    runner.style.top = (p * 100) + '%';
    stops.forEach(st => st.el.classList.toggle('done', st.p <= p + 0.001));
  }
  addEventListener('scroll', update, { passive: true });
  addEventListener('resize', () => { build(); update(); });
  addEventListener('load', () => { build(); update(); });
  [800, 2000, 4000].forEach(t => setTimeout(() => { build(); update(); }, t)); // charts change page height as they render
  build(); update();
})();

/* Games links: a few Games named in the text are buttons. Clicking one marks that Games on every chart
   that has a Games in it (Segel & Heer's "links in the text setting visualization parameters").
   Charts that support it declare the params pickYear and pickLabel (see scripts/add_pick_games.py). */
function applyPick(view) {
  const p = window.__pick || { year: 0, label: '' };
  try { view.signal('pickYear', p.year).signal('pickLabel', p.label).runAsync(); } catch (e) { /* chart has no Games axis */ }
}
(function gamesLinks() {
  const links = [...document.querySelectorAll('.games-link')];
  if (!links.length) return;
  let active = null;
  function set(link) {
    active = link;
    window.__pick = link ? { year: +link.dataset.year, label: link.dataset.label } : null;
    links.forEach(l => l.setAttribute('aria-pressed', String(l === link)));
    Object.values(window.__views).forEach(applyPick);
  }
  links.forEach(l => l.addEventListener('click', () => set(active === l ? null : l)));
  // The highlight belongs to the passage that set it, so it clears once that chapter scrolls out of view.
  const io = new IntersectionObserver(entries => entries.forEach(e => {
    if (!e.isIntersecting && active && e.target.contains(active)) set(null);
  }));
  new Set(links.map(l => l.closest('section') || document.body)).forEach(sec => io.observe(sec));
})();
