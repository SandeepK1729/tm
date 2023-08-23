
// pwa app shell
const CACHE_NAME = 'transaction-manager-v1';

const urlsToCache = [
    '/',
    
    '/static/logo/favicon.ico',
    '/static/logo/favicon-16x16.png',
    '/static/logo/favicon-32x32.png',
    '/static/logo/android-chrome-192x192.png',
    '/static/logo/android-chrome-512x512.png',
    '/static/logo/apple-touch-icon.png',
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => cache.addAll(urlsToCache))
    );
}
);

self.addEventListener('fetch', (event) => {
    var requestUrl = new URL(event.request.url);
    if (requestUrl.pathname === location.origin) {
        event.respondWith(caches.match('/'));
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                // if (response) return response;
                return fetch(event.request);
            })
    );
}
);
