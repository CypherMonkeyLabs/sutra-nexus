/* Chrome adapted from Webex Lab assets/js/frame.js and polish.js
   at commit 7631b317cbf2cad236403df960b5d5fac353a6de.
   Sanskrit study copy only. No Webex or Cisco wording. */
(function () {
  var root = document.documentElement;
  var THEMES = ["bloom", "dark", "light", "contrast"];
  var INKS = ["#1b1340", "#1a1a1a", "#ffffff", "#fde047", "#67e8f9", "#86efac"];

  function ls(key, value) {
    try {
      if (value === undefined) return localStorage.getItem(key);
      localStorage.setItem(key, value);
    } catch (err) { /* storage off */ }
    return null;
  }
  function contrast(hex, bg) {
    function lin(c) { c /= 255; return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4); }
    function lum(h) {
      var n = h.replace("#", "");
      if (n.length === 3) n = n[0] + n[0] + n[1] + n[1] + n[2] + n[2];
      var r = parseInt(n.slice(0, 2), 16), g = parseInt(n.slice(2, 4), 16), b = parseInt(n.slice(4, 6), 16);
      return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
    }
    var L1 = lum(hex), L2 = lum(bg);
    var light = Math.max(L1, L2), dark = Math.min(L1, L2);
    return (light + 0.05) / (dark + 0.05);
  }
  function bgHex() {
    var theme = root.dataset.theme || "bloom";
    if (theme === "dark") return "#100c22";
    if (theme === "contrast") return "#000000";
    if (theme === "light") return "#ffffff";
    return "#f4f0ff";
  }
  function applyFontScale(n) {
    n = Math.max(0.85, Math.min(1.6, n));
    root.style.setProperty("--fscale", String(n));
    ls("sutra-fscale", String(n));
    var slider = document.querySelector("[data-font-slider]");
    if (slider) slider.value = String(n);
  }
  function applyTheme(name) {
    if (THEMES.indexOf(name) < 0) name = "bloom";
    root.dataset.theme = name;
    ls("sutra-theme", name);
    document.querySelectorAll("[data-set-theme]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", btn.getAttribute("data-set-theme") === name ? "true" : "false");
    });
    warnInk();
  }
  function applyMotion(mode) {
    root.dataset.motion = mode;
    ls("sutra-motion", mode);
    var btn = document.querySelector("[data-motion-toggle]");
    if (btn) btn.setAttribute("aria-pressed", mode === "reduce" ? "true" : "false");
  }
  function setInk(color) {
    if (color) {
      root.style.setProperty("--ink", color);
      ls("sutra-ink", color);
    } else {
      root.style.removeProperty("--ink");
      ls("sutra-ink", "");
    }
    warnInk();
  }
  function warnInk() {
    var note = document.querySelector("[data-contrast-warn]");
    if (!note) return;
    var ink = (root.style.getPropertyValue("--ink") || "").trim();
    if (!ink) { note.textContent = ""; return; }
    var ratio = contrast(ink, bgHex());
    note.textContent = ratio < 4.5
      ? "Contrast is " + ratio.toFixed(2) + " to 1. Body text should be at least 4.5 to 1. Pick another color."
      : "Contrast is " + ratio.toFixed(2) + " to 1.";
  }

  var opener = null;
  function drawerEls() {
    return {
      drawer: document.querySelector(".drawer"),
      backdrop: document.querySelector(".backdrop"),
      buttons: document.querySelectorAll("[data-open-menu]")
    };
  }
  function focusables(drawer) {
    return Array.prototype.filter.call(drawer.querySelectorAll("a, button, input, select, textarea"), function (el) {
      return !el.disabled && el.getAttribute("aria-hidden") !== "true";
    });
  }
  function setDrawer(open) {
    var els = drawerEls();
    if (!els.drawer) return;
    els.drawer.classList.toggle("is-open", open);
    if (els.backdrop) els.backdrop.classList.toggle("is-open", open);
    els.buttons.forEach(function (btn) { btn.setAttribute("aria-expanded", open ? "true" : "false"); });
    document.body.classList.toggle("drawer-open", open);
    if (open) {
      var list = focusables(els.drawer);
      if (list[0]) list[0].focus();
    } else if (opener && opener.focus) {
      opener.focus();
    }
  }
  function bindDrawer() {
    document.addEventListener("click", function (event) {
      var openBtn = event.target.closest("[data-open-menu]");
      if (openBtn) {
        opener = openBtn;
        var els = drawerEls();
        setDrawer(!(els.drawer && els.drawer.classList.contains("is-open")));
        return;
      }
      if (event.target.closest("[data-close-menu]") || (event.target.classList && event.target.classList.contains("backdrop"))) {
        setDrawer(false);
      }
      var link = event.target.closest(".drawer a");
      if (link) setDrawer(false);
    });
    document.addEventListener("keydown", function (event) {
      var els = drawerEls();
      var open = els.drawer && els.drawer.classList.contains("is-open");
      if (event.key === "Escape" && open) {
        event.preventDefault();
        setDrawer(false);
        return;
      }
      if (!open || event.key !== "Tab") return;
      var list = focusables(els.drawer);
      if (!list.length) return;
      var first = list[0], last = list[list.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });
  }
  function bindBanner() {
    var rail = document.querySelector(".section-rail");
    if (!rail) return;
    document.querySelectorAll("[data-rail]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        rail.scrollBy({ left: Number(btn.getAttribute("data-rail")) * 240, behavior: root.dataset.motion === "reduce" ? "auto" : "smooth" });
      });
    });
    var current = rail.querySelector("[aria-current='page']");
    if (current) {
      var left = current.offsetLeft - (rail.clientWidth - current.offsetWidth) / 2;
      rail.scrollLeft = Math.max(0, left);
    }
  }
  function bindDisplay() {
    var btn = document.querySelector(".display-btn");
    var panel = document.querySelector(".display-panel");
    if (!btn || !panel) return;
    btn.addEventListener("click", function () {
      var open = panel.hasAttribute("hidden");
      if (open) panel.removeAttribute("hidden");
      else panel.setAttribute("hidden", "");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    panel.addEventListener("click", function (event) {
      var theme = event.target.closest("[data-set-theme]");
      if (theme) applyTheme(theme.getAttribute("data-set-theme"));
      var size = event.target.closest("[data-font-step]");
      if (size) applyFontScale((parseFloat(getComputedStyle(root).getPropertyValue("--fscale")) || 1) + Number(size.getAttribute("data-font-step")));
      if (event.target.closest("[data-font-reset]")) applyFontScale(1);
      var sw = event.target.closest("[data-ink]");
      if (sw) setInk(sw.getAttribute("data-ink"));
      if (event.target.closest("[data-ink-reset]")) setInk("");
      if (event.target.closest("[data-motion-toggle]")) {
        applyMotion(root.dataset.motion === "reduce" ? "full" : "reduce");
      }
    });
    var slider = panel.querySelector("[data-font-slider]");
    if (slider) slider.addEventListener("input", function () { applyFontScale(parseFloat(slider.value)); });
    var custom = panel.querySelector("[data-ink-custom]");
    if (custom) custom.addEventListener("input", function () { setInk(custom.value); });
    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && !panel.hasAttribute("hidden")) {
        panel.setAttribute("hidden", "");
        btn.setAttribute("aria-expanded", "false");
        btn.focus();
      }
    });
  }
  function bootPrefs() {
    var theme = ls("sutra-theme") || "bloom";
    if (THEMES.indexOf(theme) < 0) theme = "bloom";
    applyTheme(theme);
    var scale = parseFloat(ls("sutra-fscale") || "1");
    if (!scale) scale = 1;
    applyFontScale(scale);
    var motion = ls("sutra-motion");
    if (!motion) motion = window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "reduce" : "full";
    applyMotion(motion);
    var ink = ls("sutra-ink");
    if (ink && /^#[0-9a-f]{6}$/i.test(ink)) setInk(ink);
  }
  bootPrefs();
  bindDrawer();
  bindBanner();
  bindDisplay();
  if (/[?&]menu=1(?:&|$)/.test(location.search)) setDrawer(true);
  window.SutraFrame = { setDrawer: setDrawer, setInk: setInk };
})();
