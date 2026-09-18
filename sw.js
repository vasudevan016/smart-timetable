const CACHE_NAME = 'iiits-timetable-v1';
const ASSETS_TO_CACHE = [
  './',
  './index.html',
  './students.json',
  './timetable.json'
];

// Install Event: Cache all critical files
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS_TO_CACHE))
      .then(() => self.skipWaiting())
  );
});

// Fetch Event: Network-first, fallback to cache if offline
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Update the cache with the freshest data
        const resClone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, resClone));
        return response;
      })
      .catch(() => caches.match(event.request)) // If offline, serve from cache
  );
});