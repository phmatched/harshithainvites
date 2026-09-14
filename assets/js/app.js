/* ============================================================================
 *  Renders the invitation from the details in data.js.
 *
 *  You normally never need to edit this file — change assets/js/data.js instead.
 * ========================================================================= */

(function () {
  "use strict";

  var D = window.INVITE || (typeof INVITE !== "undefined" ? INVITE : null);

  var $ = function (id) { return document.getElementById(id); };

  /* Write text into an element, if the element exists. */
  function put(id, text) {
    var el = $(id);
    if (el && text != null) el.textContent = text;
  }

  /* Escape values before they go anywhere near innerHTML. */
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  /* Swap {bride} / {groom} placeholders in the wording. */
  function fill(tpl) {
    if (!tpl) return "";
    return String(tpl)
      .replace(/\{bride\}/g, D.bride.name)
      .replace(/\{groom\}/g, D.groom.name);
  }


  /* ==========================================================================
     1. ENVELOPE  — wired first, so a later error can never trap the reader
     ======================================================================= */

  var overlay = $("envelope");
  var envBtn = $("env-open");
  var opened = false;

  function openEnvelope() {
    if (opened || !envBtn || !overlay) return;
    opened = true;

    envBtn.classList.add("is-open");
    envBtn.setAttribute("aria-expanded", "true");

    // Let the flap and card animation play before clearing the screen.
    setTimeout(function () {
      overlay.classList.add("is-gone");
      document.body.classList.remove("is-locked");

      // Move keyboard focus into the invitation now the envelope is gone.
      var hero = document.querySelector(".hero__inner");
      if (hero) {
        hero.setAttribute("tabindex", "-1");
        hero.focus({ preventScroll: true });
      }
    }, 1500);

    startMusic();
  }

  if (envBtn && overlay) {
    document.body.classList.add("is-locked");
    envBtn.addEventListener("click", openEnvelope);
    overlay.addEventListener("click", function (e) {
      if (e.target === overlay || e.target.classList.contains("envelope__inner")) openEnvelope();
    });
  }


  /* ==========================================================================
     2. BACKGROUND MUSIC  (off unless switched on in data.js)
     ======================================================================= */

  var audio = null;

  function setupMusic() {
    if (!D || !D.music || !D.music.enabled || !D.music.file) return;

    var toggle = $("music-toggle");
    if (!toggle) return;

    audio = new Audio(D.music.file);
    audio.loop = true;
    audio.volume = 0.35;
    toggle.hidden = false;

    toggle.addEventListener("click", function () {
      if (audio.paused) { audio.play().catch(function () {}); }
      else { audio.pause(); }
      syncMusicIcon();
    });
  }

  function syncMusicIcon() {
    var toggle = $("music-toggle");
    var use = toggle && toggle.querySelector("use");
    if (!use || !audio) return;
    var playing = !audio.paused;
    use.setAttribute("href", playing ? "#i-sound-on" : "#i-sound-off");
    toggle.setAttribute("aria-label", playing ? "Mute background music" : "Unmute background music");
  }

  function startMusic() {
    if (!audio) return;
    audio.play().then(syncMusicIcon).catch(function () { syncMusicIcon(); });
  }


  /* ==========================================================================
     3. DATES  — helpers for the countdown and the calendar files
     ======================================================================= */

  function muhurtaDate() {
    var d = new Date(D.muhurta);
    return isNaN(d.getTime()) ? null : d;
  }

  /* "20261206T054500Z" — the format calendars expect (always UTC). */
  function toICSStamp(date) {
    return date.toISOString().replace(/[-:]/g, "").replace(/\.\d{3}/, "");
  }

  function endDate(start) {
    var hours = Number(D.muhurtaDurationHours) || 3;
    return new Date(start.getTime() + hours * 3600 * 1000);
  }

  function eventTitle() {
    return D.bride.name + " & " + D.groom.name + " — Wedding";
  }

  /* "Sunday, 6 December 2026  ·  11:15 AM" — the time comes from the muhurta
     itself, formatted in IST, so it cannot drift from the countdown. */
  function whenLine() {
    var t = muhurtaDate();
    if (!t) return D.dateLine || "";
    var time = "";
    try {
      time = new Intl.DateTimeFormat("en-IN", {
        hour: "numeric", minute: "2-digit", hour12: true, timeZone: "Asia/Kolkata"
      }).format(t).toUpperCase();
    } catch (e) { time = ""; }
    return time ? (D.dateLine + "  \u00b7  " + time) : (D.dateLine || "");
  }


  function venueOneLine() {
    var v = D.venue || {};
    return [v.name].concat(v.addressLines || []).filter(Boolean).join(", ");
  }


  /* ==========================================================================
     4. RENDER EVERYTHING
     ======================================================================= */

  function render() {
    var b = D.bride, g = D.groom, w = D.words || {}, v = D.venue || {};

    /* --- browser tab title (the og: share tags are static in index.html,
           because social crawlers don't run JavaScript) --- */
    document.title = eventTitle() + " Invitation";

    /* --- envelope --- */
    put("env-aamantrana", w.aamantrana);
    put("env-cue", w.envelopeCue);
    put("env-card-names", b.name + " & " + g.name);
    put("env-card-date", D.dateLine);
    put("env-seal", b.initial + " & " + g.initial);

    /* --- hero --- */
    put("invocation", w.invocation);
    put("hero-intro", w.heroIntro);
    put("hero-bride", b.name);
    put("hero-groom", g.name);
    if (b.kannadaName && g.kannadaName) {
      put("hero-kn-names", b.kannadaName + " — " + g.kannadaName);
    }
    put("hero-date", D.dateLine);
    put("hero-venue", v.short || venueOneLine());

    /* --- invitation --- */
    put("inv-heading", w.invitationHeading);
    put("inv-body", fill(w.invitationBody));
    put("inv-blessing", w.blessingLine);

    put("cd-when", whenLine());

    /* --- families --- */
    put("fam-bride-parents", b.parents);
    put("fam-bride-grand", b.grandparents);
    put("fam-bride-place", b.place);
    put("fam-groom-parents", g.parents);
    put("fam-groom-grand", g.grandparents);
    put("fam-groom-place", g.place);

    /* --- events timeline --- */
    renderEvents();

    /* --- venue --- */
    put("venue-name", v.name);
    var addr = $("venue-addr");
    if (addr) addr.innerHTML = (v.addressLines || []).map(esc).join("<br>");

    var q = encodeURIComponent(v.mapsQuery || venueOneLine());
    var map = $("venue-map");
    if (map) map.src = "https://maps.google.com/maps?q=" + q + "&z=15&output=embed";
    var dir = $("btn-directions");
    if (dir) dir.href = "https://www.google.com/maps/dir/?api=1&destination=" + q;

    /* --- closing --- */
    put("closing-heading", w.closingHeading);
    put("closing-body", w.closingBody);
    put("closing-families", w.closingFamilies);
  }


  /* --- the events timeline ------------------------------------------------ */

  var ICONS = {
    turmeric: "i-turmeric",
    mehendi:  "i-mehendi",
    dhare:    "i-dhare",
    lamp:     "i-lamp",
    betel:    "i-betel",
    mallige:  "i-mallige",
  };

  function renderEvents() {
    var list = $("timeline");
    if (!list || !D.events) return;

    /* Only let colours from data.js through — they go into a style attribute. */
    function colour(v, fallback) {
      return /^#[0-9a-fA-F]{3,8}$/.test(String(v || "")) ? v : fallback;
    }

    function row(label, value) {
      return value ? "<div><dt>" + label + "</dt><dd>" + esc(value) + "</dd></div>" : "";
    }

    /* Scene names map to files we ship — never interpolate a raw value. */
    var SCENES = { haldi: 1, mehendi: 1, dhare: 1, lamp: 1 };

    /* A custom picture may only be a plain relative path to an image. */
    function imagePath(v) {
      v = String(v || "");
      return /^[A-Za-z0-9._\-\/]+\.(png|jpe?g|webp|avif|svg)$/.test(v) && v.indexOf("..") === -1
        ? v : "";
    }

    /* The card's picture: either a supplied image, or the layered artwork. */
    function artwork(e) {
      var custom = imagePath(e.image);
      if (custom) {
        return '<img class="ev__photo" src="' + esc(custom) + '" alt="" aria-hidden="true" loading="lazy">';
      }
      var scene = SCENES[e.scene] ? e.scene : "dhare";
      return '' +
        '<img class="ev__toran" src="assets/img/toran.svg" alt="" loading="lazy">' +
        '<img class="ev__strand ev__strand--l" src="assets/img/garland-side.svg" alt="" loading="lazy">' +
        '<img class="ev__strand ev__strand--r" src="assets/img/garland-side.svg" alt="" loading="lazy">' +
        '<img class="ev__scene" src="assets/img/scene-' + scene + '.png" alt="" loading="lazy">';
    }

    list.innerHTML = D.events.map(function (e) {
      var icon = ICONS[e.icon] || "i-mallige";
      var style = "--accent:" + colour(e.accent, "#7C1F1A") +
                  ";--accent-deep:" + colour(e.accentDeep, "#4E1010");

      return '' +
        '<li class="ev' + (e.highlight ? " ev--highlight" : "") + '" style="' + style + '">' +
          '<article class="ev__card">' +
            '<div class="ev__art" aria-hidden="true">' + artwork(e) + "</div>" +
            '<div class="ev__text">' +
              '<svg class="ev__motif" aria-hidden="true"><use href="#' + icon + '"/></svg>' +
              (e.kannadaName ? '<p class="ev__kn kn">' + esc(e.kannadaName) + "</p>" : "") +
              '<h3 class="ev__name">' + esc(e.name) + "</h3>" +
              (e.note ? '<p class="ev__note">' + esc(e.note) + "</p>" : "") +
              '<span class="ev__rule"></span>' +
              '<dl class="ev__meta">' +
                row("Date", e.date) + row("Time", e.time) + row("Venue", e.venue) +
              "</dl>" +
              (e.attire ? '<span class="ev__attire">' + esc(e.attire) + "</span>" : "") +
            "</div>" +
          "</article>" +
        "</li>";
    }).join("");
  }


  /* ==========================================================================
     5. COUNTDOWN
     ======================================================================= */

  function setupCountdown() {
    var target = muhurtaDate();
    var grid = $("cd-grid");
    var done = $("cd-done");
    if (!target || !grid) return;

    var pad = function (n) { return n < 10 ? "0" + n : String(n); };

    function tick() {
      var diff = target.getTime() - Date.now();

      if (diff <= 0) {
        revealScratch();
        grid.hidden = true;
        if (done) {
          done.hidden = false;
          done.textContent = "Today we celebrate — thank you for being with us.";
        }
        var sub = $("countdown-sub");
        if (sub) sub.textContent = "";
        clearInterval(timer);
        return;
      }

      var s = Math.floor(diff / 1000);
      put("cd-days",  String(Math.floor(s / 86400)));
      put("cd-hours", pad(Math.floor(s / 3600) % 24));
      put("cd-mins",  pad(Math.floor(s / 60) % 60));
      put("cd-secs",  pad(s % 60));
    }

    tick();
    var timer = setInterval(tick, 1000);
  }


  /* ==========================================================================
     5b. SCRATCH TO REVEAL  — gold foil over the countdown
     ======================================================================= */

  var revealScratch = function () {};   // replaced once the foil exists

  function setupScratch() {
    var wrap = $("scratch");
    var canvas = $("scratch-foil");
    var skip = $("scratch-skip");
    if (!wrap || !canvas || !canvas.getContext) return;   // no canvas: stays revealed

    // Nothing to hide if the day has already come and gone.
    var target = muhurtaDate();
    if (!target || target.getTime() <= Date.now()) return;

    var ctx = canvas.getContext("2d");
    if (!ctx) return;

    var dpr = Math.min(window.devicePixelRatio || 1, 2);
    var COLS = 30, ROWS = 12;
    var cells, filled, done = false;
    var cssW = 0, cssH = 0, lastW = 0;

    function reset() {
      cells = new Uint8Array(COLS * ROWS);
      filled = 0;
    }

    function reveal() {
      if (done) return;
      done = true;
      wrap.classList.add("is-done");
      canvas.setAttribute("aria-hidden", "true");
      if (skip) skip.hidden = true;
    }
    revealScratch = reveal;

    /* ---- painting the foil ---- */
    function coin(x, y, r) {
      ctx.save();
      ctx.strokeStyle = "rgba(78,16,16,.55)";
      ctx.fillStyle = "rgba(78,16,16,.16)";
      ctx.lineWidth = Math.max(1, r * .13);
      ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      ctx.beginPath(); ctx.arc(x, y, r * .58, 0, Math.PI * 2); ctx.stroke();
      for (var i = 0; i < 12; i++) {
        var a = i / 12 * Math.PI * 2;
        ctx.beginPath();
        ctx.moveTo(x + Math.cos(a) * r * .70, y + Math.sin(a) * r * .70);
        ctx.lineTo(x + Math.cos(a) * r * .90, y + Math.sin(a) * r * .90);
        ctx.stroke();
      }
      ctx.restore();
    }

    function paint() {
      var rect = wrap.getBoundingClientRect();
      cssW = Math.max(1, Math.round(rect.width));
      cssH = Math.max(1, Math.round(rect.height));
      canvas.width = Math.round(cssW * dpr);
      canvas.height = Math.round(cssH * dpr);
      canvas.style.width = cssW + "px";
      canvas.style.height = cssH + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.globalCompositeOperation = "source-over";

      var g = ctx.createLinearGradient(0, 0, cssW, cssH);
      g.addColorStop(0,   "#9A711A");
      g.addColorStop(.20, "#C9A227");
      g.addColorStop(.44, "#F2E4BE");
      g.addColorStop(.58, "#E3CC8A");
      g.addColorStop(.80, "#C9A227");
      g.addColorStop(1,   "#8E6716");
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, cssW, cssH);

      // brushed-metal streaks
      ctx.globalAlpha = .10;
      for (var i = 0; i < 170; i++) {
        ctx.strokeStyle = i % 2 ? "#FFF6DC" : "#7E5B12";
        ctx.lineWidth = Math.random() * 1.6 + .3;
        var y = Math.random() * cssH;
        ctx.beginPath();
        ctx.moveTo(-20, y);
        ctx.lineTo(cssW + 20, y + (Math.random() * 12 - 6));
        ctx.stroke();
      }
      ctx.globalAlpha = 1;

      // the hint
      var fs = Math.max(10, Math.min(15, cssW * .026));
      coin(cssW / 2, cssH / 2 - fs * 1.5, fs * 1.4);
      ctx.fillStyle = "rgba(78,16,16,.72)";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      try { ctx.letterSpacing = "0.22em"; } catch (e) { /* older browsers */ }
      ctx.font = '600 ' + fs + 'px "Cinzel", Georgia, serif';
      ctx.fillText("SCRATCH TO REVEAL", cssW / 2, cssH / 2 + fs * 1.4);
      try { ctx.letterSpacing = "0px"; } catch (e) {}
    }

    /* ---- scratching ---- */
    /* Mark every cell the brush actually covers. Counting only the centre
       line made progress lag the visible scratching by about four times. */
    function mark(x, y, rad) {
      var cw = cssW / COLS, ch = cssH / ROWS;
      var c0 = Math.max(0, Math.floor((x - rad) / cw));
      var c1 = Math.min(COLS - 1, Math.floor((x + rad) / cw));
      var r0 = Math.max(0, Math.floor((y - rad) / ch));
      var r1 = Math.min(ROWS - 1, Math.floor((y + rad) / ch));
      for (var r = r0; r <= r1; r++) {
        for (var c = c0; c <= c1; c++) {
          var i = r * COLS + c;
          if (!cells[i]) { cells[i] = 1; filled++; }
        }
      }
    }

    var prev = null;

    function scratch(x, y) {
      var brush = Math.max(24, cssW * .075);
      ctx.globalCompositeOperation = "destination-out";
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.lineWidth = brush;
      ctx.beginPath();
      if (prev) ctx.moveTo(prev.x, prev.y); else ctx.moveTo(x - 0.01, y);
      ctx.lineTo(x, y);
      ctx.stroke();
      ctx.globalCompositeOperation = "source-over";

      // mark the grid cells along the stroke, so progress needs real coverage
      var from = prev || { x: x, y: y };
      var steps = Math.max(1, Math.ceil(Math.hypot(x - from.x, y - from.y) / 8));
      for (var s = 0; s <= steps; s++) {
        mark(from.x + (x - from.x) * s / steps,
             from.y + (y - from.y) * s / steps, brush / 2);
      }
      prev = { x: x, y: y };

      if (filled / (COLS * ROWS) >= 0.45) reveal();
    }

    function local(e) {
      var r = canvas.getBoundingClientRect();
      return { x: e.clientX - r.left, y: e.clientY - r.top };
    }

    var drawing = false;

    canvas.addEventListener("pointerdown", function (e) {
      if (done) return;
      drawing = true;
      prev = null;
      try { canvas.setPointerCapture(e.pointerId); } catch (err) {}
      var p = local(e);
      scratch(p.x, p.y);
      e.preventDefault();
    });

    canvas.addEventListener("pointermove", function (e) {
      if (!drawing || done) return;
      var p = local(e);
      scratch(p.x, p.y);
      e.preventDefault();
    });

    function stop() { drawing = false; prev = null; }
    canvas.addEventListener("pointerup", stop);
    canvas.addEventListener("pointercancel", stop);

    if (skip) {
      skip.hidden = false;
      skip.addEventListener("click", reveal);
    }

    /* ---- go ---- */
    function build() {
      reset();
      paint();
      lastW = cssW;
      wrap.classList.add("is-armed");
    }

    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(build, build);   // so Cinzel is available
    } else {
      build();
    }

    // Re-paint on a real width change (rotation). Scratching restarts, which is
    // why we only do it when the width actually moved.
    window.addEventListener("resize", function () {
      if (done) return;
      var w = Math.round(wrap.getBoundingClientRect().width);
      if (Math.abs(w - lastW) < 2) return;
      lastW = w;
      build();
    });
  }


  /* ==========================================================================
     6. ADD TO CALENDAR
     ======================================================================= */

  function setupCalendar() {
    var start = muhurtaDate();
    if (!start) return;
    var end = endDate(start);
    var title = eventTitle();
    var where = venueOneLine();
    var details = (D.words && D.words.blessingLine) || "";

    /* Google Calendar */
    var gcal = $("btn-gcal");
    if (gcal) {
      gcal.href = "https://calendar.google.com/calendar/render?action=TEMPLATE" +
        "&text=" + encodeURIComponent(title) +
        "&dates=" + toICSStamp(start) + "/" + toICSStamp(end) +
        "&details=" + encodeURIComponent(details) +
        "&location=" + encodeURIComponent(where);
    }

    /* .ics download — works in Apple Calendar, Outlook, everything else */
    var icsBtn = $("btn-ics");
    if (icsBtn) {
      icsBtn.addEventListener("click", function () {
        var esc2 = function (t) {
          return String(t).replace(/\\/g, "\\\\").replace(/;/g, "\\;")
                          .replace(/,/g, "\\,").replace(/\n/g, "\\n");
        };
        var ics = [
          "BEGIN:VCALENDAR",
          "VERSION:2.0",
          "PRODID:-//Wedding Invitation//EN",
          "CALSCALE:GREGORIAN",
          "BEGIN:VEVENT",
          "UID:" + Date.now() + "@wedding-invite",
          "DTSTAMP:" + toICSStamp(new Date()),
          "DTSTART:" + toICSStamp(start),
          "DTEND:" + toICSStamp(end),
          "SUMMARY:" + esc2(title),
          "DESCRIPTION:" + esc2(details),
          "LOCATION:" + esc2(where),
          "END:VEVENT",
          "END:VCALENDAR",
        ].join("\r\n");

        var blob = new Blob([ics], { type: "text/calendar;charset=utf-8" });
        var url = URL.createObjectURL(blob);
        var a = document.createElement("a");
        a.href = url;
        a.download = title.replace(/[^\w]+/g, "-").replace(/^-|-$/g, "") + ".ics";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
      });
    }
  }


  /* ==========================================================================
     7. SCROLL REVEAL
     ======================================================================= */

  function setupReveal() {
    var items = document.querySelectorAll(".reveal");

    if (!("IntersectionObserver" in window)) {
      for (var i = 0; i < items.length; i++) items[i].classList.add("is-in");
      return;
    }

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });

    items.forEach(function (el) { io.observe(el); });
  }

  /* If anything above goes wrong, make sure nothing stays invisible. */
  function revealAll() {
    document.querySelectorAll(".reveal").forEach(function (el) {
      el.classList.add("is-in");
    });
  }


  /* ==========================================================================
     GO
     ======================================================================= */

  if (!D) {
    console.error("data.js did not load — check assets/js/data.js for a typo.");
    revealAll();
    return;
  }

  try {
    render();
    setupMusic();
    setupCountdown();
    setupScratch();
    setupCalendar();
    setupReveal();
  } catch (err) {
    console.error("Invitation failed to render:", err);
    revealAll();
  }

})();
