/* Phone dock adapted from Webex Lab assets/js/phone-nav.js and polish.js
   at commit 7631b317cbf2cad236403df960b5d5fac353a6de. */
(function () {
  function ls(key, value) {
    try {
      if (value === undefined) return localStorage.getItem(key);
      localStorage.setItem(key, value);
    } catch (err) { /* storage off */ }
    return null;
  }
  function mountHint() {
    var hint = document.querySelector(".nav-hint");
    if (!hint) return;
    if (!window.matchMedia("(max-width: 720px)").matches || ls("sutra-nav-hint") === "1") {
      hint.remove();
      return;
    }
    var dock = document.querySelector(".phone-dock");
    function fit() {
      if (!dock) return;
      var next = dock.offsetHeight;
      var current = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--dock-h")) || 0;
      if (Math.abs(next - current) > 4) document.documentElement.style.setProperty("--dock-h", next + "px");
    }
    window.addEventListener("resize", fit);
    function close() {
      hint.remove();
      document.documentElement.style.removeProperty("--dock-h");
      document.documentElement.removeAttribute("data-nav-hint");
      ls("sutra-nav-hint", "1");
    }
    hint.querySelector("button").addEventListener("click", close);
    var menu = document.querySelector(".phone-dock [data-open-menu]");
    if (menu) menu.addEventListener("click", close);
    function park() {
      var disclaimer = document.querySelector(".site-footer");
      if (!disclaimer || !hint.isConnected) return;
      var box = disclaimer.getBoundingClientRect();
      var tip = hint.getBoundingClientRect();
      var overlap = box.top < tip.bottom && box.bottom > tip.top;
      hint.style.visibility = overlap ? "hidden" : "visible";
    }
    park();
    window.addEventListener("scroll", park, { passive: true });
    var scroller = document.querySelector(".page-scroll");
    if (scroller) scroller.addEventListener("scroll", park, { passive: true });
  }
  function markDock() {
    var file = (location.pathname.split("/").pop() || "index.html");
    document.querySelectorAll(".dock-item[href]").forEach(function (link) {
      var href = (link.getAttribute("href") || "").split("/").pop();
      if (href === file) link.setAttribute("aria-current", "page");
    });
  }
  function bindGuide() {
    document.querySelectorAll("[data-open-guide]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        document.dispatchEvent(new CustomEvent("sutra-guide-open"));
      });
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", function () { mountHint(); markDock(); bindGuide(); });
  else { mountHint(); markDock(); bindGuide(); }
})();
