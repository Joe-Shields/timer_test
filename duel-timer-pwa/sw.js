/* Time Debt Clock — service worker
 * Strategy:
 *  - Navigations: network-first (so updates land), fall back to cached shell when offline.
 *  - Same-origin assets: cache-first with runtime caching.
 *  - Old caches are removed on activate. Bump VERSION after any app change.
 */
const VERSION = "tdc-v1";
const STATIC_CACHE = `${VERSION}-static`;
const RUNTIME_CACHE = `${VERSION}-runtime`;

const APP_SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./icons/favicon.svg",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-192.png",
  "./icons/icon-maskable-512.png",
  "./icons/apple-touch-icon-180.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(keys.filter(k => !k.startsWith(VERSION)).map(k => caches.delete(k)));
      await self.clients.claim();
    })()
  );
});

self.addEventListener("fetch", event => {
  const req = event.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  // Navigations: network-first, offline fallback to the cached app shell.
  if (req.mode === "navigate") {
    event.respondWith(
      (async () => {
        try {
          const fresh = await fetch(req);
          if (fresh && fresh.ok) {
            const cache = await caches.open(RUNTIME_CACHE);
            cache.put(req, fresh.clone());
            return fresh;
          }
        } catch (err) {
          // offline — fall through to cache
        }
        const cached = (await caches.match(req)) || (await caches.match("./index.html"));
        return cached || Response.error();
      })()
    );
    return;
  }

  // Assets: cache-first, then network with runtime caching.
  event.respondWith(
    (async () => {
      const hit = await caches.match(req);
      if (hit) return hit;
      try {
        const res = await fetch(req);
        if (res && res.ok && url.protocol === "http:") {
          const cache = await caches.open(RUNTIME_CACHE);
          cache.put(req, res.clone());
        }
        return res;
      } catch (err) {
        return Response.error();
      }
    })()
  );
});
