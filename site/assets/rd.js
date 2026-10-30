(function () {
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return [].slice.call((r || document).querySelectorAll(s)); };
  var store = {
    get: function (k) { try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} }
  };

  /* phone menu */
  var menu = $('#menu');
  if (menu) {
    var openBtn = $('#menu-open'), closeBtn = $('#menu-close');
    var setOpen = function (on) {
      menu.classList.toggle('open', on);
      openBtn.setAttribute('aria-expanded', on ? 'true' : 'false');
      document.body.style.overflow = on ? 'hidden' : '';
      if (on) closeBtn.focus(); else openBtn.focus();
    };
    openBtn.addEventListener('click', function () { setOpen(true); });
    closeBtn.addEventListener('click', function () { setOpen(false); });
    $$('.menu .row button').forEach(function (b) {
      b.addEventListener('click', function () {
        var li = b.closest('li'), on = !li.classList.contains('op');
        li.classList.toggle('op', on); b.setAttribute('aria-expanded', on ? 'true' : 'false'); b.textContent = on ? '−' : '+';
      });
    });
    $$('.menu a').forEach(function (a) { a.addEventListener('click', function () { setOpen(false); }); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && menu.classList.contains('open')) setOpen(false); });
  }

  /* reveal on scroll */
  var rv = $$('.rv');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }); }, { rootMargin: '0px 0px -8% 0px' });
    rv.forEach(function (el) { io.observe(el); });
  } else rv.forEach(function (el) { el.classList.add('in'); });

  /* alumni quotes: one at a time, 5 seconds each, loops */
  var qs = $$('.quote');
  if (qs.length > 1) {
    var qi = Math.floor(Math.random() * qs.length);
    qs.forEach(function (q, i) { q.classList.toggle('on', i === qi); });
    setInterval(function () { if (document.hidden) return; qs[qi].classList.remove('on'); qi = (qi + 1) % qs.length; qs[qi].classList.add('on'); }, 5000);
  }

  /* home pillars on computers: photo tiles, wording opens under the clicked row */
  var tiles = $$('.pt-tile'), ptp = $('#pt-panel');
  tiles.forEach(function (b) {
    b.addEventListener('click', function () {
      var k = +b.getAttribute('data-pd'), on = b.getAttribute('aria-expanded') !== 'true';
      tiles.forEach(function (x) { x.setAttribute('aria-expanded', x === b && on ? 'true' : 'false'); });
      ptp.hidden = !on;
      if (on) {
        ptp.classList.toggle('row2', k >= 3);
        ptp.style.setProperty('--px', ((k % 3) * 2 + 1) / 6 * 100 + '%');
        $$('.pt-tx', ptp).forEach(function (t) { t.hidden = +t.getAttribute('data-pd') !== k; });
      }
    });
  });

  /* home pillars: read more on phones */
  $$('.readmore').forEach(function (b) {
    b.addEventListener('click', function () {
      var tx = b.closest('.txt'), on = !tx.classList.contains('open');
      tx.classList.toggle('open', on); b.textContent = on ? 'Show less' : 'Read more';
    });
  });

  /* pillars: only one open at a time */
  var pils = $$('.pil');
  pils.forEach(function (d) { d.addEventListener('toggle', function () { if (d.open) pils.forEach(function (o) { if (o !== d) o.open = false; }); }); });

  /* slideshows: endless loop, no controls (1 photo on phones, 3 on computers) */
  $$('.slider .gallery').forEach(function (gal) {
    var real = $$('button', gal), n = real.length; if (n < 2) return;
    for (var k = 0; k < Math.min(3, n); k++) { var cl = real[k].cloneNode(true); cl.classList.add('clone'); cl.setAttribute('aria-hidden', 'true'); cl.tabIndex = -1; gal.appendChild(cl); }
    var auto, settle;
    var step = function () { return real[1].offsetLeft - real[0].offsetLeft; };
    var cur = function () { return Math.round(gal.scrollLeft / step()); };
    var next = function () { gal.scrollTo({ left: (cur() + 1) * step(), behavior: 'smooth' }); };
    gal.addEventListener('scroll', function () {
      clearTimeout(settle);
      settle = setTimeout(function () { if (desk.matches) return; var c = cur(); if (c >= n) { gal.style.scrollSnapType = 'none'; gal.scrollLeft = (c - n) * step(); gal.offsetHeight; gal.style.scrollSnapType = ''; } }, 120);
    }, { passive: true });
    var desk = window.matchMedia('(min-width:821px)'), hover = false, last = 0, pos = null;
    var flow = function (t) {
      if (desk.matches && !hover && !document.hidden) {
        var dt = last ? Math.min(t - last, 50) : 16;
        if (pos === null) pos = gal.scrollLeft;
        pos += dt * 0.04;
        if (pos >= n * step()) pos -= n * step();
        gal.scrollLeft = pos;
      } else pos = null;
      last = t; requestAnimationFrame(flow);
    };
    requestAnimationFrame(flow);
    var restart = function () { clearInterval(auto); auto = setInterval(function () { if (!document.hidden && !desk.matches) next(); }, 4000); };
    gal.addEventListener('touchstart', function () { clearInterval(auto); }, { passive: true });
    gal.addEventListener('touchend', restart, { passive: true });
    restart();
  });

  /* team filters + bio dialog */
  var fbtns = $$('[data-filter]');
  if (fbtns.length) {
    fbtns.forEach(function (b) {
      b.addEventListener('click', function () {
        var f = b.getAttribute('data-filter');
        fbtns.forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        $$('.person').forEach(function (p) { p.classList.toggle('hide', f !== 'all' && p.getAttribute('data-group') !== f); });
        $$('.letter').forEach(function (l) {
          var any = false, n = l.nextElementSibling;
          while (n && !n.classList.contains('letter')) { if (!n.classList.contains('hide')) any = true; n = n.nextElementSibling; }
          l.classList.toggle('hide', !any);
        });
      });
    });
  }
  var dlg = $('#bio');
  if (dlg) {
    $$('.person').forEach(function (p) {
      p.addEventListener('click', function () {
        $('#bio-img').src = p.getAttribute('data-img') || '';
        $('#bio-img').alt = p.getAttribute('data-name');
        $('#bio-ph').style.display = p.getAttribute('data-img') ? '' : 'none';
        $('#bio-name').textContent = p.getAttribute('data-name');
        $('#bio-text').textContent = p.getAttribute('data-bio');
        dlg.showModal();
      });
    });
    $('#bio-x').addEventListener('click', function () { dlg.close(); });
    dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
  }

  /* schedule day tabs (phone) */
  var dayBtns = $$('.days button');
  if (dayBtns.length) {
    var showDay = function (d) {
      dayBtns.forEach(function (b) { b.setAttribute('aria-selected', b.getAttribute('data-day') === d ? 'true' : 'false'); });
      $$('.daylist').forEach(function (l) { l.hidden = l.getAttribute('data-day') !== d; });
    };
    dayBtns.forEach(function (b) { b.addEventListener('click', function () { showDay(b.getAttribute('data-day')); }); });
    showDay('sun');
  }
  var evMore = $('#ev-more');
  if (evMore) evMore.addEventListener('click', function () {
    var ul = $('.events'), on = !ul.classList.contains('all');
    ul.classList.toggle('all', on); evMore.textContent = on ? 'Show fewer' : 'Show all events';
  });

  /* photo lightbox */
  var lb = $('#lb');
  if (lb) {
    var pics = $$('.gallery button:not(.clone)'), at = 0;
    var put = function (i) { at = (i + pics.length) % pics.length; var im = pics[at].querySelector('img'); $('#lb-img').src = im.getAttribute('data-full') || im.src; $('#lb-img').alt = im.alt; };
    pics.forEach(function (b, i) { b.addEventListener('click', function () { put(i); lb.showModal(); }); });
    $$('.gallery button.clone').forEach(function (b) { var src = b.querySelector('img').getAttribute('src'); b.addEventListener('click', function () { var i = 0; pics.forEach(function (p, j) { if (p.querySelector('img').getAttribute('src') === src) i = j; }); put(i); lb.showModal(); }); });
    $('#lb-prev').addEventListener('click', function () { put(at - 1); });
    $('#lb-next').addEventListener('click', function () { put(at + 1); });
    $('#lb-x').addEventListener('click', function () { lb.close(); });
    lb.addEventListener('click', function (e) { if (e.target === lb) lb.close(); });
    lb.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight') put(at + 1); if (e.key === 'ArrowLeft') put(at - 1); });
    var x0 = null;
    lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', function (e) { if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null; if (Math.abs(dx) > 40) put(at + (dx < 0 ? 1 : -1)); });
  }

  /* before-you-fly checklist (remembered on this device) */
  var checks = $$('.check input');
  if (checks.length) {
    var saved = store.get('moreshet-checklist') || {};
    var upd = function () {
      var n = 0;
      checks.forEach(function (c) { c.closest('.check').classList.toggle('done', c.checked); if (c.checked) n++; });
      $('#prog-n').textContent = n + ' of ' + checks.length + ' done';
      $('#prog-bar').style.width = Math.round(n / checks.length * 100) + '%';
    };
    checks.forEach(function (c) {
      c.checked = !!saved[c.id];
      c.addEventListener('change', function () { saved[c.id] = c.checked; store.set('moreshet-checklist', saved); upd(); });
    });
    upd();
  }

  /* FAQ: one answer open at a time; open the one a link points to */
  var fds = $$('.faq details');
  fds.forEach(function (d) { d.addEventListener('toggle', function () { if (d.open) fds.forEach(function (o) { if (o !== d) o.open = false; }); }); });
  var openHash = function () {
    var id = decodeURIComponent(location.hash.slice(1)); if (!id) return;
    var t = document.getElementById(id); if (t && t.tagName === 'DETAILS') { t.open = true; setTimeout(function () { t.scrollIntoView({ block: 'start' }); }, 50); }
  };
  openHash(); window.addEventListener('hashchange', openHash);

  /* FAQ search + topic filter */
  var fq = $('#faq-q');
  if (fq) {
    var topic = 'all';
    var run = function () {
      var q = fq.value.trim().toLowerCase(), shown = 0;
      $$('.faq [data-cat]').forEach(function (sec) {
        var any = false;
        $$('details', sec).forEach(function (d) {
          var ok = (topic === 'all' || topic === sec.getAttribute('data-cat')) && (!q || d.textContent.toLowerCase().indexOf(q) >= 0);
          d.hidden = !ok; if (ok) { any = true; shown++; if (q) d.open = true; }
        });
        sec.hidden = !any;
      });
      $('#faq-none').hidden = shown > 0;
    };
    fq.addEventListener('input', run);
    $$('[data-topic]').forEach(function (b) {
      b.addEventListener('click', function () {
        topic = b.getAttribute('data-topic');
        $$('[data-topic]').forEach(function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        run();
      });
    });
  }
})();
