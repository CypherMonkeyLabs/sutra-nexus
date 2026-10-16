/* Guide bot shell. The study router is guide/engine.mjs, adapted from
   Webex Lab guide/engine.mjs at commit 7631b317cbf2cad236403df960b5d5fac353a6de.
   Voice is off until the reader turns it on. */
import { createGuide, blankSession } from "../../guide/engine.mjs";

var root = document.documentElement;
var host = document.querySelector(".guide-root");
if (host) boot();

function ls(key, value) {
  try {
    if (value === undefined) return localStorage.getItem(key);
    localStorage.setItem(key, value);
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

function boot() {
  host.innerHTML = '<button type="button" class="guide-fab" aria-expanded="false" aria-controls="guide-panel" aria-label="Open the Sūtra guide"><span class="sr">Guide</span></button><section id="guide-panel" class="guide-panel" hidden><header><div class="guide-face" aria-hidden="true"></div><strong>Sūtra guide</strong><button type="button" data-guide-close>Close</button></header><div class="guide-log" aria-live="polite"></div><div class="guide-cards"></div><p class="voice-note"></p><div class="voice-row"></div></section>';
  var face = host.querySelector(".guide-face");
  if (window.SUTRA_BRAND) {
    face.innerHTML = window.SUTRA_BRAND.monkey("guide").replace("<svg", "<svg class=\"monkey-idle\"");
  }
  var fab = host.querySelector(".guide-fab");
  var panel = host.querySelector(".guide-panel");
  var log = host.querySelector(".guide-log");
  var cards = host.querySelector(".guide-cards");
  var session = blankSession();
  var guide = null;
  var speaking = false;
  var voiceOn = false;
  var page = (location.pathname.split("/").pop() || "index.html");

  function place() {
    var disclaimer = document.querySelector(".disclaimer-panel");
    if (!disclaimer) return;
    var rect = disclaimer.getBoundingClientRect();
    var overlap = rect.top < window.innerHeight - 8 && rect.bottom > 80;
    host.style.bottom = "";
    if (!overlap) return;
    var lift = Math.max(16, window.innerHeight - rect.top + 12);
    if (window.matchMedia("(max-width: 720px)").matches) {
      host.style.bottom = "calc(" + lift + "px)";
    } else {
      host.style.bottom = lift + "px";
    }
  }
  place();
  window.addEventListener("scroll", place, { passive: true });
  window.addEventListener("resize", place);

  var guideReady = null;
  function ensureGuide() {
    if (guideReady) return guideReady;
    var kbReady = (window.SUTRA_EMBED && window.SUTRA_EMBED.kb)
      ? Promise.resolve(window.SUTRA_EMBED.kb)
      : fetch(prefix() + "guide/kb/bundle.json").then(function (res) { return res.json(); });
    guideReady = kbReady.then(function (kb) {
      guide = createGuide(kb, { rng: Math.random });
      welcome();
      return guide;
    }).catch(function () {
      log.textContent = "I don't know yet, confirm before relying. The guide notes did not load.";
      return null;
    });
    return guideReady;
  }
  function open(next) {
    if (next) panel.hidden = false;
    else panel.hidden = true;
    fab.setAttribute("aria-expanded", next ? "true" : "false");
    fab.hidden = next;
    ls("sutra-guide-open", next ? "1" : "0");
    if (next) ensureGuide();
    place();
  }
  var dragHeader = panel.querySelector("header");
  dragHeader.addEventListener("pointerdown", function (event) {
    if (window.matchMedia("(min-width: 721px)").matches) return;
    if (event.target.closest("button")) return;
    var startY = event.clientY;
    function move(ev) {
      var dy = Math.max(0, ev.clientY - startY);
      panel.style.transform = "translateY(" + dy + "px)";
    }
    function up(ev) {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
      panel.style.transform = "";
      if (ev.clientY - startY > 72) open(false);
    }
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
  });
  fab.addEventListener("click", function () { open(true); });
  host.querySelector("[data-guide-close]").addEventListener("click", function () { open(false); fab.focus(); });
  document.addEventListener("sutra-guide-open", function () { open(true); });
  if (ls("sutra-guide-open") === "1" && window.matchMedia("(min-width: 721px)").matches) open(true);

  function say(text) {
    if (!voiceOn || !window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    var utter = new SpeechSynthesisUtterance(text);
    var saved = ls("sutra-voice");
    var voices = window.speechSynthesis.getVoices();
    var pick = voices.filter(function (voice) { return saved && voice.name === saved; })[0];
    if (!pick) {
      pick = voices.filter(function (voice) { return /natural|enhanced|premium/i.test(voice.name); })[0] || voices[0];
    }
    if (pick) utter.voice = pick;
    var rate = host.querySelector("[data-rate]");
    var pitch = host.querySelector("[data-pitch]");
    utter.rate = rate ? Number(rate.value) : 1;
    utter.pitch = pitch ? Number(pitch.value) : 1;
    speaking = true;
    utter.onend = function () { speaking = false; };
    window.speechSynthesis.speak(utter);
  }

  function paint(reply) {
    var text = reply.text || "";
    log.innerHTML = "<p>" + esc(text).replace(/\n/g, "<br>") + "</p>";
    var chips = (reply.chips || []).concat(reply.extraChips || []);
    cards.innerHTML = chips.map(function (chip) {
      return '<button type="button" data-chip="' + esc(chip) + '">' + esc(chip) + "</button>";
    }).join("");
    if (voiceOn) say(text);
  }

  function welcome() {
    log.innerHTML = "<p>Welcome to CypherMonkey Labs, I'm your Sūtra guide. I only repeat what is written in this app. If I don't know, I will say so.</p>";
    var items = [
      ["1-minute clip", "1-minute clip"],
      ["10-minute trailer", "10-minute trailer"],
      ["1-hour guided walk", "Start the 1-hour course"],
      ["Cheat codes", "cheat codes"],
      ["Quiz me", "Quiz me"],
      ["Teach me this room", "Teach me this room"],
      ["Games", "Play a game"],
      ["Mute me and just read", "Mute me and just read"]
    ];
    cards.innerHTML = items.map(function (item) {
      return '<button type="button" data-chip="' + esc(item[1]) + '">' + esc(item[0]) + "</button>";
    }).join("");
  }

  cards.addEventListener("click", function (event) {
    var btn = event.target.closest("[data-chip]");
    if (!btn || !guide) return;
    var chip = btn.getAttribute("data-chip");
    if (chip === "Mute me and just read") {
      voiceOn = false;
      if (window.speechSynthesis) window.speechSynthesis.cancel();
      host.querySelector(".voice-note").textContent = "Voice is off. You can read the answer on the page.";
      return;
    }
    if (chip === "1-minute clip" || chip === "10-minute trailer" || chip === "cheat codes") {
      var local = {
        "1-minute clip": "The 1-minute clip is a scripted read on the Listen page. It is not a video and there is no audio file.",
        "10-minute trailer": "The 10-minute trailer is a reading list on the Listen page. It is not a video.",
        "cheat codes": "Cheat sheets are study files on the Downloads page: pratyāhāra, counts, how to read a number, and the Kashmir notes. They are not a hidden mode."
      };
      var href = chip === "cheat codes" ? "downloads.html" : (chip === "1-minute clip" ? "listen.html#minute" : "listen.html#trailer");
      log.innerHTML = "<p>" + esc(local[chip]) + "</p><p><a href=\"" + href + "\">Open it</a></p>";
      return;
    }
    if (!guide) {
      ensureGuide().then(function () {
        if (!guide) return;
        var out = guide.route(chip, session, { page: page, room: document.body.dataset.room || "" });
        session = out.session;
        paint(out.reply);
      });
      return;
    }
    var out = guide.route(chip, session, { page: page, room: document.body.dataset.room || "" });
    session = out.session;
    paint(out.reply);
  });

  var voiceRow = host.querySelector(".voice-row");
  voiceRow.innerHTML = '<button type="button" data-voice>Voice off</button><label>Voice <select data-voice-pick><option value="">Browser default</option></select></label><label>Rate <input data-rate type="range" min="0.7" max="1.2" step="0.1" value="1"></label><label>Pitch <input data-pitch type="range" min="0.8" max="1.2" step="0.1" value="1"></label><button type="button" data-voice-stop>Stop</button>';
  host.querySelector(".voice-note").textContent = "Voice is off. Browser voices may mispronounce Sanskrit. This is a reading aid, not a recitation.";
  function fillVoices() {
    var select = host.querySelector("[data-voice-pick]");
    if (!window.speechSynthesis) return;
    var voices = window.speechSynthesis.getVoices();
    var ranked = voices.slice().sort(function (a, b) {
      function score(voice) { return (/natural/i.test(voice.name) ? 3 : 0) + (/enhanced|premium/i.test(voice.name) ? 2 : 0); }
      return score(b) - score(a);
    });
    select.innerHTML = '<option value="">Browser default</option>' + ranked.map(function (voice) {
      return '<option value="' + esc(voice.name) + '">' + esc(voice.name) + "</option>";
    }).join("");
  }
  if (window.speechSynthesis) {
    fillVoices();
    window.speechSynthesis.addEventListener("voiceschanged", fillVoices);
  }
  host.querySelector("[data-voice]").addEventListener("click", function () {
    voiceOn = !voiceOn;
    this.textContent = voiceOn ? "Voice on" : "Voice off";
    host.querySelector(".voice-note").textContent = voiceOn
      ? "Voice is on. Browser voices may mispronounce Sanskrit. This is a reading aid, not a recitation."
      : "Voice is off. Browser voices may mispronounce Sanskrit. This is a reading aid, not a recitation.";
  });
  host.querySelector("[data-voice-pick]").addEventListener("change", function (event) {
    ls("sutra-voice", event.target.value);
  });
  host.querySelector("[data-voice-stop]").addEventListener("click", function () {
    if (window.speechSynthesis) window.speechSynthesis.cancel();
    speaking = false;
  });

  welcome();
  if (ls("sutra-guide-open") === "1" && window.matchMedia("(min-width: 721px)").matches) ensureGuide();
  if (/[?&]guide=1(?:&|$)/.test(location.search)) open(true);
}
