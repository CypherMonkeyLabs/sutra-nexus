/* Offline shell adapted from Webex Lab sw.js at commit
   7631b317cbf2cad236403df960b5d5fac353a6de.
   Same-origin GET only. The contact page is never in this list. */
var CACHE = "sutra-nexus-v2-1";
var SHELL = [
  "./",
  "./index.html",
  "./offline.html",
  "./foundations.html",
  "./maheshvara.html",
  "./sandhi.html",
  "./ashtadhyayi.html",
  "./anuvrtti.html",
  "./dhatu.html",
  "./shiva.html",
  "./history.html",
  "./ecosystem.html",
  "./resources.html",
  "./play.html",
  "./listen.html",
  "./diagrams.html",
  "./charts.html",
  "./downloads.html",
  "./glossary.html",
  "./credits.html",
  "./about.html",
  "./assets/css/sutra.css",
  "./assets/js/brand.js",
  "./assets/js/frame.js",
  "./assets/js/phone-nav.js",
  "./assets/js/app.js",
  "./assets/js/guide.js",
  "./assets/data/socials.json",
  "./guide/engine.mjs",
  "./favicon.svg"
];

self.addEventListener("install", function (event) {
  event.waitUntil(caches.open(CACHE).then(function (cache) {
    return cache.addAll(SHELL);
  }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (event) {
  event.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (key) { return key !== CACHE; }).map(function (key) {
      return caches.delete(key);
    }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener("fetch", function (event) {
  var request = event.request;
  if (request.method !== "GET") return;
  var url = new URL(request.url);
  if (url.origin !== self.location.origin) return;
  if (url.href.indexOf("cyphermonkeylabs.com") !== -1) return;
  event.respondWith(caches.match(request).then(function (hit) {
    var network = fetch(request).then(function (response) {
      if (response && response.ok && response.type === "basic") {
        var copy = response.clone();
        caches.open(CACHE).then(function (cache) { cache.put(request, copy); });
      }
      return response;
    }).catch(function () {
      if (hit) return hit;
      if (request.mode === "navigate") return caches.match("./offline.html");
      return hit;
    });
    return hit || network;
  }));
});
