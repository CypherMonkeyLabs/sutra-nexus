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
    if (!window.matchMedia("(max-width: 720px)").matches) return;
    if (ls("sutra-nav-hint") === "1" || document.querySelector(".nav-hint")) return;
    var hint = document.createElement("div");
    hint.className = "nav-hint";
    hint.setAttribute("role", "dialog");
    hint.setAttribute("aria-label", "How to open the menu");
    hint.innerHTML = "<b>Tap for menu</b><p>The glowing Menu button lists every section.</p><button type=\"button\">Got it</button>";
    document.body.appendChild(hint);
    function close() {
      hint.remove();
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
