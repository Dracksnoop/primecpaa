/* Prime CPA — interactions and motion. No dependencies. */
(function () {
  "use strict";

  var doc = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };

  /* ---------- Header: solid on scroll, hide on scroll down ---------- */
  var header = $(".site-header");
  var progress = $(".progress-bar span");
  var toTop = $(".to-top");
  var ring = toTop ? $(".ring circle", toTop) : null;
  var ringLen = ring ? 2 * Math.PI * 24 : 0;
  if (ring) { ring.style.strokeDasharray = ringLen; ring.style.strokeDashoffset = ringLen; }
  var lastY = window.scrollY;
  var ticking = false;

  function onScroll() {
    var y = window.scrollY;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    var pct = max > 0 ? y / max : 0;
    if (header) {
      header.classList.toggle("is-scrolled", y > 40);
      var menuOpen = doc.classList.contains("menu-open");
      header.classList.toggle("is-hidden", !menuOpen && y > 420 && y > lastY);
    }
    if (progress) progress.style.transform = "scaleX(" + pct + ")";
    if (toTop) {
      toTop.classList.toggle("is-visible", y > 800);
      if (ring) ring.style.strokeDashoffset = ringLen * (1 - pct);
    }
    lastY = y;
    ticking = false;
  }
  window.addEventListener("scroll", function () {
    if (!ticking) { window.requestAnimationFrame(onScroll); ticking = true; }
  }, { passive: true });
  onScroll();

  if (toTop) toTop.addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
  });

  /* ---------- Mobile menu ---------- */
  var toggle = $(".nav-toggle");
  var menu = $(".mobile-menu");
  function setMenu(open) {
    doc.classList.toggle("menu-open", open);
    if (toggle) toggle.setAttribute("aria-expanded", String(open));
    if (menu) menu.setAttribute("aria-hidden", String(!open));
    if (open) { var c = $(".mobile-menu__close"); if (c) setTimeout(function () { c.focus(); }, 350); }
    else if (toggle) toggle.focus();
  }
  if (toggle && menu) {
    toggle.addEventListener("click", function () { setMenu(true); });
    $$(".mobile-menu__close", menu).forEach(function (b) { b.addEventListener("click", function () { setMenu(false); }); });
    $$("a", menu).forEach(function (a) { a.addEventListener("click", function () { setMenu(false); }); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && doc.classList.contains("menu-open")) setMenu(false); });
  }

  /* ---------- Split headings into masked words ---------- */
  $$("[data-split]").forEach(function (el) {
    var words = el.textContent.trim().split(/\s+/);
    var em = el.querySelector("em");
    var emText = em ? em.textContent.trim().split(/\s+/) : [];
    var emStart = -1;
    if (emText.length) {
      for (var k = 0; k <= words.length - emText.length; k++) {
        if (words.slice(k, k + emText.length).join(" ") === emText.join(" ")) { emStart = k; break; }
      }
    }
    el.setAttribute("aria-label", el.textContent.trim().replace(/\s+/g, " "));
    el.innerHTML = words.map(function (w, i) {
      var inner = (emStart > -1 && i >= emStart && i < emStart + emText.length) ? "<em>" + w + "</em>" : w;
      inner = inner.replace(/&(?!amp;|lt;|gt;)/g, "&amp;");
      return '<span class="line" aria-hidden="true" style="display:inline-block;--i:' + i + '"><span>' + inner + "</span></span>";
    }).join(" ");
  });

  /* ---------- Reveal on scroll ---------- */
  var revealEls = $$("[data-reveal], [data-split], .why__item");
  if ("IntersectionObserver" in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add("is-visible"); io.unobserve(entry.target); }
      });
    // threshold 0 so very tall blocks (legal text, long articles) still reveal
    }, { rootMargin: "0px 0px -12% 0px", threshold: 0 });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add("is-visible"); });
  }

  /* Stagger children: [data-stagger] sets --d on its [data-reveal] children */
  $$("[data-stagger]").forEach(function (group) {
    var step = parseFloat(group.getAttribute("data-stagger")) || 0.1;
    $$("[data-reveal]", group).forEach(function (el, i) { el.style.setProperty("--d", (i * step).toFixed(2) + "s"); });
  });

  /* ---------- Parallax ---------- */
  var parallaxEls = $$("[data-parallax]");
  if (parallaxEls.length && !reduceMotion) {
    var pTick = false;
    var updateParallax = function () {
      var vh = window.innerHeight;
      parallaxEls.forEach(function (el) {
        var rect = el.parentElement.getBoundingClientRect();
        if (rect.bottom < -100 || rect.top > vh + 100) return;
        var speed = parseFloat(el.getAttribute("data-parallax")) || 0.12;
        var offset = (rect.top + rect.height / 2 - vh / 2) * -speed;
        el.style.translate = "0 " + offset.toFixed(1) + "px";
      });
      pTick = false;
    };
    window.addEventListener("scroll", function () {
      if (!pTick) { window.requestAnimationFrame(updateParallax); pTick = true; }
    }, { passive: true });
    window.addEventListener("resize", updateParallax);
    updateParallax();
  }

  /* ---------- Hero slider ---------- */
  var hero = $(".hero");
  if (hero) {
    var slides = $$(".hero__slide", hero);
    var dots = $$(".hero__dot", hero);
    var countEl = $(".hero__count b", hero);
    var delay = parseInt(hero.getAttribute("data-delay"), 10) || 7000;
    hero.style.setProperty("--hero-delay", delay + "ms");
    var current = 0;
    var timer = null;

    $$(".hero__title", hero).forEach(function (t) {
      var words = t.textContent.trim().split(/\s+/);
      t.setAttribute("aria-label", t.textContent.trim());
      t.innerHTML = words.map(function (w, i) {
        return '<span class="word" aria-hidden="true"><span style="transition-delay:' + (0.25 + i * 0.08).toFixed(2) + 's">' + w.replace(/&/g, "&amp;") + "</span></span>";
      }).join(" ");
    });

    var go = function (i) {
      var n = slides.length;
      i = (i + n) % n;
      slides[current].classList.remove("is-active");
      slides[current].setAttribute("aria-hidden", "true");
      current = i;
      slides[current].classList.add("is-active");
      slides[current].setAttribute("aria-hidden", "false");
      dots.forEach(function (d, j) {
        d.classList.remove("is-active");
        d.classList.toggle("is-done", j < current);
        d.setAttribute("aria-current", j === current ? "true" : "false");
      });
      // restart the progress animation
      if (dots[current]) { void dots[current].offsetWidth; dots[current].classList.add("is-active"); }
      if (countEl) countEl.textContent = String(current + 1).padStart(2, "0");
      schedule();
    };
    // Slides always advance every `delay` ms; clicking an arrow or dot restarts the count.
    var schedule = function () {
      clearTimeout(timer);
      timer = setTimeout(function () { go(current + 1); }, delay);
    };

    var prevBtn = $(".hero__arrow--prev", hero);
    var nextBtn = $(".hero__arrow--next", hero);
    if (prevBtn) prevBtn.addEventListener("click", function () { go(current - 1); });
    if (nextBtn) nextBtn.addEventListener("click", function () { go(current + 1); });
    dots.forEach(function (d, j) { d.addEventListener("click", function () { go(j); }); });

    document.addEventListener("visibilitychange", function () {
      if (document.hidden) clearTimeout(timer); else go(current);
    });
    hero.addEventListener("keydown", function (e) {
      if (e.key === "ArrowRight") go(current + 1);
      if (e.key === "ArrowLeft") go(current - 1);
    });
    var startX = null;
    hero.addEventListener("touchstart", function (e) { startX = e.touches[0].clientX; }, { passive: true });
    hero.addEventListener("touchend", function (e) {
      if (startX === null) return;
      var dx = e.changedTouches[0].clientX - startX;
      if (Math.abs(dx) > 50) go(current + (dx < 0 ? 1 : -1));
      startX = null;
    });

    // first slide: wait a frame so the entrance transition plays
    slides[0].classList.remove("is-active");
    requestAnimationFrame(function () { requestAnimationFrame(function () {
      slides[0].classList.add("is-active");
      if (dots[0]) dots[0].classList.add("is-active");
      schedule();
    }); });
  }

  /* ---------- Services explorer: gliding highlight + wipe panels ---------- */
  $$("[data-svx]").forEach(function (wrap) {
    var section = wrap.closest(".svx") || wrap;
    var list = $(".svx__list", wrap);
    var tabs = $$(".svx-tab", wrap);
    var slides = $$(".svx-slide", wrap);
    var indicator = $(".svx__indicator", wrap);
    var bar = $(".svx__bar", wrap);
    var stage = $(".svx__stage", wrap);
    var delay = 8000, idx = 0, timer = null, inView = false, hovering = false;
    section.style.setProperty("--svx-delay", delay + "ms");

    var placeIndicator = function () {
      var t = tabs[idx];
      if (!indicator || !t || !list.offsetParent) return;
      indicator.style.setProperty("--iy", t.offsetTop + "px");
      indicator.style.setProperty("--ih", t.offsetHeight + "px");
    };
    var runBar = function () {
      if (!bar) return;
      bar.classList.remove("is-running"); void bar.offsetWidth;
      if (inView && !hovering) bar.classList.add("is-running");
    };
    var schedule = function () {
      clearTimeout(timer);
      if (inView && !hovering) timer = setTimeout(function () { select(idx + 1); }, delay);
      runBar();
    };
    var select = function (i) {
      var n = tabs.length;
      i = (i + n) % n;
      if (i !== idx) {
        var out = slides[idx];
        out.classList.add("is-leaving");
        setTimeout(function () { out.classList.remove("is-leaving"); }, 1150);
      }
      idx = i;
      tabs.forEach(function (t, j) {
        var on = j === idx;
        t.classList.toggle("is-active", on);
        t.setAttribute("aria-selected", on ? "true" : "false");
        t.tabIndex = on ? 0 : -1;
      });
      slides.forEach(function (sl, j) { sl.classList.toggle("is-active", j === idx); });
      placeIndicator();
      schedule();
    };

    tabs.forEach(function (t, i) {
      t.addEventListener("click", function () { select(i); });
      t.addEventListener("keydown", function (e) {
        var k = e.key, j = null;
        if (k === "ArrowDown" || k === "ArrowRight") j = i + 1;
        if (k === "ArrowUp" || k === "ArrowLeft") j = i - 1;
        if (k === "Home") j = 0;
        if (k === "End") j = tabs.length - 1;
        if (j === null) return;
        e.preventDefault();
        select(j); tabs[idx].focus();
      });
    });

    // pause while the visitor reads the panel
    if (stage) {
      stage.addEventListener("mouseenter", function () { hovering = true; clearTimeout(timer); if (bar) bar.classList.remove("is-running"); });
      stage.addEventListener("mouseleave", function () { hovering = false; schedule(); });
    }
    window.addEventListener("resize", placeIndicator);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(placeIndicator);

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) {
        inView = en[0].isIntersecting;
        if (inView) { placeIndicator(); schedule(); } else { clearTimeout(timer); if (bar) bar.classList.remove("is-running"); }
      }, { threshold: 0.3 }).observe(wrap);
    } else { inView = true; schedule(); }

    placeIndicator();
  });

  /* ---------- Testimonials: stacked card deck ---------- */
  $$("[data-testimonials]").forEach(function (stage) {
    var section = stage.closest(".testimonials");
    var cards = $$(".tq-card", stage);
    var countEl = $(".tq__count b", section);
    var bar = $(".tq__progress", section);
    var prev = $("[data-prev]", section);
    var next = $("[data-next]", section);
    var delay = 6500, idx = 0, timer = null, inView = false;
    section.style.setProperty("--tq-delay", delay + "ms");
    if (cards.length < 2) { if (prev) prev.hidden = true; if (next) next.hidden = true; if (bar) bar.hidden = true; }

    var layout = function () {
      cards.forEach(function (c, j) {
        c.classList.toggle("is-active", j === idx);
        c.classList.toggle("is-next", cards.length > 1 && j === (idx + 1) % cards.length);
        c.setAttribute("aria-hidden", j === idx ? "false" : "true");
      });
      if (countEl) countEl.textContent = String(idx + 1).padStart(2, "0");
    };
    var restartBar = function () {
      if (!bar) return;
      bar.classList.remove("is-running"); void bar.offsetWidth;
      if (inView && cards.length > 1) bar.classList.add("is-running");
    };
    var schedule = function () {
      clearTimeout(timer);
      if (inView && cards.length > 1) timer = setTimeout(function () { go(idx + 1); }, delay);
      restartBar();
    };
    var go = function (i) {
      var n = cards.length;
      var leaving = cards[idx];
      leaving.style.removeProperty("--rx"); leaving.style.removeProperty("--ry");
      leaving.classList.add("is-leaving");
      setTimeout(function () { leaving.classList.remove("is-leaving"); }, 900);
      idx = (i + n) % n;
      layout();
      schedule();
    };
    if (prev) prev.addEventListener("click", function () { go(idx - 1); });
    if (next) next.addEventListener("click", function () { go(idx + 1); });

    // swipe on touch screens
    var sx = null;
    stage.addEventListener("touchstart", function (e) { sx = e.touches[0].clientX; }, { passive: true });
    stage.addEventListener("touchend", function (e) {
      if (sx === null) return;
      var dx = e.changedTouches[0].clientX - sx;
      if (Math.abs(dx) > 40) go(idx + (dx < 0 ? 1 : -1));
      sx = null;
    });

    // gentle 3D tilt and a light that follows the pointer (mouse only)
    if (!reduceMotion && window.matchMedia("(hover: hover)").matches) {
      stage.addEventListener("pointermove", function (e) {
        var c = cards[idx], r = c.getBoundingClientRect();
        var px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
        c.classList.add("is-tilting");
        c.style.setProperty("--ry", ((px - 0.5) * 8).toFixed(2) + "deg");
        c.style.setProperty("--rx", ((0.5 - py) * 6).toFixed(2) + "deg");
        c.style.setProperty("--mx", (px * 100).toFixed(1) + "%");
        c.style.setProperty("--my", (py * 100).toFixed(1) + "%");
      });
      stage.addEventListener("pointerleave", function () {
        var c = cards[idx];
        c.classList.remove("is-tilting");
        c.style.removeProperty("--rx"); c.style.removeProperty("--ry");
      });
    }

    // only rotate while the section is on screen, so visitors always start at the first review
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (en) {
        inView = en[0].isIntersecting;
        if (inView) schedule(); else { clearTimeout(timer); if (bar) bar.classList.remove("is-running"); }
      }, { threshold: 0.35 }).observe(section);
    } else { inView = true; schedule(); }

    layout();
  });

  /* ---------- FAQ: animate open / close ---------- */
  $$(".faq-item").forEach(function (item) {
    var summary = $("summary", item);
    var body = $(".faq-item__body", item);
    if (!summary || !body || reduceMotion || !body.animate) return;
    summary.addEventListener("click", function (e) {
      e.preventDefault();
      if (item.open) {
        var h = body.offsetHeight;
        var a = body.animate([{ height: h + "px", opacity: 1 }, { height: "0px", opacity: 0 }], { duration: 450, easing: "cubic-bezier(0.65,0,0.35,1)" });
        a.onfinish = function () { item.open = false; };
      } else {
        item.open = true;
        var full = body.offsetHeight;
        body.animate([{ height: "0px", opacity: 0 }, { height: full + "px", opacity: 1 }], { duration: 550, easing: "cubic-bezier(0.16,1,0.3,1)" });
      }
    });
  });

  /* ---------- State refund tracker: choosing a state opens its refund page ---------- */
  var stateSel = $("#state-select");
  if (stateSel) {
    stateSel.addEventListener("change", function () {
      var url = stateSel.value;
      if (url) window.open(url, "_blank", "noopener");
    });
  }

  /* ---------- Forms ----------
     Submission is wired up by CountingWorks on deployment. Until then the
     forms validate in the browser and do not post anywhere. */
  $$("form[data-cw-form]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      if (!form.getAttribute("action")) e.preventDefault();
    });
  });
})();
