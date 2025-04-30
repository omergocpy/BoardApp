const CACHE_NAME = 'board-app-v1';
const urlsToCache = [
  '/',
  '/static/css/styles.css',
  '/static/js/main.js',
  '/static/images/icon-192x192.png',
  '/static/images/icon-512x512.png'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});