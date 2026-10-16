/* First-open tour. A card, not a modal. The page stays clickable.
   The card sits under the title, sizes to its text, and stays inside the viewport.
   It is stored in this browser and shown once. */
(function () {
  var KEY = "sutra-tour-done";
  var soundOn = false;
  var audio = null;
  var layer = null;
  var step = 0;
  var reduce = false;

  var STEPS = [
    {
      title: "Home",
      selectors: ["a.brand"],
      body: "This is Home. The name in the header brings you back to the front door, where the six-step path starts."
    },
    {
      title: "Menu",
      selectors: [".menu-btn", ".phone-dock [data-open-menu]"],
      body: "Menu is the large button at the top left on a wide screen, and the left side of the bottom bar on a phone. It slides open. Escape, Close, or a tap outside puts it away."
    },
    {
      title: "Learn",
      selectors: [".phone-dock a[href$='foundations.html']", "a.section-chip[href$='foundations.html']"],
      body: "Learn opens Foundations. Each room has a short note, a picture, a worked example, a quiz, and sources."
    },
    {
      title: "Diagrams",
      selectors: [".phone-dock a[href*='diagrams.html']", "a.section-chip[href*='diagrams.html']"],
      body: "Diagrams are the study drawings. Open one, then use its download links if you want the SVG or PNG."
    },
    {
      title: "Play and Listen",
      selectors: [".phone-dock a[href*='play.html']", ".phone-dock a[href*='listen.html']", "a.section-chip[href*='play.html']"],
      body: "Play is the practice page. Listen is a script you read. Speech stays off until you choose it."
    },
    {
      title: "Downloads and the guide",
      selectors: ["a.section-chip[href*='downloads.html']", ".sb-monkey"],
      body: "Downloads holds the sheets, the cards, and one optional zip. The monkey is the guide. You can drag it on a wide screen and close it. This card does not block the page."
    }
  ];

  function ls(key, value) {
    try {
      if (value === undefined) return localStorage.getItem(key);
      if (value === null) localStorage.removeItem(key);
      else localStorage.setItem(key, value);
    } catch (err) { return null; }
    return null;
  }

  function motionOff() {
    if (document.documentElement.dataset.motion === "reduce") return true;
    return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function chime() {
    if (!soundOn || reduce) return;
    var Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;
    if (!audio) audio = new Ctx();
    audio.resume();
    var osc = audio.createOscillator();
    var gain = audio.createGain();
    osc.type = "sine";
    osc.frequency.value = 520;
    gain.gain.setValueAtTime(0.0001, audio.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.03, audio.currentTime + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, audio.currentTime + 0.28);
    osc.connect(gain);
    gain.connect(audio.destination);
    osc.start();
    osc.stop(audio.currentTime + 0.3);
  }

  function visible(el) {
    if (!el || el.closest("[hidden]")) return false;
    var style = getComputedStyle(el);
    if (style.display === "none" || style.visibility === "hidden") return false;
    var rect = el.getBoundingClientRect();
    return rect.width > 8 && rect.height > 8 && rect.bottom > 0 && rect.right > 0 && rect.top < window.innerHeight && rect.left < window.innerWidth;
  }

  function targets() {
    var found = [];
    (STEPS[step].selectors || []).forEach(function (selector) {
      document.querySelectorAll(selector).forEach(function (el) {
        if (found.indexOf(el) !== -1 || !visible(el)) return;
        var scroller = el.closest(".rail-scroller");
        if (scroller) {
          var left = el.offsetLeft - 24;
          if (left < scroller.scrollLeft || left > scroller.scrollLeft + scroller.clientWidth - 80) scroller.scrollLeft = Math.max(0, left);
        }
        found.push(el);
      });
    });
    return found.slice(0, 2);
  }

  function heading() {
    return document.querySelector("main h1, h1");
  }

  function overlapsHeading(rect) {
    var h1 = heading();
    if (!h1) return false;
    var box = h1.getBoundingClientRect();
    return rect.bottom > box.top && rect.top < box.bottom && rect.right > box.left && rect.left < box.right;
  }

  function paintSpots(nodes) {
    layer.querySelectorAll(".ob-spot").forEach(function (spot) { spot.remove(); });
    var h1 = heading();
    nodes.forEach(function (el) {
      if (h1 && (el === h1 || h1.contains(el))) return;
      var rect = el.getBoundingClientRect();
      if (overlapsHeading(rect)) return;
      var spot = document.createElement("div");
      spot.className = "ob-spot";
      spot.style.top = Math.max(4, rect.top - 4) + "px";
      spot.style.left = Math.max(4, rect.left - 4) + "px";
      spot.style.width = Math.min(window.innerWidth - 8, rect.width + 8) + "px";
      spot.style.height = rect.height + 8 + "px";
      layer.appendChild(spot);
    });
  }

  function placeCard() {
    var card = layer.querySelector(".ob-card");
    var h1 = heading();
    var dock = 8;
    if (window.matchMedia("(max-width: 720px)").matches) {
      var bar = document.querySelector(".phone-dock");
      dock = (bar ? bar.offsetHeight : 72) + 8;
    }
    var top = 8;
    if (h1) {
      var rect = h1.getBoundingClientRect();
      if (rect.bottom > 0 && rect.top < window.innerHeight) top = Math.max(8, Math.round(rect.bottom + 10));
    }
    var maxH = Math.max(120, window.innerHeight - top - dock);
    card.style.top = top + "px";
    card.style.bottom = "auto";
    card.style.maxHeight = maxH + "px";
    card.style.height = "auto";
    if (window.innerWidth < 800) {
      card.style.left = "8px";
      card.style.right = "8px";
      card.style.width = "auto";
      card.style.transform = "none";
    } else {
      card.style.left = "50%";
      card.style.right = "auto";
      card.style.width = "min(440px, calc(100vw - 32px))";
      card.style.transform = "translateX(-50%)";
    }
  }

  function paint() {
    var card = layer.querySelector(".ob-card");
    var item = STEPS[step];
    card.querySelector("[data-ob-num]").textContent = String(step + 1);
    card.querySelector("h2").textContent = item.title;
    card.querySelector(".ob-body").textContent = item.body;
    card.querySelector("[data-ob-count]").textContent = (step + 1) + " of " + STEPS.length;
    var next = card.querySelector("[data-ob-next]");
    next.textContent = step === STEPS.length - 1 ? "OK" : "Next";
    card.querySelector("[data-ob-back]").hidden = step === 0;
    placeCard();
    paintSpots(targets());
  }

  function close(finished) {
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    document.body.classList.remove("tour-open");
    if (layer) layer.remove();
    layer = null;
    if (finished === "done" || finished === "skip") {
      ls(KEY, finished === "done" ? "1" : "skip");
      document.dispatchEvent(new CustomEvent("sutra-tour-finished"));
    }
  }

  function open() {
    if (layer) return;
    reduce = motionOff();
    document.body.classList.add("tour-open");
    layer = document.createElement("div");
    layer.className = "ob-layer" + (reduce ? " is-still" : "");
    layer.innerHTML =
      '<div class="ob-card" role="dialog" aria-modal="false" aria-labelledby="ob-title">' +
      '<p class="ob-count"><span class="ob-num" data-ob-num>1</span> <span data-ob-count></span></p>' +
      '<h2 id="ob-title"></h2><p class="ob-body"></p>' +
      '<div class="ob-actions">' +
      '<button type="button" data-ob-sound aria-pressed="false">Sound off</button>' +
      '<button type="button" data-ob-back hidden>Back</button>' +
      '<button type="button" data-ob-skip>Skip</button>' +
      '<button type="button" data-ob-next>Next</button></div></div>';
    document.body.appendChild(layer);
    step = 0;
    paint();
    layer.querySelector("[data-ob-next]").focus();
    layer.addEventListener("click", function (event) {
      if (event.target.closest("[data-ob-sound]")) {
        soundOn = !soundOn;
        var button = layer.querySelector("[data-ob-sound]");
        button.setAttribute("aria-pressed", soundOn ? "true" : "false");
        button.textContent = soundOn ? "Sound on" : "Sound off";
        if (soundOn) chime();
        return;
      }
      if (event.target.closest("[data-ob-back]")) {
        if (step > 0) { step -= 1; paint(); }
        return;
      }
      if (event.target.closest("[data-ob-skip]")) {
        close("skip");
        return;
      }
      if (event.target.closest("[data-ob-next]")) {
        chime();
        if (step >= STEPS.length - 1) close("done");
        else { step += 1; paint(); }
      }
    });
    document.addEventListener("keydown", onKey);
    window.addEventListener("resize", onMove);
    window.addEventListener("scroll", onMove, true);
  }

  function onKey(event) {
    if (!layer) return;
    if (event.key === "Escape") close("skip");
  }

  function onMove() {
    if (!layer) return;
    placeCard();
    paintSpots(targets());
  }

  function shouldShow() {
    var params = new URLSearchParams(location.search);
    if (params.get("tour") === "1") return true;
    return !ls(KEY);
  }

  document.addEventListener("click", function (event) {
    if (!event.target.closest("[data-replay-onboard]")) return;
    event.preventDefault();
    ls(KEY, null);
    open();
  });

  window.SUTRA_SHOW_TOUR = function () {
    ls(KEY, null);
    open();
  };

  if (shouldShow()) window.setTimeout(open, 400);
})();
