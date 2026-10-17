/* Talking study guide. Layered glasses monkey, adapted from the BA lab
   companion pattern. Facts come from guide/kb through the local engine.
   Voice stays off until a reader turns it on. */
import { createGuide, blankSession } from "../../guide/engine.mjs";

var host = document.querySelector(".guide-root");
if (host) boot(host);

function ls(key, value) {
  try {
    if (value === undefined) return localStorage.getItem(key);
    if (value === null) localStorage.removeItem(key);
    else localStorage.setItem(key, value);
  } catch (err) { /* storage off */ }
  return null;
}

function esc(value) {
  return String(value == null ? "" : value).replace(/[&<>"']/g, function (ch) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[ch];
  });
}

function prefix() {
  var node = document.querySelector("script[src*='assets/js/guide.js']");
  var src = node ? node.getAttribute("src") || "" : "";
  var at = src.indexOf("assets/js/guide.js");
  return at === -1 ? "" : src.slice(0, at);
}

function phone() {
  return window.matchMedia("(max-width: 720px)").matches;
}

function motionOff() {
  if (document.documentElement.dataset.motion === "reduce") return true;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
}

function monkeySvg() {
  return '<span class="sb-soft" aria-hidden="true"></span>' +
    '<span class="sb-float" aria-hidden="true"><svg viewBox="0 0 220 260" aria-hidden="true">' +
    "<defs>" +
    '<radialGradient id="sbfur" cx="38%" cy="30%" r="78%"><stop offset="0" stop-color="#ffe08a"/><stop offset=".48" stop-color="#f5a524"/><stop offset="1" stop-color="#c2410c"/></radialGradient>' +
    '<radialGradient id="sbmuz" cx="50%" cy="28%" r="80%"><stop offset="0" stop-color="#fff7dc"/><stop offset="1" stop-color="#f0c27a"/></radialGradient>' +
    '<radialGradient id="sbear" cx="40%" cy="35%" r="75%"><stop offset="0" stop-color="#fecdd3"/><stop offset="1" stop-color="#e11d48"/></radialGradient>' +
    '<linearGradient id="sbglass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#22d3ee"/><stop offset=".5" stop-color="#7c3aed"/><stop offset="1" stop-color="#f472b6"/></linearGradient>' +
    '<linearGradient id="sbscarf" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#22d3ee"/><stop offset=".34" stop-color="#a78bfa"/><stop offset=".67" stop-color="#f472b6"/><stop offset="1" stop-color="#fbbf24"/></linearGradient>' +
    "</defs>" +
    '<ellipse cx="110" cy="248" rx="58" ry="8" fill="#1e1b4b" opacity=".2"/>' +
    '<path class="sb-tail" d="M172 200c26 6 34 26 16 38-16 10-30-4-24-16" fill="none" stroke="#ea580c" stroke-width="12" stroke-linecap="round"/>' +
    '<path d="M74 168c6 22 22 48 36 52s32-16 38-40c2 22-10 52-40 56s-46-20-34-68z" fill="url(#sbfur)"/>' +
    '<path class="sb-scarf" d="M80 162h62c-2 16-16 24-32 24s-28-8-30-24z" fill="url(#sbscarf)"/>' +
    '<g class="sb-head">' +
    '<circle class="sb-ear" cx="46" cy="92" r="30" fill="url(#sbfur)"/><circle cx="46" cy="92" r="16" fill="url(#sbear)"/>' +
    '<circle class="sb-ear" cx="174" cy="92" r="30" fill="url(#sbfur)"/><circle cx="174" cy="92" r="16" fill="url(#sbear)"/>' +
    '<circle cx="110" cy="102" r="64" fill="url(#sbfur)"/>' +
    '<ellipse cx="110" cy="122" rx="38" ry="30" fill="url(#sbmuz)"/>' +
    '<ellipse cx="76" cy="116" rx="11" ry="7" fill="#fb7185" opacity=".7"/>' +
    '<ellipse cx="144" cy="116" rx="11" ry="7" fill="#fb7185" opacity=".7"/>' +
    '<g class="sb-eye"><ellipse cx="86" cy="96" rx="14" ry="16" fill="#fff"/><circle cx="90" cy="98" r="7" fill="#1c1917"/><circle cx="93" cy="95" r="2.6" fill="#fff"/></g>' +
    '<g class="sb-eye"><ellipse cx="134" cy="96" rx="14" ry="16" fill="#fff"/><circle cx="138" cy="98" r="7" fill="#1c1917"/><circle cx="141" cy="95" r="2.6" fill="#fff"/></g>' +
    '<g class="sb-glasses" fill="none" stroke="url(#sbglass)" stroke-width="5" stroke-linecap="round">' +
    '<circle cx="86" cy="96" r="20"/><circle cx="134" cy="96" r="20"/><path d="M106 96h12"/>' +
    '<path d="M66 92c-10-2-16 4-16 10M154 92c10-2 16 4 16 10"/>' +
    "</g>" +
    '<ellipse cx="110" cy="120" rx="8" ry="5.5" fill="#9a3412"/>' +
    '<path class="sb-mouth" d="M90 136c8 12 32 12 40 0" fill="none" stroke="#7c2d12" stroke-width="4" stroke-linecap="round"/>' +
    "</g>" +
    '<g class="sb-arm sb-arm-left"><path d="M76 172v40" fill="none" stroke="#ea580c" stroke-width="16" stroke-linecap="round"/>' +
    '<circle cx="76" cy="218" r="14" fill="url(#sbfur)"/><circle cx="76" cy="218" r="7" fill="url(#sbmuz)"/></g>' +
    '<g class="sb-arm sb-arm-right"><path d="M146 172v40" fill="none" stroke="#ea580c" stroke-width="16" stroke-linecap="round"/>' +
    '<circle cx="146" cy="218" r="14" fill="url(#sbfur)"/><circle cx="146" cy="218" r="7" fill="url(#sbmuz)"/></g>' +
    '<g class="sb-pop" aria-hidden="true"><path d="M186 36l2.2 6.2 6.4.2-5 4 1.8 6.2-5.4-3.6-5.4 3.6 1.8-6.2-5-4 6.4-.2z" fill="#fde047"/>' +
    '<path d="M34 40l1.6 4.4 4.6.2-3.6 2.8 1.3 4.4-3.9-2.6-3.9 2.6 1.3-4.4-3.6-2.8 4.6-.2z" fill="#22d3ee"/></g>' +
    "</svg></span>";
}

function boot(root) {
  root.innerHTML =
    '<button type="button" class="sb-monkey" aria-expanded="false" aria-controls="sb-panel" aria-label="Sūtra guide. A student who has read these rooms.">' +
    monkeySvg() + "</button>" +
    '<section class="sb-panel" id="sb-panel" hidden role="dialog" aria-modal="false" aria-labelledby="sb-title">' +
    '<header class="sb-bar"><div class="sb-who"><span class="sb-avatar" aria-hidden="true"></span>' +
    '<div><h2 id="sb-title">Sūtra guide</h2><p class="sb-status">In the notes. Voice is on.</p></div></div>' +
    '<button type="button" data-guide-close>Close</button></header>' +
    '<div class="sb-along" role="group" aria-label="Read along">' +
    '<button type="button" data-along-start>Read along</button>' +
    '<button type="button" data-along-pause>Pause</button>' +
    '<button type="button" data-along-next>Next</button>' +
    '<button type="button" data-along-stop>Stop</button></div>' +
    '<div class="sb-log" role="log" aria-live="polite"></div>' +
    '<div class="sb-chips" role="group" aria-label="Commands"></div>' +
    '<p class="sb-note"></p>' +
    '<div class="sb-voice">' +
    '<button type="button" data-voice aria-pressed="true">Voice on</button>' +
    '<label>Voice <select data-voice-pick aria-label="Speaking voice"><option value="">Browser default</option></select></label>' +
    '<button type="button" data-voice-stop>Stop voice</button></div>' +
    '<form class="sb-form"><input type="text" aria-label="Ask about this page" placeholder="Ask, or say quiz me" autocomplete="off">' +
    '<button type="submit">Send</button></form></section>';

  var monkey = root.querySelector(".sb-monkey");
  var panel = root.querySelector(".sb-panel");
  var log = root.querySelector(".sb-log");
  var chips = root.querySelector(".sb-chips");
  var note = root.querySelector(".sb-note");
  var input = root.querySelector(".sb-form input");
  root.querySelector(".sb-avatar").innerHTML = monkeySvg();
  var session = blankSession();
  var guide = null;
  var guideReady = null;
  var voiceOn = ls("sutra-voice-on") !== "0";
  var along = { items: [], index: 0, timer: 0, paused: false, token: 0 };
  var page = (location.pathname.split("/").pop() || "index.html");

  function pose(name) {
    monkey.dataset.pose = name;
    root.dataset.pose = name;
  }
  pose("idle");

  function context() {
    return { page: page, room: document.body.dataset.room || "" };
  }

  function readRoot() {
    return document.querySelector("[data-room-panel]:not([hidden])") || document.querySelector("main") || document.body;
  }

  function place() {
    var disclaimer = document.querySelector(".disclaimer-panel");
    var lift = phone() ? 8 : 16;
    if (phone()) {
      var dock = document.querySelector(".phone-dock");
      lift = (dock ? dock.offsetHeight : 72) + 8;
    }
    if (disclaimer) {
      var rect = disclaimer.getBoundingClientRect();
      var overlap = rect.top < window.innerHeight - 8 && rect.bottom > window.innerHeight - 220;
      if (overlap) lift = Math.max(lift, window.innerHeight - rect.top + 12);
    }
    root.style.bottom = lift + "px";
    document.documentElement.style.setProperty("--guide-lift", lift + "px");
  }
  place();
  window.addEventListener("scroll", place, { passive: true });
  window.addEventListener("resize", place);
  var scroller = document.querySelector(".page-scroll");
  if (scroller) scroller.addEventListener("scroll", place, { passive: true });

  function ensureGuide() {
    if (guideReady) return guideReady;
    var kbReady = (window.SUTRA_EMBED && window.SUTRA_EMBED.kb)
      ? Promise.resolve(window.SUTRA_EMBED.kb)
      : fetch(prefix() + "guide/kb/bundle.json").then(function (res) { return res.json(); });
    guideReady = kbReady.then(function (kb) {
      guide = createGuide(kb, { rng: Math.random });
      return guide;
    }).catch(function () {
      log.innerHTML = "<p>I don't know yet, confirm before relying. The guide notes did not load.</p>";
      return null;
    });
    return guideReady;
  }

  function open(next) {
    panel.hidden = !next;
    monkey.hidden = !!next;
    monkey.setAttribute("aria-expanded", next ? "true" : "false");
    ls("sutra-guide-open", next ? "1" : "0");
    if (next) {
      pose("wave");
      ensureGuide();
    } else {
      pose("idle");
      stopAlong(false);
    }
    place();
  }

  function say(text) {
    if (!voiceOn || !window.speechSynthesis || !text) return;
    window.speechSynthesis.cancel();
    var utter = new SpeechSynthesisUtterance(text);
    var saved = ls("sutra-voice");
    var voices = window.speechSynthesis.getVoices();
    var pick = voices.filter(function (voice) { return saved && voice.name === saved; })[0];
    if (!pick) pick = voices.filter(function (voice) { return /natural|enhanced|premium/i.test(voice.name); })[0] || voices[0];
    if (pick) utter.voice = pick;
    utter.rate = 0.92;
    utter.pitch = 0.96;
    window.speechSynthesis.speak(utter);
  }

  function paint(reply) {
    var text = reply.text || "";
    var links = reply.links || [];
    if (reply.href && !links.some(function (link) { return link.href === reply.href; })) {
      links = [{ href: reply.href, title: "Open the note" }].concat(links);
    }
    var linkHtml = links.filter(function (link) { return link && link.href; }).map(function (link) {
      return '<a href="' + esc(link.href) + '">' + esc(link.title || link.href) + "</a>";
    }).join(" ");
    log.innerHTML = "<p>" + esc(text).replace(/\n/g, "<br>") + "</p>" + (linkHtml ? "<p class=\"sb-links\">" + linkHtml + "</p>" : "");
    var list = (reply.chips || []).concat(reply.extraChips || []);
    chips.innerHTML = list.map(function (chip) {
      return '<button type="button" data-chip="' + esc(chip) + '">' + esc(chip) + "</button>";
    }).join("");
    pose("talk");
    if (voiceOn) say(text);
    if (reply.kind === "tour" && window.SUTRA_SHOW_TOUR) window.SUTRA_SHOW_TOUR();
  }

  function welcome() {
    log.innerHTML = "<p>Welcome to CypherMonkey Labs. I'm your Sūtra guide. I only repeat what is written in this app. If I don't know, I will say so.</p>";
    var items = [
      ["Quiz me", "Quiz me"],
      ["Teach me this room", "Teach me this room"],
      ["Play a game", "Play a game"],
      ["Flashcards", "Flashcards"],
      ["How do I use this?", "How do I use this?"],
      ["Tour this room", "Tour this room"],
      ["1-hour course", "Start the 1-hour course"],
      ["Read along", "Read along"],
      ["Help", "Help"]
    ];
    chips.innerHTML = items.map(function (item) {
      return '<button type="button" data-chip="' + esc(item[1]) + '">' + esc(item[0]) + "</button>";
    }).join("");
    note.textContent = (voiceOn ? "Voice is on. " : "Voice is off. ") + "Browser voices may mispronounce Sanskrit. This is a reading aid, not a recitation.";
  }

  function ask(text) {
    if (!text) return;
    if (!guide) {
      ensureGuide().then(function () {
        if (guide) ask(text);
      });
      return;
    }
    var out = guide.route(text, session, context());
    session = out.session;
    paint(out.reply);
  }

  var hasHighlights = !!(window.CSS && CSS.highlights && window.Highlight);

  function clearSpoken() {
    document.querySelectorAll(".is-reading").forEach(function (node) { node.classList.remove("is-reading"); });
    if (hasHighlights) CSS.highlights.delete("sb-sentence");
  }

  function textRange(node, from, to) {
    var walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT);
    var range = document.createRange();
    var seen = 0;
    var started = false;
    var cur;
    while ((cur = walker.nextNode())) {
      var len = cur.nodeValue.length;
      if (!started && from < seen + len) { range.setStart(cur, from - seen); started = true; }
      if (started && to <= seen + len) { range.setEnd(cur, to - seen); return range; }
      seen += len;
    }
    return started ? range : null;
  }

  function alongItems() {
    var scope = readRoot();
    var nodes = scope.querySelectorAll("h1, h2, h3, p, li");
    var items = [];
    nodes.forEach(function (node) {
      if (node.closest(".sb-panel, .ob-card, .sb-log, .drawer, .site-header, .phone-dock, .disclaimer-panel, svg")) return;
      if (node.querySelector("h1, h2, h3, p, li")) return;
      var raw = node.textContent || "";
      var found = false;
      var re = /[\s\S]+?[.!?\u0964\u0965](?=\s|$)|[\s\S]+$/g;
      var m;
      while ((m = re.exec(raw))) {
        var lead = m[0].length - m[0].replace(/^\s+/, "").length;
        var text = m[0].replace(/\s+/g, " ").trim();
        if (text.length < 2) continue;
        found = true;
        items.push({ node: node, text: text, from: m.index + lead, to: m.index + m[0].replace(/\s+$/, "").length });
      }
      if (!found) {
        var whole = raw.replace(/\s+/g, " ").trim();
        if (whole.length >= 2) items.push({ node: node, text: whole, from: 0, to: raw.length });
      }
    });
    return items;
  }

  function showAlong() {
    clearSpoken();
    var item = along.items[along.index];
    if (!item) return;
    item.node.classList.add("is-reading");
    var range = hasHighlights ? textRange(item.node, item.from, item.to) : null;
    if (range) CSS.highlights.set("sb-sentence", new Highlight(range));
    var target = range ? range.getBoundingClientRect() : item.node.getBoundingClientRect();
    var scroller = document.querySelector(".page-scroll");
    var box = scroller ? scroller.getBoundingClientRect() : { top: 0, bottom: window.innerHeight };
    var low = Math.min(box.bottom, window.innerHeight) - (phone() ? 230 : 120);
    if (target.top < box.top + 70 || target.bottom > low) {
      var delta = target.top - box.top - 90;
      if (scroller) scroller.scrollBy({ top: delta, behavior: motionOff() ? "auto" : "smooth" });
      else window.scrollBy({ top: delta, behavior: motionOff() ? "auto" : "smooth" });
    }
    window.clearTimeout(along.timer);
    var token = ++along.token;
    function advance() {
      if (token !== along.token || along.paused || !along.items.length) return;
      stepAlong(1);
    }
    if (voiceOn && window.speechSynthesis) {
      window.speechSynthesis.cancel();
      var utter = new SpeechSynthesisUtterance(item.text);
      utter.rate = 0.92;
      utter.onend = advance;
      utter.onerror = advance;
      window.speechSynthesis.speak(utter);
      along.timer = window.setTimeout(advance, 3000 + item.text.length * 95);
      return;
    }
    along.timer = window.setTimeout(advance, Math.min(4200, 900 + item.text.length * 28));
  }

  function stepAlong(dir) {
    if (!along.items.length) return;
    along.index += dir;
    if (along.index >= along.items.length) {
      stopAlong(true);
      return;
    }
    if (along.index < 0) along.index = 0;
    showAlong();
  }

  function startAlong() {
    along.items = alongItems();
    along.index = 0;
    along.paused = false;
    if (!along.items.length) {
      note.textContent = "There is no readable text on this page yet.";
      return;
    }
    note.textContent = voiceOn
      ? "Read along is speaking this page. Sanskrit may be pronounced wrong."
      : "Read along is highlighting this page. Turn voice on if you want to hear it.";
    showAlong();
  }

  function stopAlong(done) {
    along.paused = true;
    along.token += 1;
    along.items = [];
    window.clearTimeout(along.timer);
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    clearSpoken();
    if (done) note.textContent = "Read along finished. Voice stays where you left it.";
  }

  monkey.addEventListener("click", function () { open(true); });
  root.querySelector("[data-guide-close]").addEventListener("click", function () { open(false); monkey.focus(); });
  document.addEventListener("sutra-guide-open", function () { open(true); });
  root.querySelector("[data-along-start]").addEventListener("click", startAlong);
  root.querySelector("[data-along-pause]").addEventListener("click", function () {
    along.paused = !along.paused;
    this.textContent = along.paused ? "Resume" : "Pause";
    if (along.paused) {
      window.clearTimeout(along.timer);
      if (window.speechSynthesis) window.speechSynthesis.cancel();
    } else if (along.items.length) showAlong();
  });
  root.querySelector("[data-along-next]").addEventListener("click", function () {
    along.paused = false;
    if (!along.items.length) startAlong();
    else stepAlong(1);
  });
  root.querySelector("[data-along-stop]").addEventListener("click", function () { stopAlong(false); });

  chips.addEventListener("click", function (event) {
    var btn = event.target.closest("[data-chip]");
    if (!btn) return;
    var chip = btn.getAttribute("data-chip");
    if (chip === "Read along") {
      startAlong();
      return;
    }
    ask(chip);
  });
  root.querySelector(".sb-form").addEventListener("submit", function (event) {
    event.preventDefault();
    var text = input.value.trim();
    input.value = "";
    if (text.toLowerCase() === "read along") startAlong();
    else ask(text);
  });

  function fillVoices() {
    var select = root.querySelector("[data-voice-pick]");
    if (!window.speechSynthesis || !select) return;
    var voices = window.speechSynthesis.getVoices();
    select.innerHTML = '<option value="">Browser default</option>' + voices.map(function (voice) {
      return '<option value="' + esc(voice.name) + '">' + esc(voice.name) + "</option>";
    }).join("");
    var saved = ls("sutra-voice");
    if (saved) select.value = saved;
  }
  if (window.speechSynthesis) {
    fillVoices();
    window.speechSynthesis.addEventListener("voiceschanged", fillVoices);
  }
  root.querySelector("[data-voice]").addEventListener("click", function () {
    voiceOn = !voiceOn;
    ls("sutra-voice-on", voiceOn ? "1" : "0");
    if (!voiceOn && window.speechSynthesis) window.speechSynthesis.cancel();
    this.textContent = voiceOn ? "Voice on" : "Voice off";
    this.setAttribute("aria-pressed", voiceOn ? "true" : "false");
    note.textContent = voiceOn
      ? "Voice is on. Browser voices may mispronounce Sanskrit. This is a reading aid, not a recitation."
      : "Voice is off. Browser voices may mispronounce Sanskrit. This is a reading aid, not a recitation.";
  });
  root.querySelector("[data-voice-pick]").addEventListener("change", function (event) {
    ls("sutra-voice", event.target.value);
  });
  root.querySelector("[data-voice-stop]").addEventListener("click", function () {
    if (window.speechSynthesis) window.speechSynthesis.cancel();
  });

  var drag = null;
  monkey.addEventListener("pointerdown", function (event) {
    if (phone() || event.button !== 0) return;
    drag = { x: event.clientX, y: event.clientY, left: root.offsetLeft, top: root.offsetTop, moved: false };
    monkey.setPointerCapture(event.pointerId);
  });
  monkey.addEventListener("pointermove", function (event) {
    if (!drag) return;
    var dx = event.clientX - drag.x;
    var dy = event.clientY - drag.y;
    if (Math.abs(dx) + Math.abs(dy) > 6) drag.moved = true;
    root.style.left = Math.max(8, drag.left + dx) + "px";
    root.style.right = "auto";
    root.style.top = Math.max(8, drag.top + dy) + "px";
    root.style.bottom = "auto";
  });
  monkey.addEventListener("pointerup", function () {
    if (drag && drag.moved) monkey.dataset.dragged = "1";
    drag = null;
  });
  monkey.addEventListener("click", function (event) {
    if (monkey.dataset.dragged === "1") {
      event.stopImmediatePropagation();
      delete monkey.dataset.dragged;
    }
  }, true);

  function speakTour(event) {
    var d = event.detail || {};
    if (d.text && voiceOn) say(d.text);
    pose(d.last ? "wave" : "talk");
  }
  document.addEventListener("sutra-tour-step", speakTour);
  welcome();
  if (ls("sutra-guide-open") === "1" && !phone()) open(true);
  if (/[?&]guide=1(?:&|$)/.test(location.search)) open(true);
}
