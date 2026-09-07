/* Astrology AI — Service Worker
   Strategy:
     * App shell (HTML, CSS, JS, icons): stale-while-revalidate for instant loads.
     * API calls (/api/*): NEVER cached — always network (private, live astrology).
     * Offline fallback: the cached shell renders an offline notice screen.
   Bump CACHE_VERSION to invalidate old caches on deploy. */
const CACHE_VERSION = 'astro-v3';
const SHELL_CACHE = `${CACHE_VERSION}-shell`;

const SHELL_ASSETS = [
  '/app',
  '/static/product.css',
  '/static/product.js',
  '/static/icons/icon-192.png',
  '/static/icons/icon-512.png',
  '/static/icons/apple-touch-icon.png',
  '/manifest.webmanifest',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE)
      .then((cache) => cache.addAll(SHELL_ASSETS).catch(() => {}))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => !k.startsWith(CACHE_VERSION)).map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  // Never cache API / auth / streaming — always live network.
  if (url.pathname.startsWith('/api/') || url.pathname.startsWith('/sw.js')) {
    return; // default browser behaviour (network)
  }

  // Navigations (app shell): network-first, fall back to cached shell offline.
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request)
        .then((res) => {
          const copy = res.clone();
          caches.open(SHELL_CACHE).then((c) => c.put('/app', copy)).catch(() => {});
          return res;
        })
        .catch(() => caches.match('/app').then((r) => r || offlineResponse()))
    );
    return;
  }

  // Static assets: stale-while-revalidate.
  if (url.pathname.startsWith('/static/') || url.pathname === '/manifest.webmanifest') {
    event.respondWith(
      caches.open(SHELL_CACHE).then((cache) =>
        cache.match(request).then((cached) => {
          const network = fetch(request)
            .then((res) => { cache.put(request, res.clone()).catch(() => {}); return res; })
            .catch(() => cached);
          return cached || network;
        })
      )
    );
  }
});

function offlineResponse() {
  return new Response(
    '<!doctype html><meta charset="utf-8"><title>Offline</title>' +
    '<body style="font-family:-apple-system,system-ui,sans-serif;background:#000;color:#fff;' +
    'display:flex;height:100vh;margin:0;align-items:center;justify-content:center;text-align:center">' +
    '<div><h2>You\u2019re offline</h2><p style="color:#8e8e93">Reconnect to see your live chart and timing.</p></div>',
    { headers: { 'Content-Type': 'text/html' } }
  );
}
