/* ============================================================================
   Astrology AI — Product SPA
   App shell + client router + all screens. Consumes the /api/product/* layer.
   The browser NEVER computes astrology; it renders structured results.
   ========================================================================== */

/* ---- API client --------------------------------------------------------- */
const API = {
  async get(path) {
    const res = await fetch(path, { credentials: 'include', headers: { 'Accept': 'application/json' } });
    return handle(res);
  },
  async post(path, body) {
    const res = await fetch(path, {
      method: 'POST', credentials: 'include',
      headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body || {})
    });
    return handle(res);
  },
  async del(path) {
    const res = await fetch(path, { method: 'DELETE', credentials: 'include' });
    return handle(res);
  }
};
async function handle(res) {
  if (res.status === 401) { window.location.href = '/login'; throw new Error('unauthorized'); }
  let data = null;
  try { data = await res.json(); } catch { data = null; }
  if (!res.ok) {
    const err = new Error((data && data.detail) || `Request failed (${res.status})`);
    err.status = res.status; err.data = data; throw err;
  }
  return data;
}

/* ---- tiny DOM helpers --------------------------------------------------- */
const $ = (sel, root = document) => root.querySelector(sel);
const h = (html) => { const t = document.createElement('template'); t.innerHTML = html.trim(); return t.content.firstElementChild; };
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const toneClass = (t) => `tone-${t || 'neutral'}`;

/* ---- icon set (single coherent stroke system) --------------------------- */
const ICON = {
  home: '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>',
  chart: '<circle cx="12" cy="12" r="9"/><path d="M12 3v18M3 12h18"/>',
  forecast: '<path d="M3 12h4l3 8 4-16 3 8h4"/>',
  people: '<circle cx="9" cy="8" r="3.2"/><path d="M3.5 20a5.5 5.5 0 0 1 11 0"/><path d="M16 5.5a3 3 0 0 1 0 5.8"/><path d="M17.5 14.4A5.5 5.5 0 0 1 21 20"/>',
  calendar: '<rect x="3.5" y="5" width="17" height="16" rx="2.5"/><path d="M3.5 9.5h17M8 3v4M16 3v4"/>',
  profile: '<circle cx="12" cy="8" r="4"/><path d="M4 20a8 8 0 0 1 16 0"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 13a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-2.7 1.1V21a2 2 0 1 1-4 0v-.2a1.6 1.6 0 0 0-2.7-1.1l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1A1.6 1.6 0 0 0 4.6 13H4a2 2 0 1 1 0-4h.2a1.6 1.6 0 0 0 1.1-2.7l-.1-.1A2 2 0 1 1 8 3.4l.1.1a1.6 1.6 0 0 0 2.7-1.1V2a2 2 0 1 1 4 0v.2a1.6 1.6 0 0 0 2.7 1.1l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1A1.6 1.6 0 0 0 19.4 9H20a2 2 0 1 1 0 4z"/>',
  chevron: '<path d="M9 6l6 6-6 6"/>',
  back: '<path d="M15 6l-6 6 6 6"/>',
  close: '<path d="M6 6l12 12M18 6L6 18"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  bell: '<path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/>',
  sun: '<circle cx="12" cy="12" r="4.5"/><path d="M12 1v2.5M12 20.5V23M4.2 4.2l1.8 1.8M18 18l1.8 1.8M1 12h2.5M20.5 12H23M4.2 19.8 6 18M18 6l1.8-1.8"/>',
  moon: '<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',
  spark: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
  logout: '<path d="M15 4h3a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-3"/><path d="M10 12H3M6 8l-4 4 4 4"/>',
  share: '<path d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7"/><path d="M12 3v13M8 7l4-4 4 4"/>',
  heart: '<path d="M12 20s-7-4.5-9.5-9A4.5 4.5 0 0 1 12 6a4.5 4.5 0 0 1 9.5 5c-2.5 4.5-9.5 9-9.5 9z"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  trash: '<path d="M4 7h16M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2M6 7l1 13a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-13"/>',
  location: '<path d="M12 21s-7-6-7-11a7 7 0 0 1 14 0c0 5-7 11-7 11z"/><circle cx="12" cy="10" r="2.5"/>',
  crown: '<path d="M3 8l4 4 5-7 5 7 4-4v10H3z"/>',
};
const svg = (name, cls = 'ic') =>
  `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICON[name] || ''}</svg>`;

/* ---- global state ------------------------------------------------------- */
const State = {
  user: null,
  summary: null,
  cache: {},           // screen data cache
};

const TABS = [
  { id: 'home', label: 'Home', icon: 'home' },
  { id: 'chart', label: 'Chart', icon: 'chart' },
  { id: 'forecast', label: 'Forecast', icon: 'forecast' },
  { id: 'relationships', label: 'People', icon: 'people' },
  { id: 'calendar', label: 'Calendar', icon: 'calendar' },
];

/* ---- theme -------------------------------------------------------------- */
function applyAppearance(pref) {
  localStorage.setItem('astro_appearance', pref || 'system');
  const dark = pref === 'dark' || (pref === 'system' && matchMedia('(prefers-color-scheme: dark)').matches);
  document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
}
matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
  if ((localStorage.getItem('astro_appearance') || 'system') === 'system')
    applyAppearance('system');
});

/* ---- toast -------------------------------------------------------------- */
let toastTimer;
function toast(msg) {
  const t = $('#toast'); t.textContent = msg; t.classList.add('show');
  clearTimeout(toastTimer); toastTimer = setTimeout(() => t.classList.remove('show'), 2600);
}

/* ---- bottom sheet ------------------------------------------------------- */
function openSheet(title, bodyHtml) {
  const sheet = $('#sheet'), scrim = $('#sheet-scrim');
  sheet.innerHTML = `<div class="grabber"></div>
    <div class="row-between" style="margin-bottom:12px;">
      <h2>${esc(title)}</h2>
      <button class="icon-btn ghost" id="sheet-close" aria-label="Close">${svg('close', 'ic')}</button>
    </div>${bodyHtml}`;
  scrim.classList.add('open'); sheet.classList.add('open');
  document.body.style.overflow = 'hidden';
  $('#sheet-close').onclick = closeSheet;
  scrim.onclick = closeSheet;
  document.addEventListener('keydown', escClose);
}
function closeSheet() {
  $('#sheet').classList.remove('open'); $('#sheet-scrim').classList.remove('open');
  document.body.style.overflow = '';
  document.removeEventListener('keydown', escClose);
}
function escClose(e) { if (e.key === 'Escape') closeSheet(); }

/* ---- reusable render bits ---------------------------------------------- */
const skeletonScreen = () => `
  <div class="screen">
    <div class="skeleton sk-line" style="width:40%;height:22px;"></div>
    <div class="skeleton sk-card" style="margin-top:16px;"></div>
    <div class="skeleton sk-card" style="margin-top:16px;height:80px;"></div>
    <div class="skeleton sk-card" style="margin-top:16px;height:80px;"></div>
  </div>`;

function errorState(msg, retryFn) {
  const el = h(`<div class="state">
    ${svg('info', 'state-ic')}
    <h3>Something went off course</h3>
    <p>${esc(msg || 'We couldn’t load this right now.')}</p>
    <button class="btn btn-secondary" id="retry-btn">Try again</button>
  </div>`);
  el.querySelector('#retry-btn').onclick = retryFn;
  return el;
}

function badge(status, tone) {
  if (!status) return '';
  return `<span class="badge ${toneClass(tone)}"><span class="dot"></span>${esc(status)}</span>`;
}

/* ============================================================================
   ROUTER
   ========================================================================== */
const Screens = {}; // registered below

function currentRoute() {
  const p = location.pathname.replace(/^\/app\/?/, '').split('/').filter(Boolean);
  return { name: p[0] || 'home', param: p[1] || null };
}
function navigate(path, replace = false) {
  const url = '/app' + (path ? '/' + path : '');
  if (replace) history.replaceState({}, '', url); else history.pushState({}, '', url);
  render();
}
window.addEventListener('popstate', render);

/* ============================================================================
   APP BOOT
   ========================================================================== */
async function boot() {
  registerSW();
  try {
    State.summary = await API.get('/api/product/summary');
    State.user = State.summary.user;
  } catch (e) {
    if (e.status === 401) return; // redirected to login
    // Non-auth failure — still render shell with error inside.
  }
  if (State.summary) applyAppearance(State.summary.appearance || localStorage.getItem('astro_appearance') || 'system');

  // No birth profile yet → onboarding (unless already there).
  if (State.summary && !State.summary.has_profile && currentRoute().name !== 'onboarding') {
    navigate('onboarding', true); return;
  }
  render();
}

function renderShell(activeName) {
  const root = $('#app-root');
  if (root.dataset.shell === '1') return; // shell already mounted
  root.dataset.shell = '1';
  root.innerHTML = `
    <div class="app-frame">
      <aside class="sidebar">
        <div class="brand"><img class="logo" src="/static/icons/icon-192.png" alt=""><b>Astrology AI</b></div>
        <nav id="side-nav"></nav>
        <div class="side-foot">
          <button class="side-link" data-nav="profile">${svg('profile')}<span>Profile</span></button>
        </div>
      </aside>
      <div class="main-col">
        <header class="topbar">
          <div class="tb-left">
            <button class="icon-btn ghost mobile-only" id="tb-back" style="display:none" aria-label="Back">${svg('back')}</button>
            <h1 id="tb-title">Home</h1>
          </div>
          <div class="tb-actions" id="tb-actions"></div>
        </header>
        <main class="screen-scroll" id="screen-host"></main>
      </div>
    </div>
    <nav class="tabbar" id="tabbar"></nav>`;

  // Build nav (sidebar + tabbar)
  const side = $('#side-nav'), tabbar = $('#tabbar');
  side.innerHTML = TABS.map(t => `<button class="side-link" data-nav="${t.id}">${svg(t.icon)}<span>${t.label}</span></button>`).join('');
  tabbar.innerHTML = TABS.map(t => `<button class="tab" data-nav="${t.id}">${svg(t.icon)}<span>${t.label}</span></button>`).join('');
  root.querySelectorAll('[data-nav]').forEach(b => b.onclick = () => navigate(b.dataset.nav));
}

function setActiveNav(name) {
  document.querySelectorAll('.side-link[data-nav]').forEach(b => b.classList.toggle('active', b.dataset.nav === name));
  document.querySelectorAll('.tab[data-nav]').forEach(b => b.classList.toggle('active', b.dataset.nav === name));
}

function setTopbar(title, { back = false, actions = '' } = {}) {
  $('#tb-title').textContent = title;
  const backBtn = $('#tb-back');
  backBtn.style.display = back ? '' : 'none';
  backBtn.onclick = () => history.length > 1 ? history.back() : navigate('home');
  const host = $('#tb-actions'); host.innerHTML = actions;
  return host;
}

async function render() {
  const route = currentRoute();

  // Full-screen routes (no shell)
  if (route.name === 'onboarding') { $('#app-root').dataset.shell = ''; return Screens.onboarding(); }

  renderShell(route.name);
  const isTab = TABS.some(t => t.id === route.name);
  setActiveNav(route.name);

  const host = $('#screen-host');
  host.innerHTML = skeletonScreen();

  const fn = Screens[route.name] || Screens.home;
  try {
    await fn(host, route.param);
  } catch (e) {
    if (e.status === 401) return;
    host.innerHTML = '<div class="screen"></div>';
    $('.screen', host).appendChild(errorState(e.message, () => render()));
  }
}

/* ============================================================================
   SCREEN: HOME
   ========================================================================== */
Screens.home = async (host) => {
  setTopbar('Home', { actions: `<button class="icon-btn" id="a-profile" aria-label="Profile">${svg('profile')}</button>` });
  const data = await API.get('/api/product/home');
  State.cache.home = data;

  const id = data.identity || {};
  const transits = (data.right_now && data.right_now.transits) || [];

  const el = h(`<div class="screen">
    <section class="greeting-hero">
      <div class="g-date">${esc(data.date_label)}</div>
      <div class="g-hi">${esc(data.greeting)}${data.name ? ',&nbsp;' + esc(data.name) : ''}.</div>
      <div class="identity-line">
        <div class="id-chip"><span class="k">Rising</span><span class="v">${esc(id.ascendant?.glyph || '')} ${esc(id.ascendant?.sign || '—')}</span></div>
        <div class="id-chip"><span class="k">Moon</span><span class="v">${esc(id.moon?.glyph || '')} ${esc(id.moon?.sign || '—')}</span></div>
        <div class="id-chip"><span class="k">Nakshatra</span><span class="v">${esc(id.nakshatra || '—')}</span></div>
      </div>
    </section>

    <div class="home-2col">
      <section class="card-hero card-tap full" id="c-today">
        <div class="section-label" style="margin-top:0;">Today</div>
        <p class="today-plain">${esc(data.today?.plain || 'Your day is calm and open.')}</p>
        <div class="chips" style="margin-top:16px;">
          ${data.today?.nakshatra ? `<span class="chip">${svg('moon', 'ic') } ${esc(data.today.moon_sign_today)}</span>` : ''}
          ${data.today?.nakshatra ? `<span class="chip">${esc(data.today.nakshatra)}</span>` : ''}
          ${data.today?.tithi ? `<span class="chip">${esc(data.today.tithi)}</span>` : ''}
        </div>
      </section>

      <section class="card full">
        <div class="row-between"><div class="section-label" style="margin:0;">Right now</div>
          <span class="badge tone-neutral">${esc(data.right_now?.period || '')}</span></div>
        <p class="text-2" style="margin-top:10px;line-height:1.5;">${esc(data.right_now?.plain || '')}</p>
        <div style="margin-top:8px;">
          ${transits.map(t => `
            <div class="transit-row">
              <div class="tg">${esc(t.glyph)}</div>
              <div class="grow"><div class="tt">${esc(t.plain)}</div></div>
              ${t.retrograde ? '<span class="retro">Rx</span>' : ''}
            </div>`).join('') || '<p class="muted" style="padding:8px 0;">No major transits flagged today.</p>'}
        </div>
      </section>
    </div>

    <div class="section-label">Explore</div>
    <div class="list">
      <button class="list-row" data-nav="chart"><div class="tg" style="width:34px;height:34px;border-radius:50%;background:var(--accent-soft);color:var(--accent);display:flex;align-items:center;justify-content:center;">${svg('chart', 'ic')}</div>
        <div class="grow"><div class="lr-title">Your chart</div><div class="lr-sub">Planets, houses & patterns</div></div>${svg('chevron', 'chev')}</button>
      <button class="list-row" data-nav="forecast"><div class="tg" style="width:34px;height:34px;border-radius:50%;background:var(--accent-soft);color:var(--accent);display:flex;align-items:center;justify-content:center;">${svg('forecast', 'ic')}</div>
        <div class="grow"><div class="lr-title">Your timing</div><div class="lr-sub">Career, love, wealth & health</div></div>${svg('chevron', 'chev')}</button>
      <button class="list-row" data-nav="relationships"><div class="tg" style="width:34px;height:34px;border-radius:50%;background:var(--accent-soft);color:var(--accent);display:flex;align-items:center;justify-content:center;">${svg('people', 'ic')}</div>
        <div class="grow"><div class="lr-title">Your people</div><div class="lr-sub">Compare charts & compatibility</div></div>${svg('chevron', 'chev')}</button>
    </div>
    <div style="height:24px;"></div>
  </div>`);

  host.innerHTML = ''; host.appendChild(el);
  el.querySelectorAll('[data-nav]').forEach(b => b.onclick = () => navigate(b.dataset.nav));
  $('#a-profile').onclick = () => navigate('profile');
  $('#c-today').onclick = () => openSheet('Today', `
    <p class="today-plain">${esc(data.today?.plain || '')}</p>
    <div class="list" style="margin-top:16px;">
      ${row('Tithi', data.today?.tithi)}${row('Weekday', data.today?.vara)}
      ${row('Nakshatra', data.today?.nakshatra)}${row('Yoga', data.today?.yoga)}
    </div>`);
};

const row = (k, v) => v ? `<div class="list-row" style="cursor:default;"><div class="grow"><div class="lr-sub">${esc(k)}</div><div class="lr-title">${esc(v)}</div></div></div>` : '';

/* ============================================================================
   SCREEN: CHART
   ========================================================================== */
Screens.chart = async (host) => {
  setTopbar('My Chart', { back: false });
  const data = await API.get('/api/product/chart');
  State.cache.chart = data;
  const id = data.identity || {};

  const el = h(`<div class="screen">
    <div class="segmented" id="chart-tabs" role="tablist">
      <button class="on" data-tab="overview">Overview</button>
      <button data-tab="planets">Planets</button>
      <button data-tab="houses">Houses</button>
      <button data-tab="patterns">Patterns</button>
    </div>
    <div id="chart-body" style="margin-top:20px;"></div>
  </div>`);
  host.innerHTML = ''; host.appendChild(el);

  const body = $('#chart-body', el);
  const tabs = el.querySelectorAll('#chart-tabs button');
  const paint = (tab) => {
    tabs.forEach(b => b.classList.toggle('on', b.dataset.tab === tab));
    if (tab === 'overview') body.innerHTML = chartOverview(data, id);
    else if (tab === 'planets') { body.innerHTML = chartPlanets(data); wirePlanetCells(body); }
    else if (tab === 'houses') body.innerHTML = chartHouses(data);
    else body.innerHTML = chartPatterns(data);
  };
  tabs.forEach(b => b.onclick = () => paint(b.dataset.tab));
  paint('overview');
  wirePlanetCells(body); // overview wheel taps
};

function chartOverview(data, id) {
  return `
    <div class="card-hero">
      <div class="chart-wrap">${chartWheelSVG(data.houses)}</div>
      <p class="center text-2" style="margin-top:8px;">${esc(id.summary || '')}</p>
    </div>
    <div class="section-label">Your signatures</div>
    <div class="planet-grid">
      ${signatureCell('Rising sign', id.ascendant?.sign, id.ascendant?.glyph, 'How you meet the world')}
      ${signatureCell('Moon sign', id.moon?.sign, id.moon?.glyph, 'Your inner emotional world')}
      ${signatureCell('Sun sign', id.sun?.sign, id.sun?.glyph, 'Your core vitality')}
      ${signatureCell('Nakshatra', id.nakshatra, '✦', 'Your birth star')}
    </div>
    <div class="section-label">Current life period</div>
    <div class="card">
      <div class="row-between"><h3>${esc(data.dasha?.label || '')}</h3><span class="badge tone-neutral">${esc(data.dasha?.years || '')}</span></div>
      <p class="text-2" style="margin-top:8px;line-height:1.5;">${esc(data.dasha?.plain || '')}</p>
    </div>
    <div style="height:24px;"></div>`;
}
const signatureCell = (k, sign, glyph, sub) => `
  <div class="planet-cell" style="cursor:default;">
    <div class="glyph">${esc(glyph || '✦')}</div>
    <div class="grow"><div class="pc-sub">${esc(k)}</div><div class="pc-name">${esc(sign || '—')}</div><div class="pc-sub">${esc(sub)}</div></div>
  </div>`;

function chartPlanets(data) {
  return `<div class="planet-grid">
    ${(data.planets || []).map(p => `
      <button class="planet-cell" data-planet="${esc(p.planet)}">
        <div class="glyph">${esc(p.glyph)}</div>
        <div class="grow">
          <div class="pc-name">${esc(p.planet)} ${p.retrograde ? '<span class="retro">Rx</span>' : ''}</div>
          <div class="pc-sub">${esc(p.sign)} · House ${esc(p.house)}</div>
        </div>
      </button>`).join('')}
  </div><div style="height:24px;"></div>`;
}
function wirePlanetCells(root) {
  root.querySelectorAll('[data-planet]').forEach(b => b.onclick = () => openPlanetSheet(b.dataset.planet));
}
async function openPlanetSheet(name) {
  openSheet(name, `<div class="loading-full"><div class="spinner"></div></div>`);
  try {
    const p = await API.get('/api/product/planet/' + encodeURIComponent(name));
    const sheet = $('#sheet');
    sheet.querySelector('.loading-full').outerHTML = `
      <div class="row" style="margin-bottom:12px;">
        <div class="glyph" style="width:48px;height:48px;border-radius:50%;background:var(--accent-soft);color:var(--accent);display:flex;align-items:center;justify-content:center;font-size:24px;">${esc(p.glyph)}</div>
        <div><div style="font-weight:650;font-size:1.15rem;">${esc(p.planet)} in ${esc(p.sign)}</div>
        <div class="muted">House ${esc(p.house)} · ${esc(p.house_name)}${p.nakshatra ? ' · ' + esc(p.nakshatra) : ''}</div></div>
      </div>
      <span class="badge ${toneClass(p.tone)}">${esc(p.dignity)}</span>
      ${p.retrograde ? '<span class="badge tone-mixed" style="margin-left:6px;">Retrograde</span>' : ''}
      <p style="margin-top:14px;line-height:1.55;">${esc(p.plain)}</p>
      <p class="muted" style="margin-top:8px;">${esc(cap(p.theme))}.</p>
      <details class="disclose" style="margin-top:16px;">
        <summary>${svg('chevron', 'caret')} Astrological detail</summary>
        <div class="disclose-body">
          <div class="list">
            ${row('Sign', p.sign + ' ' + (p.degree || ''))}
            ${row('House', p.house + ' — ' + p.house_name)}
            ${row('Nakshatra', p.nakshatra + (p.nakshatra_pada ? ' (pada ' + p.nakshatra_pada + ')' : ''))}
            ${p.owns_houses && p.owns_houses.length ? row('Rules houses', p.owns_houses.join(', ')) : ''}
            ${p.dispositor ? row('Dispositor', p.dispositor) : ''}
            ${p.conjunct_with && p.conjunct_with.length ? row('Conjunct', p.conjunct_with.join(', ')) : ''}
            ${p.aspected_by && p.aspected_by.length ? row('Aspected by', p.aspected_by.join(', ')) : ''}
          </div>
        </div>
      </details>`;
  } catch (e) {
    $('#sheet .loading-full').outerHTML = `<p class="muted">Couldn’t load ${esc(name)}.</p>`;
  }
}

function chartHouses(data) {
  return `<div class="list">
    ${(data.houses || []).map(hs => `
      <div class="list-row" style="cursor:default;">
        <div class="tg" style="width:36px;height:36px;border-radius:9px;background:var(--card-2);display:flex;align-items:center;justify-content:center;font-weight:700;color:var(--muted);" class="num">${esc(hs.house)}</div>
        <div class="grow">
          <div class="lr-title">${esc(hs.name)} <span class="muted" style="font-weight:400;">· ${esc(hs.sign_glyph)} ${esc(hs.sign)}</span></div>
          <div class="lr-sub">${esc(hs.theme)}</div>
        </div>
        <div class="row" style="gap:4px;">${(hs.occupants || []).map(o => `<span title="${esc(o.planet)}" style="font-size:16px;">${esc(o.glyph)}</span>`).join('')}</div>
      </div>`).join('')}
  </div><div style="height:24px;"></div>`;
}

function chartPatterns(data) {
  const y = data.yogas || [];
  if (!y.length) return `<div class="state">${svg('spark', 'state-ic')}<h3>No standout patterns</h3><p>Your chart is balanced without dominant classical yogas.</p></div>`;
  return `<div class="stack">
    ${y.map(yo => `
      <div class="card">
        <div class="row-between"><h3>${esc(yo.name)}</h3>${badge(yo.confidence, yo.tone)}</div>
        ${yo.domain ? `<div class="muted" style="font-size:var(--t-cap);margin-top:4px;">${esc(yo.domain)}</div>` : ''}
        <p class="text-2" style="margin-top:10px;line-height:1.5;">${esc(yo.reason)}</p>
      </div>`).join('')}
  </div><div style="height:24px;"></div>`;
}

/* Chart wheel — North-Indian style diamond (whole-sign houses). */
function chartWheelSVG(houses) {
  const S = 300, m = 4, c = S / 2;
  // Diamond + inner squares layout: house center positions (North Indian fixed layout).
  const pos = {
    1: [c, S * 0.25], 2: [S * 0.25, S * 0.12], 3: [S * 0.12, S * 0.25], 4: [S * 0.25, c],
    5: [S * 0.12, S * 0.75], 6: [S * 0.25, S * 0.88], 7: [c, S * 0.75], 8: [S * 0.75, S * 0.88],
    9: [S * 0.88, S * 0.75], 10: [S * 0.75, c], 11: [S * 0.88, S * 0.25], 12: [S * 0.75, S * 0.12],
  };
  let cells = '';
  (houses || []).forEach(hs => {
    const [x, y] = pos[hs.house] || [c, c];
    const occ = (hs.occupants || []).map(o => o.glyph).join(' ');
    cells += `<text class="sign" x="${x}" y="${y - 8}" text-anchor="middle">${esc(hs.sign_glyph)}</text>`;
    cells += `<text class="planet" x="${x}" y="${y + 9}" text-anchor="middle">${esc(occ)}</text>`;
    cells += `<text class="hnum" x="${x}" y="${y + 22}" text-anchor="middle">${hs.house}</text>`;
  });
  return `<svg class="chart-svg" viewBox="0 0 ${S} ${S}" role="img" aria-label="Birth chart">
    <rect class="frame" x="${m}" y="${m}" width="${S - 2 * m}" height="${S - 2 * m}"/>
    <line class="diag" x1="${m}" y1="${m}" x2="${S - m}" y2="${S - m}"/>
    <line class="diag" x1="${S - m}" y1="${m}" x2="${m}" y2="${S - m}"/>
    <line class="diag" x1="${c}" y1="${m}" x2="${m}" y2="${c}"/>
    <line class="diag" x1="${m}" y1="${c}" x2="${c}" y2="${S - m}"/>
    <line class="diag" x1="${c}" y1="${S - m}" x2="${S - m}" y2="${c}"/>
    <line class="diag" x1="${S - m}" y1="${c}" x2="${c}" y2="${m}"/>
    ${cells}
  </svg>`;
}

/* ============================================================================
   SCREEN: FORECAST
   ========================================================================== */
const DOMAIN_ICON = { career: 'forecast', marriage: 'heart', wealth: 'crown', health: 'spark' };
Screens.forecast = async (host, param) => {
  if (param) return forecastDomain(host, param);
  setTopbar('Forecast', { back: false });
  const data = await API.get('/api/product/forecast');
  State.cache.forecast = data;

  const el = h(`<div class="screen">
    <div class="card-hero">
      <div class="section-label" style="margin-top:0;">Your current season</div>
      <h2 style="margin-top:4px;">${esc(data.period?.label || '')}</h2>
      <p class="text-2" style="margin-top:8px;line-height:1.5;">${esc(data.period?.plain || '')}</p>
    </div>
    <div class="section-label">Life areas</div>
    <div class="list">
      ${(data.domains || []).map(d => `
        <button class="list-row" data-domain="${esc(d.domain)}">
          <div class="tg" style="width:38px;height:38px;border-radius:10px;background:var(--accent-soft);color:var(--accent);display:flex;align-items:center;justify-content:center;">${svg(DOMAIN_ICON[d.domain] || 'spark', 'ic')}</div>
          <div class="grow">
            <div class="lr-title">${esc(d.label)}</div>
            <div class="lr-sub">${esc(d.sub)}</div>
          </div>
          <div style="text-align:right;margin-right:8px;">${badge(d.status, d.tone)}${d.next_window ? `<div class="lr-sub" style="margin-top:4px;">Next: ${esc(d.next_window)}</div>` : ''}</div>
          ${svg('chevron', 'chev')}
        </button>`).join('')}
    </div>
    <div style="height:24px;"></div>
  </div>`);
  host.innerHTML = ''; host.appendChild(el);
  el.querySelectorAll('[data-domain]').forEach(b => b.onclick = () => navigate('forecast/' + b.dataset.domain));
};

async function forecastDomain(host, domain) {
  setTopbar('Forecast', { back: true });
  host.innerHTML = skeletonScreen();
  const d = await API.get('/api/product/forecast/' + encodeURIComponent(domain));
  const el = h(`<div class="screen">
    <div class="card-hero">
      <div class="row-between"><div class="section-label" style="margin:0;">${esc(d.label)}</div>${badge(d.status, d.tone)}</div>
      <p class="today-plain" style="margin-top:12px;">${esc(d.level1?.plain || '')}</p>
    </div>

    ${(d.level2?.supports?.length || d.level2?.challenges?.length) ? `
    <div class="section-label">What's shaping this</div>
    <div class="stack">
      ${(d.level2.supports || []).map(s => factorCard(s.text, s.strength, 'strong', 'Support')).join('')}
      ${(d.level2.challenges || []).map(s => factorCard(s.text, s.strength, 'challenged', 'Friction')).join('')}
    </div>` : ''}

    ${(d.windows && d.windows.length) ? `
    <div class="section-label">Timing ahead</div>
    <div class="stack">
      ${d.windows.map(w => `
        <div class="card">
          <div class="row-between"><h3>${esc(w.start)}${w.end && w.end !== w.start ? ' – ' + esc(w.end) : ''}</h3><span class="badge tone-neutral">${esc(w.confidence || '')}</span></div>
          ${w.label ? `<div class="text-2" style="margin-top:6px;font-weight:550;">${esc(w.label)}</div>` : ''}
          ${w.reason ? `<p class="muted" style="margin-top:6px;line-height:1.5;">${esc(w.reason)}</p>` : ''}
          ${w.peak ? `<div class="chip" style="margin-top:10px;">${svg('clock', 'ic')} Peak: ${esc(w.peak)}</div>` : ''}
        </div>`).join('')}
    </div>` : ''}

    <details class="disclose" style="margin-top:20px;">
      <summary>${svg('chevron', 'caret')} Astrological evidence</summary>
      <div class="disclose-body stack">
        ${(d.level3?.supporting_factors || []).map(f => `<div class="card" style="padding:14px;"><span class="badge tone-strong" style="margin-bottom:6px;">${esc(f.strength || 'Support')}</span><p class="text-2" style="line-height:1.5;">${esc(f.reason)}</p></div>`).join('')}
        ${(d.level3?.contradicting_factors || []).map(f => `<div class="card" style="padding:14px;"><span class="badge tone-challenged" style="margin-bottom:6px;">${esc(f.strength || 'Friction')}</span><p class="text-2" style="line-height:1.5;">${esc(f.reason)}</p></div>`).join('')}
        ${d.level4?.final_judgment ? `<div class="card" style="padding:14px;"><div class="lr-sub" style="margin-bottom:6px;">Engine verdict</div><p class="text-2" style="line-height:1.5;white-space:pre-line;">${esc(d.level4.final_judgment)}</p></div>` : ''}
      </div>
    </details>
    <div style="height:24px;"></div>
  </div>`);
  host.innerHTML = ''; host.appendChild(el);
}
const factorCard = (text, strength, tone, kind) => `
  <div class="card" style="padding:16px;">
    <span class="badge ${toneClass(tone)}">${esc(kind)}${strength ? ' · ' + esc(strength) : ''}</span>
    <p class="text-2" style="margin-top:8px;line-height:1.5;">${esc(text)}</p>
  </div>`;

/* ============================================================================
   SCREEN: RELATIONSHIPS
   ========================================================================== */
Screens.relationships = async (host) => {
  setTopbar('Relationships', { actions: `<button class="icon-btn" id="add-rel" aria-label="Add person">${svg('plus')}</button>` });
  const data = await API.get('/api/product/relationships');
  const rels = data.relationships || [];

  const el = h(`<div class="screen">
    ${rels.length ? `<div class="list">
      ${rels.map(r => `
        <button class="list-row" data-rel="${esc(r.id)}">
          <div class="glyph" style="width:44px;height:44px;border-radius:50%;background:var(--accent-soft);color:var(--accent);display:flex;align-items:center;justify-content:center;">${svg('heart', 'ic')}</div>
          <div class="grow"><div class="lr-title">${esc(r.label)}</div><div class="lr-sub">${esc(cap(r.relation))} · ${esc(r.city || '')}</div></div>
          ${svg('chevron', 'chev')}
        </button>`).join('')}
    </div>` : `<div class="state">${svg('people', 'state-ic')}<h3>No one saved yet</h3><p>Add someone to explore how your charts fit together — compatibility, warmth and friction.</p><button class="btn btn-primary" id="empty-add">${svg('plus', 'ic')} Add a person</button></div>`}
    <div style="height:24px;"></div>
  </div>`);
  host.innerHTML = ''; host.appendChild(el);
  const addBtn = $('#add-rel'); if (addBtn) addBtn.onclick = openAddRelationship;
  const emptyAdd = $('#empty-add', el); if (emptyAdd) emptyAdd.onclick = openAddRelationship;
  el.querySelectorAll('[data-rel]').forEach(b => b.onclick = () => openCompatibility(b.dataset.rel));
};

function openAddRelationship() {
  openSheet('Add a person', `
    <form id="rel-form" class="stack">
      <div class="field"><label>Their name</label><input class="input" id="rf-name" required placeholder="Full name"></div>
      <div class="row" style="gap:12px;">
        <div class="field grow"><label>Label</label><input class="input" id="rf-label" placeholder="e.g. Partner" required></div>
        <div class="field grow"><label>Relation</label>
          <select class="select" id="rf-relation">
            <option value="partner">Partner</option><option value="spouse">Spouse</option>
            <option value="parent">Parent</option><option value="child">Child</option>
            <option value="sibling">Sibling</option><option value="friend">Friend</option>
            <option value="colleague">Colleague</option>
          </select>
        </div>
      </div>
      <div class="field"><label>Date of birth</label><input class="input" id="rf-date" type="date" required></div>
      <div class="field"><label>Time of birth</label><input class="input" id="rf-time" type="time" required></div>
      <div class="field"><label>Birth city</label><input class="input" id="rf-city" placeholder="Search a city…" autocomplete="off" required>
        <div id="rf-loc" class="loc-results hide"></div>
        <div class="field-hint" id="rf-loc-hint">We use this only to place their chart accurately.</div>
      </div>
      <div class="field-error hide" id="rf-err"></div>
      <button type="submit" class="btn btn-primary btn-block" id="rf-submit">Save person</button>
    </form>`);
  const form = $('#rel-form');
  const loc = { lat: null, lon: null, tz: null };
  wireCitySearch($('#rf-city'), $('#rf-loc'), $('#rf-loc-hint'), (r) => { loc.lat = r.lat; loc.lon = r.lon; loc.tz = r.tz; });
  form.onsubmit = async (e) => {
    e.preventDefault();
    const err = $('#rf-err');
    if (loc.lat == null) { err.textContent = 'Please pick a city from the list.'; err.classList.remove('hide'); return; }
    const btn = $('#rf-submit'); btn.disabled = true; btn.textContent = 'Saving…';
    try {
      await API.post('/api/product/relationships', {
        label: $('#rf-label').value.trim(), relation: $('#rf-relation').value,
        full_name: $('#rf-name').value.trim(), birth_date: $('#rf-date').value,
        birth_time: $('#rf-time').value, city: $('#rf-city').value.trim(),
        latitude: loc.lat, longitude: loc.lon, timezone: loc.tz
      });
      closeSheet(); toast('Person saved'); render();
    } catch (ex) { err.textContent = ex.message; err.classList.remove('hide'); btn.disabled = false; btn.textContent = 'Save person'; }
  };
}

async function openCompatibility(relId) {
  openSheet('Compatibility', `<div class="loading-full"><div class="spinner"></div><p>Comparing charts…</p></div>`);
  try {
    const c = await API.get('/api/product/relationships/' + relId + '/compatibility');
    const dash = 2 * Math.PI * 54;
    const off = dash * (1 - c.percent / 100);
    $('#sheet .loading-full').outerHTML = `
      <div class="score-ring">
        <svg width="132" height="132" viewBox="0 0 132 132"><circle class="track" cx="66" cy="66" r="54"/><circle class="fill" cx="66" cy="66" r="54" stroke-dasharray="${dash}" stroke-dashoffset="${dash}" id="ring-fill"/></svg>
        <div class="lbl"><span class="pct num">${c.percent}%</span><span class="of num">${c.score}/${c.total}</span></div>
      </div>
      <div class="center" style="margin-top:8px;"><span class="badge ${c.percent >= 69 ? 'tone-strong' : c.percent >= 50 ? 'tone-mixed' : 'tone-tender'}">${esc(c.band)}</span></div>
      <p class="center text-2" style="margin-top:12px;line-height:1.5;">${esc(c.plain)}</p>
      <div class="section-label">The eight harmonies</div>
      <div class="list">
        ${(c.breakdown || []).map(b => `<div class="list-row" style="cursor:default;"><div class="grow"><div class="lr-title">${esc(b.koota)}</div><div class="lr-sub">${esc(b.note)}</div></div><span class="dot ${toneClass(b.tone)}" style="color:${b.tone === 'strong' ? 'var(--good)' : 'var(--bad)'};"></span></div>`).join('')}
      </div>
      <button class="btn btn-danger btn-block" id="rel-del" style="margin-top:20px;">${svg('trash', 'ic')} Remove ${esc(c.person)}</button>`;
    requestAnimationFrame(() => { const f = $('#ring-fill'); if (f) f.style.strokeDashoffset = off; });
    $('#rel-del').onclick = async () => {
      try { await API.del('/api/product/relationships/' + relId); closeSheet(); toast('Removed'); render(); }
      catch (e) { toast('Could not remove'); }
    };
  } catch (e) {
    $('#sheet .loading-full').outerHTML = `<p class="muted center">${esc(e.message)}</p>`;
  }
}

/* ============================================================================
   SCREEN: CALENDAR / SKY
   ========================================================================== */
Screens.calendar = async (host) => {
  setTopbar('Calendar', { back: false });
  const data = await API.get('/api/product/calendar');
  const t = data.today || {};
  const el = h(`<div class="screen">
    <div class="card-hero">
      <div class="section-label" style="margin-top:0;">${esc(t.date_label || 'Today')}</div>
      <p class="today-plain" style="margin-top:6px;">${esc(t.plain || '')}</p>
      <div class="chips" style="margin-top:14px;">
        ${t.moon_sign_today ? `<span class="chip">${svg('moon', 'ic')} Moon in ${esc(t.moon_sign_today)}</span>` : ''}
        ${t.nakshatra ? `<span class="chip">${esc(t.nakshatra)}</span>` : ''}
        ${t.tithi ? `<span class="chip">${esc(t.tithi)}</span>` : ''}
        ${t.yoga ? `<span class="chip">${esc(t.yoga)}</span>` : ''}
      </div>
    </div>

    <div class="section-label">Sky right now</div>
    <div class="card">
      ${(data.transits || []).map(tr => `
        <div class="transit-row"><div class="tg">${esc(tr.glyph)}</div>
          <div class="grow"><div class="tt">${esc(tr.plain)}</div></div>${tr.retrograde ? '<span class="retro">Rx</span>' : ''}</div>`).join('') || '<p class="muted">No major movements today.</p>'}
    </div>

    ${(data.auspicious && data.auspicious.length) ? `<div class="section-label">Favourable windows today</div>
      <div class="list">${data.auspicious.map(w => `<div class="list-row" style="cursor:default;"><div class="grow"><div class="lr-title">${esc(w.name)}</div>${w.start ? `<div class="lr-sub num">${esc(w.start)}${w.end ? ' – ' + esc(w.end) : ''}</div>` : ''}</div><span class="dot" style="color:var(--good);"></span></div>`).join('')}</div>` : ''}
    ${(data.inauspicious && data.inauspicious.length) ? `<div class="section-label">Take it easy</div>
      <div class="list">${data.inauspicious.map(w => `<div class="list-row" style="cursor:default;"><div class="grow"><div class="lr-title">${esc(w.name)}</div>${w.start ? `<div class="lr-sub num">${esc(w.start)}${w.end ? ' – ' + esc(w.end) : ''}</div>` : ''}</div><span class="dot" style="color:var(--warn);"></span></div>`).join('')}</div>` : ''}
    <div style="height:24px;"></div>
  </div>`);
  host.innerHTML = ''; host.appendChild(el);
};

/* ============================================================================
   SCREEN: PROFILE / SETTINGS
   ========================================================================== */
Screens.profile = async (host) => {
  setTopbar('Profile', { back: false });
  const [summary, prefs] = await Promise.all([API.get('/api/product/summary'), API.get('/api/product/preferences')]);
  State.summary = summary; State.user = summary.user;
  const u = summary.user, p = summary.profile || {};
  const appearance = prefs.appearance || 'system';

  const el = h(`<div class="screen">
    <div class="card-hero center">
      <div class="glyph" style="width:72px;height:72px;border-radius:50%;background:var(--accent-soft);color:var(--accent);display:flex;align-items:center;justify-content:center;font-size:30px;margin:0 auto 12px;">${esc((u.full_name || 'A')[0].toUpperCase())}</div>
      <h2>${esc(u.full_name)}</h2>
      <p class="muted">${esc(u.email)}</p>
      <span class="badge ${u.plan === 'premium' ? 'tone-strong' : 'tone-neutral'}" style="margin-top:10px;">${u.plan === 'premium' ? svg('crown', 'ic') + ' Premium' : 'Free plan'}</span>
    </div>

    <div class="section-label">Birth details</div>
    <div class="list">
      ${row('Name', p.full_name)}${row('Date of birth', p.birth_date)}
      ${row('Time of birth', p.birth_time)}${row('Birth place', p.city)}
      ${row('Timezone', p.timezone)}
    </div>
    <button class="btn btn-secondary btn-block" id="edit-birth" style="margin-top:12px;">Edit birth details</button>

    <div class="section-label">Appearance</div>
    <div class="segmented" id="appearance-seg">
      <button data-appear="system" class="${appearance === 'system' ? 'on' : ''}">System</button>
      <button data-appear="light" class="${appearance === 'light' ? 'on' : ''}">${svg('sun', 'ic')} Light</button>
      <button data-appear="dark" class="${appearance === 'dark' ? 'on' : ''}">${svg('moon', 'ic')} Dark</button>
    </div>

    <div class="section-label">Notifications</div>
    <div class="list" id="notif-list">
      ${toggleRow('daily_insight', 'Daily astrology', 'A short read each morning', prefs.daily_insight)}
      ${toggleRow('transit_alert', 'Important transits', 'When major planets shift', prefs.transit_alert)}
      ${toggleRow('timing_period', 'Timing windows', 'When a key period opens', prefs.timing_period)}
      ${toggleRow('relationship_event', 'Relationship events', 'Notable dates for saved people', prefs.relationship_event)}
      ${toggleRow('product_updates', 'Product updates', 'New features & tips', prefs.product_updates)}
    </div>

    <div class="section-label">Subscription</div>
    <div class="card">
      ${u.plan === 'premium'
        ? `<div class="row-between"><div><h3>Premium</h3><p class="muted">Unlimited readings & deep timing.</p></div>${svg('crown', 'ic')}</div>`
        : `<div class="row-between"><div><h3>Go Premium</h3><p class="muted">Unlock unlimited readings & deep timing.</p></div></div><button class="btn btn-primary btn-block" id="go-premium" style="margin-top:14px;">Upgrade</button>`}
    </div>

    <div class="section-label">More</div>
    <div class="list">
      <button class="list-row" id="install-app"><div class="grow"><div class="lr-title">Install app</div><div class="lr-sub">Add to your Home Screen</div></div>${svg('chevron', 'chev')}</button>
      <button class="list-row" id="open-chat"><div class="grow"><div class="lr-title">Classic chat</div><div class="lr-sub">Ask the astrologer directly</div></div>${svg('chevron', 'chev')}</button>
      <button class="list-row" id="about"><div class="grow"><div class="lr-title">About & privacy</div><div class="lr-sub">Your birth data stays private</div></div>${svg('chevron', 'chev')}</button>
    </div>

    <button class="btn btn-danger btn-block" id="logout" style="margin-top:20px;">${svg('logout', 'ic')} Sign out</button>
    <div style="height:24px;"></div>
  </div>`);
  host.innerHTML = ''; host.appendChild(el);

  // Appearance
  el.querySelectorAll('[data-appear]').forEach(b => b.onclick = async () => {
    el.querySelectorAll('[data-appear]').forEach(x => x.classList.remove('on'));
    b.classList.add('on'); applyAppearance(b.dataset.appear);
    try { await API.post('/api/product/preferences', { ...prefsPayload(el), appearance: b.dataset.appear }); } catch {}
  });
  // Notification toggles
  el.querySelectorAll('.toggle').forEach(t => t.onclick = async () => {
    t.classList.toggle('on');
    try { await API.post('/api/product/preferences', { ...prefsPayload(el), appearance }); toast('Saved'); }
    catch { t.classList.toggle('on'); toast('Could not save'); }
  });

  $('#edit-birth', el).onclick = () => editBirthDetails(p);
  $('#logout', el).onclick = async () => { try { await API.post('/api/auth/logout'); } catch {} localStorage.removeItem('astro_user'); window.location.href = '/login'; };
  $('#open-chat', el).onclick = () => window.location.href = '/chat';
  const gp = $('#go-premium', el); if (gp) gp.onclick = startCheckout;
  $('#install-app', el).onclick = showInstall;
  $('#about', el).onclick = () => openSheet('About & privacy', `
    <p style="line-height:1.6;">Astrology AI turns a deep, deterministic Vedic engine into a calm, simple experience.</p>
    <p style="line-height:1.6;margin-top:12px;"><b>Your privacy.</b> Your birth details are private to your account. They are never shown publicly and never shared. Only you can see your chart and the people you save.</p>
    <p class="muted" style="margin-top:12px;">Ancient wisdom, modern precision.</p>`);
};

const toggleRow = (key, title, sub, on) => `
  <div class="list-row" style="cursor:default;">
    <div class="grow"><div class="lr-title">${esc(title)}</div><div class="lr-sub">${esc(sub)}</div></div>
    <button class="toggle ${on ? 'on' : ''}" data-key="${key}" role="switch" aria-checked="${!!on}" aria-label="${esc(title)}"></button>
  </div>`;
function prefsPayload(root) {
  const p = {};
  root.querySelectorAll('.toggle').forEach(t => p[t.dataset.key] = t.classList.contains('on'));
  return p;
}

function editBirthDetails(p) {
  openSheet('Edit birth details', birthFormHtml(p));
  const loc = { lat: null, lon: null, tz: p.timezone || null };
  wireCitySearch($('#bf-city'), $('#bf-loc'), $('#bf-loc-hint'), (r) => { loc.lat = r.lat; loc.lon = r.lon; loc.tz = r.tz; });
  $('#bf-form').onsubmit = async (e) => {
    e.preventDefault();
    const err = $('#bf-err');
    if (loc.lat == null) { err.textContent = 'Please pick your city from the list to recalculate the chart.'; err.classList.remove('hide'); return; }
    const btn = $('#bf-submit'); btn.disabled = true; btn.textContent = 'Saving…';
    try {
      await API.post('/api/profile', {
        full_name: $('#bf-name').value.trim(), date: $('#bf-date').value, time: $('#bf-time').value,
        city: $('#bf-city').value.trim(), lat: loc.lat, lon: loc.lon, timezone: loc.tz
      });
      State.cache = {}; closeSheet(); toast('Chart updated'); navigate('home');
    } catch (ex) { err.textContent = ex.message; err.classList.remove('hide'); btn.disabled = false; btn.textContent = 'Save'; }
  };
}
const birthFormHtml = (p = {}) => `
  <form id="bf-form" class="stack">
    <div class="field"><label>Your name</label><input class="input" id="bf-name" value="${esc(p.full_name || '')}" required></div>
    <div class="field"><label>Date of birth</label><input class="input" id="bf-date" type="date" value="${esc(p.birth_date || '')}" required></div>
    <div class="field"><label>Exact time of birth</label><input class="input" id="bf-time" type="time" value="${esc(p.birth_time || '')}" required>
      <div class="field-hint">Accurate to the minute gives the truest chart.</div></div>
    <div class="field"><label>Birth city</label><input class="input" id="bf-city" value="${esc(p.city || '')}" placeholder="Search a city…" autocomplete="off" required>
      <div id="bf-loc" class="loc-results hide"></div>
      <div class="field-hint" id="bf-loc-hint">${p.timezone ? 'Currently: ' + esc(p.timezone) : 'Pick your city to set timezone.'}</div></div>
    <div class="field-error hide" id="bf-err"></div>
    <button type="submit" class="btn btn-primary btn-block" id="bf-submit">Save</button>
  </form>`;

async function startCheckout() {
  try { const r = await API.post('/api/create-checkout-session'); if (r.checkout_url) window.location.href = r.checkout_url; }
  catch (e) { toast(e.status === 503 ? 'Payments not enabled here' : 'Could not start checkout'); }
}

/* ============================================================================
   ONBOARDING
   ========================================================================== */
Screens.onboarding = () => {
  const root = $('#app-root'); root.dataset.shell = '';
  const steps = ['welcome', 'name', 'birth', 'place', 'confirm'];
  let i = 0;
  const answers = { full_name: (State.user && State.user.full_name) || '', date: '', time: '', city: '', lat: null, lon: null, tz: null };

  const mount = () => {
    root.innerHTML = `<div class="auth-wrap"><div class="auth-card">
      <div class="ob-progress">${steps.map((_, k) => `<div class="seg ${k <= i ? 'done' : ''}"></div>`).join('')}</div>
      <div id="ob-step"></div>
    </div></div>`;
    paint();
  };
  const paint = () => {
    const box = $('#ob-step');
    const step = steps[i];
    if (step === 'welcome') {
      box.innerHTML = `<div class="center stack">
        <img src="/static/icons/icon-192.png" width="64" height="64" style="border-radius:16px;margin:8px auto;">
        <h1>Welcome${answers.full_name ? ', ' + esc(answers.full_name.split(' ')[0]) : ''}.</h1>
        <p class="muted">Let’s build your birth chart. It takes about a minute — just your birth date, exact time, and city.</p>
        <button class="btn btn-primary btn-block" id="ob-next">Begin</button>
      </div>`;
      $('#ob-next').onclick = () => { i++; paint(); repaintProgress(); };
    } else if (step === 'name') {
      box.innerHTML = `<div class="stack">
        <h1>What’s your name?</h1>
        <p class="muted">This personalises your readings.</p>
        <div class="field"><input class="input" id="ob-name" value="${esc(answers.full_name)}" placeholder="Your full name" autofocus></div>
        ${obNav()}</div>`;
      $('#ob-back').onclick = () => { i--; paint(); repaintProgress(); };
      $('#ob-cont').onclick = () => { answers.full_name = $('#ob-name').value.trim(); if (!answers.full_name) return toast('Please enter your name'); i++; paint(); repaintProgress(); };
    } else if (step === 'birth') {
      box.innerHTML = `<div class="stack">
        <h1>When were you born?</h1>
        <p class="muted">Exact time matters — it sets your rising sign and houses.</p>
        <div class="field"><label>Date of birth</label><input class="input" id="ob-date" type="date" value="${esc(answers.date)}" required></div>
        <div class="field"><label>Exact time of birth</label><input class="input" id="ob-time" type="time" value="${esc(answers.time)}" required>
          <div class="field-hint">If unsure, ask family or check a birth certificate.</div></div>
        ${obNav()}</div>`;
      $('#ob-back').onclick = () => { i--; paint(); repaintProgress(); };
      $('#ob-cont').onclick = () => {
        answers.date = $('#ob-date').value; answers.time = $('#ob-time').value;
        if (!answers.date || !answers.time) return toast('Please enter date and time');
        i++; paint(); repaintProgress();
      };
    } else if (step === 'place') {
      box.innerHTML = `<div class="stack">
        <h1>Where were you born?</h1>
        <p class="muted">We use your city to place the planets precisely.</p>
        <div class="field"><input class="input" id="ob-city" value="${esc(answers.city)}" placeholder="Search your birth city…" autocomplete="off" autofocus>
          <div id="ob-loc" class="loc-results hide"></div>
          <div class="field-hint" id="ob-loc-hint">Pick from the list so the timezone is exact.</div></div>
        ${obNav('Continue', answers.lat != null)}</div>`;
      wireCitySearch($('#ob-city'), $('#ob-loc'), $('#ob-loc-hint'), (r) => {
        answers.city = r.display; answers.lat = r.lat; answers.lon = r.lon; answers.tz = r.tz;
        $('#ob-cont').disabled = false;
      });
      $('#ob-back').onclick = () => { i--; paint(); repaintProgress(); };
      $('#ob-cont').onclick = () => { if (answers.lat == null) return toast('Pick your city from the list'); i++; paint(); repaintProgress(); };
    } else if (step === 'confirm') {
      box.innerHTML = `<div class="stack">
        <h1>Does this look right?</h1>
        <div class="list">
          ${row('Name', answers.full_name)}${row('Born', answers.date + ' at ' + answers.time)}
          ${row('Place', answers.city)}${row('Timezone', answers.tz)}
        </div>
        <div class="field-error hide" id="ob-err"></div>
        <button class="btn btn-primary btn-block" id="ob-generate">Generate my chart</button>
        <button class="btn btn-ghost btn-block" id="ob-back">Go back</button>
      </div>`;
      $('#ob-back').onclick = () => { i--; paint(); repaintProgress(); };
      $('#ob-generate').onclick = generate;
    }
  };
  const repaintProgress = () => { const segs = root.querySelectorAll('.ob-progress .seg'); segs.forEach((s, k) => s.classList.toggle('done', k <= i)); };
  const obNav = (label = 'Continue', enabled = true) => `
    <div class="row" style="gap:12px;margin-top:8px;">
      <button class="btn btn-secondary" id="ob-back" style="flex:0 0 auto;">Back</button>
      <button class="btn btn-primary grow" id="ob-cont" ${enabled ? '' : 'disabled'}>${label}</button>
    </div>`;

  async function generate() {
    const btn = $('#ob-generate'); btn.disabled = true; btn.textContent = 'Calculating your chart…';
    try {
      await API.post('/api/profile', {
        full_name: answers.full_name, date: answers.date, time: answers.time,
        city: answers.city, lat: answers.lat, lon: answers.lon, timezone: answers.tz
      });
      // Warm the chart + show a first summary before entering the app.
      const home = await API.get('/api/product/home');
      const id = home.identity || {};
      root.innerHTML = `<div class="auth-wrap"><div class="auth-card center stack">
        <div class="glyph" style="width:80px;height:80px;border-radius:50%;background:var(--accent-soft);color:var(--accent);display:flex;align-items:center;justify-content:center;font-size:34px;margin:0 auto;">${esc(id.ascendant?.glyph || '✦')}</div>
        <h1>Your chart is ready</h1>
        <p class="text-2" style="line-height:1.55;">${esc(id.summary || '')}</p>
        <div class="identity-line" style="justify-content:center;">
          <div class="id-chip"><span class="k">Rising</span><span class="v">${esc(id.ascendant?.sign || '')}</span></div>
          <div class="id-chip"><span class="k">Moon</span><span class="v">${esc(id.moon?.sign || '')}</span></div>
          <div class="id-chip"><span class="k">Star</span><span class="v">${esc(id.nakshatra || '')}</span></div>
        </div>
        <button class="btn btn-primary btn-block" id="ob-enter">Enter Astrology AI</button>
      </div></div>`;
      $('#ob-enter').onclick = () => { State.summary = null; navigate('home'); boot(); };
    } catch (ex) {
      const err = $('#ob-err'); if (err) { err.textContent = ex.message; err.classList.remove('hide'); }
      btn.disabled = false; btn.textContent = 'Generate my chart';
    }
  }
  mount();
};

/* ---- shared city search ------------------------------------------------- */
function wireCitySearch(input, resultsEl, hintEl, onPick) {
  let timer, lastQ = '';
  input.addEventListener('input', () => {
    const q = input.value.trim();
    clearTimeout(timer);
    if (q.length < 2) { resultsEl.classList.add('hide'); return; }
    timer = setTimeout(async () => {
      if (q === lastQ) return; lastQ = q;
      try {
        const data = await API.get('/api/locations/search?q=' + encodeURIComponent(q));
        const results = (data.results || []).slice(0, 6);
        if (!results.length) { resultsEl.innerHTML = '<div class="loc-item muted">No matches</div>'; resultsEl.classList.remove('hide'); return; }
        resultsEl.innerHTML = results.map((r, k) => `<div class="loc-item" data-k="${k}">${svg('location', 'ic')} ${esc(r.display_name)}</div>`).join('');
        resultsEl.classList.remove('hide');
        resultsEl.querySelectorAll('.loc-item[data-k]').forEach(item => item.onclick = async () => {
          const r = results[+item.dataset.k];
          const display = r.display_name;
          input.value = display.split(',').slice(0, 2).join(',').trim();
          resultsEl.classList.add('hide');
          if (hintEl) hintEl.textContent = 'Finding timezone…';
          try {
            const tz = await API.get(`/api/location/timezone?lat=${r.lat}&lon=${r.lon}`);
            if (hintEl) hintEl.textContent = `${input.value} · ${tz.timezone}`;
            onPick({ display, lat: parseFloat(r.lat), lon: parseFloat(r.lon), tz: tz.timezone });
          } catch { if (hintEl) hintEl.textContent = 'Could not resolve timezone — try another city.'; }
        });
      } catch { resultsEl.innerHTML = '<div class="loc-item muted">Search unavailable</div>'; resultsEl.classList.remove('hide'); }
    }, 320);
  });
}

/* ---- PWA install -------------------------------------------------------- */
let deferredInstall = null;
window.addEventListener('beforeinstallprompt', (e) => { e.preventDefault(); deferredInstall = e; });
function isStandalone() { return matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true; }
function isIOS() { return /iphone|ipad|ipod/i.test(navigator.userAgent); }
function showInstall() {
  if (isStandalone()) return openSheet('Already installed', '<p class="text-2">You’re running the installed app. Enjoy the sky. ✦</p>');
  if (deferredInstall) {
    deferredInstall.prompt();
    deferredInstall.userChoice.finally(() => { deferredInstall = null; closeSheet(); });
    return;
  }
  if (isIOS()) {
    openSheet('Add to Home Screen', `
      <p class="text-2" style="line-height:1.6;">To install on iPhone or iPad:</p>
      <ol class="text-2" style="line-height:1.9;padding-left:20px;margin-top:10px;">
        <li>Tap the <b>Share</b> button ${svg('share', 'ic')} in Safari’s toolbar.</li>
        <li>Scroll and choose <b>Add to Home Screen</b>.</li>
        <li>Tap <b>Add</b> — Astrology AI appears like a native app.</li>
      </ol>
      <p class="muted" style="margin-top:12px;">iOS installs differently from Android — this is Apple’s built-in flow.</p>`);
  } else {
    openSheet('Install app', `<p class="text-2" style="line-height:1.6;">Open your browser menu and choose <b>Install app</b> or <b>Add to Home screen</b>. If you don’t see it yet, keep using the app for a moment and try again.</p>`);
  }
}
function registerSW() {
  if ('serviceWorker' in navigator) navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(() => {});
}

/* ---- misc --------------------------------------------------------------- */
const cap = (s) => (s ? s.charAt(0).toUpperCase() + s.slice(1) : '');

/* ---- go ----------------------------------------------------------------- */
boot();
