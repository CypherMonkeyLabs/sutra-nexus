/* Rooms, search, quizzes, games, flashcards, and the lazy sūtra index. */
(function () {
  var root = document.documentElement;
  function esc(value) {
    return String(value == null ? "" : value).replace(/[&<>"']/g, function (ch) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
    });
  }
  function ls(key, value) {
    try {
      if (value === undefined) return JSON.parse(localStorage.getItem(key));
      localStorage.setItem(key, JSON.stringify(value));
    } catch (err) { return value === undefined ? null : null; }
    return null;
  }
  function prefix() {
    var node = document.querySelector("script[src*='assets/js/app.js']");
    if (!node) return "";
    var src = node.getAttribute("src") || "";
    var at = src.indexOf("assets/js/app.js");
    return at === -1 ? "" : src.slice(0, at);
  }
  var base = prefix();

  function bindQuiz() {
    document.querySelectorAll(".quiz-q").forEach(function (block) {
      var answer = Number(block.getAttribute("data-answer"));
      var why = block.querySelector(".why");
      block.querySelectorAll("button").forEach(function (btn, index) {
        btn.addEventListener("click", function () {
          block.querySelectorAll("button").forEach(function (peer) { peer.setAttribute("aria-pressed", "false"); });
          btn.setAttribute("aria-pressed", "true");
          var ok = index === answer;
          if (why) {
            why.textContent = (ok ? "Yes. " : "Not this one. ") + (block.getAttribute("data-why") || "");
          }
          var progress = ls("sutra-quiz") || {};
          progress[block.id || btn.textContent.slice(0, 24)] = ok;
          ls("sutra-quiz", progress);
        });
      });
    });
  }

  function bindPath() {
    var box = document.querySelector("[data-path]");
    if (!box) return;
    var saved = ls("sutra-path") || {};
    box.querySelectorAll("[data-step]").forEach(function (btn) {
      var id = btn.getAttribute("data-step");
      function paint() { btn.setAttribute("aria-pressed", saved[id] ? "true" : "false"); btn.textContent = (saved[id] ? "Done: " : "Mark done: ") + btn.getAttribute("data-label"); }
      paint();
      btn.addEventListener("click", function () {
        saved[id] = !saved[id];
        ls("sutra-path", saved);
        paint();
        var total = box.querySelectorAll("[data-step]").length;
        var done = Object.keys(saved).filter(function (key) { return saved[key]; }).length;
        var meter = box.querySelector("[data-path-meter]");
        if (meter) meter.textContent = done + " of " + total + " steps marked on this device.";
      });
    });
  }

  var indexPromise = null;
  function loadIndex() {
    if (!indexPromise) {
      if (window.SUTRA_EMBED && window.SUTRA_EMBED.search) indexPromise = Promise.resolve(window.SUTRA_EMBED.search);
      else indexPromise = fetch(base + "assets/data/search-index.json").then(function (res) { return res.json(); });
    }
    return indexPromise;
  }
  function renderHits(items) {
    var host = document.querySelector("[data-search-hits]");
    if (!host) return;
    host.innerHTML = items.slice(0, 12).map(function (item) {
      return '<a class="search-hit" href="' + esc(base + item.href) + '"><b>' + esc(item.title) + '</b><span>' + esc(item.kind) + (item.note ? " · " + esc(item.note) : "") + "</span></a>";
    }).join("") || "<p>No match in the offline index.</p>";
  }
  function bindSearch() {
    var input = document.querySelector("[data-search]");
    if (!input) return;
    var timer;
    input.addEventListener("input", function () {
      clearTimeout(timer);
      var q = input.value.trim().toLowerCase();
      timer = setTimeout(function () {
        if (q.length < 1) { renderHits([]); return; }
        loadIndex().then(function (data) {
          var hits = (data.items || []).filter(function (item) {
            return (item.hay || "").toLowerCase().indexOf(q) !== -1;
          });
          renderHits(hits);
        }).catch(function () {
          var host = document.querySelector("[data-search-hits]");
          if (host) host.textContent = "The search index did not load. confirm before relying.";
        });
      }, 120);
    });
  }

  function bindFilters() {
    var bar = document.querySelector("[data-filters]");
    if (!bar) return;
    bar.addEventListener("click", function (event) {
      var btn = event.target.closest("[data-filter]");
      if (!btn) return;
      var kind = btn.getAttribute("data-filter");
      document.querySelectorAll("details.dl-room").forEach(function (section) {
        var any = false;
        section.querySelectorAll("[data-dl]").forEach(function (card) {
          var show = kind === "all" || card.getAttribute("data-kind") === kind || card.getAttribute("data-room") === kind;
          card.hidden = !show;
          if (show) any = true;
        });
        section.hidden = !any;
        if (any && kind !== "all") section.open = true;
      });
    });
  }

  function lines() {
    return window.SUTRA_LINES || [];
  }
  function pratyahara(start, startLine, markerLine) {
    var seq = [];
    lines().forEach(function (line) {
      line.sounds.forEach(function (sound) { seq.push({ line: line.n, sound: sound }); });
    });
    var i = -1;
    seq.forEach(function (item, index) {
      if (i < 0 && item.sound === start && item.line === startLine) i = index;
    });
    if (i < 0) return [];
    var out = [];
    for (var k = i; k < seq.length; k += 1) {
      if (seq[k].line > markerLine) break;
      if (out.indexOf(seq[k].sound) < 0) out.push(seq[k].sound);
    }
    return out;
  }
  function bindBuilder() {
    if (!lines().length) return;
    document.querySelectorAll("[data-pratyahara]").forEach(function (host) {
      var start = host.querySelector("[data-start]");
      var marker = host.querySelector("[data-marker]");
      var out = host.querySelector("[data-pr-out]");
      if (!start || !marker || !out) return;
      function run() {
        var parts = (start.value || "a|1").split("|");
        var sounds = pratyahara(parts[0], Number(parts[1]), Number(marker.value));
        out.textContent = sounds.length ? sounds.join(" · ") : "No set. Check the start and the marker line.";
      }
      start.addEventListener("change", run);
      marker.addEventListener("change", run);
      run();
    });
  }

  function bindGame() {
    document.querySelectorAll("[data-game]").forEach(function (form) {
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        var expect = form.getAttribute("data-expect");
        var value = (new FormData(form).get("answer") || "").toString().trim();
        var note = form.querySelector(".why");
        var ok = value.toLowerCase() === String(expect).toLowerCase();
        if (note) note.textContent = ok ? "Yes. " + (form.getAttribute("data-why") || "") : "Not this one. " + (form.getAttribute("data-why") || "");
      });
    });
  }

  function bindCards() {
    var host = document.querySelector("[data-cards]");
    if (!host) return;
    var cardsReady = (window.SUTRA_EMBED && window.SUTRA_EMBED.cards)
      ? Promise.resolve(window.SUTRA_EMBED.cards)
      : fetch(base + "downloads/flashcards.json").then(function (res) { return res.json(); });
    cardsReady.then(function (data) {
      var cards = data.cards || [];
      var state = ls("sutra-cards") || {};
      var cursor = 0;
      function due(card) {
        var row = state[card.id] || { n: 0, due: 0 };
        return row.due <= Date.now();
      }
      function next() {
        for (var i = 0; i < cards.length; i += 1) {
          var index = (cursor + i) % cards.length;
          if (due(cards[index])) return index;
        }
        return cursor % cards.length;
      }
      function show(reveal) {
        var card = cards[next()];
        cursor = cards.indexOf(card);
        host.querySelector("[data-card-front]").textContent = card.front;
        host.querySelector("[data-card-back]").textContent = reveal ? card.back + " — " + card.source : "Tap show.";
        host.querySelector("[data-card-back]").hidden = !reveal;
      }
      host.querySelector("[data-card-show]").addEventListener("click", function () { show(true); });
      host.querySelector("[data-card-again]").addEventListener("click", function () {
        var card = cards[cursor];
        state[card.id] = { n: 0, due: Date.now() + 60 * 1000 };
        ls("sutra-cards", state);
        cursor += 1;
        show(false);
      });
      host.querySelector("[data-card-know]").addEventListener("click", function () {
        var card = cards[cursor];
        var row = state[card.id] || { n: 0, due: 0 };
        row.n += 1;
        var day = 24 * 60 * 60 * 1000;
        row.due = Date.now() + (row.n === 1 ? day : row.n === 2 ? 3 * day : 7 * day);
        state[card.id] = row;
        ls("sutra-cards", state);
        cursor += 1;
        show(false);
      });
      show(false);
    }).catch(function () {
      host.insertAdjacentHTML("beforeend", "<p>Flashcards did not load. confirm before relying.</p>");
    });
  }

  function bindSutraBrowser() {
    var host = document.querySelector("[data-sutra-browser]");
    if (!host) return;
    var input = host.querySelector("input");
    var out = host.querySelector("[data-sutra-out]");
    var cache = null;
    input.addEventListener("input", function () {
      var q = input.value.trim();
      if (q.length < 1) { out.textContent = "Type a number such as 1.1.1, or a few letters of the transliteration."; return; }
      var run = function () {
        var hits = cache.filter(function (row) {
          return row[0].indexOf(q) !== -1 || row[1].indexOf(q) !== -1 || row[2].toLowerCase().indexOf(q.toLowerCase()) !== -1;
        }).slice(0, 20);
        out.innerHTML = hits.map(function (row) {
          return "<p><b>" + esc(row[0]) + "</b> <span class=\"deva\">" + esc(row[1]) + "</span><br><span>" + esc(row[2]) + "</span><br><small>meaning: not yet sourced from an open text. Transliteration is script-converted, not yet human-checked.</small></p>";
        }).join("") || "<p>No line matched.</p>";
      };
      if (cache) { run(); return; }
      out.textContent = "Loading the sūtra index…";
      var sutraReady = (window.SUTRA_EMBED && window.SUTRA_EMBED.sutras)
        ? Promise.resolve(window.SUTRA_EMBED.sutras)
        : fetch(base + "assets/data/sutra-index.json").then(function (res) { return res.json(); });
      sutraReady.then(function (data) {
        cache = data.rows || [];
        run();
      }).catch(function () { out.textContent = "The sūtra index did not load. confirm before relying."; });
    });
  }

  function bindThree() {
    var btn = document.querySelector("[data-load-three]");
    if (!btn) return;
    btn.addEventListener("click", function () {
      if (window.matchMedia("(max-width: 720px)").matches || root.dataset.motion === "reduce") {
        btn.insertAdjacentHTML("afterend", "<p>The 3D wheel stays off on a phone and when motion is reduced. The poster image is the still version.</p>");
        return;
      }
      import("./effects.js").catch(function () {
        btn.insertAdjacentHTML("afterend", "<p>The 3D extra did not start. The still poster is the version to rely on.</p>");
      });
    });
  }

  bindQuiz();
  bindPath();
  bindSearch();
  bindFilters();
  bindBuilder();
  bindGame();
  bindCards();
  bindSutraBrowser();
  bindThree();
})();
