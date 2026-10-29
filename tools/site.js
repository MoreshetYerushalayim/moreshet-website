/* Replaces the bits of Wix's runtime this site actually uses:
   pop-ups (teacher bios + Instagram posts), phone menu, alumni slideshow,
   photo galleries (scroll arrows + full-screen viewer). */
(function () {
  var doc = document, body = doc.body;
  var $$ = function (sel, root) { return [].slice.call((root || doc).querySelectorAll(sel)); };
  var lock = function (on) { body.classList.toggle('siteScrollingBlockedIOSFix', !!on); };

  /* ---------- entrance animations (fade/glide/blur... in as you scroll, like Wix) ---------- */
  function playMotion(el) {
    el.style.animationPlayState = 'running';
    var done = function () { el.setAttribute('data-motion-enter', 'done'); el.style.animationPlayState = ''; };
    el.addEventListener('animationend', done, { once: true });
    setTimeout(done, 4000);
  }
  function armMotion(root, now) {
    var els = $$('[id^="comp-"]', root).filter(function (el) {
      if (el.getAttribute('data-motion-enter') === 'done') return false;
      var c = getComputedStyle(el);
      return c.animationName && c.animationName !== 'none' && c.animationPlayState.indexOf('paused') >= 0;
    });
    if (now || !('IntersectionObserver' in window)) { els.forEach(playMotion); return; }
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (en) { if (en.isIntersecting) { io.unobserve(en.target); playMotion(en.target); } });
    }, { threshold: 0.01 });
    els.forEach(function (el) { io.observe(el); });
  }
  armMotion(doc, false);

  /* ---------- pop-ups ---------- */
  var tpls = { popup: {}, insta: {} };
  $$('template.site-popup').forEach(function (t) { tpls[t.dataset.popupGroup][+t.dataset.popupIndex] = t; });
  var openRoot = null;
  function closePopup() {
    if (!openRoot) return;
    openRoot.remove(); openRoot = null; lock(false);
  }
  function openPopup(group, i) {
    var t = tpls[group][i]; if (!t) return;
    var was = !!openRoot;
    if (openRoot) { openRoot.remove(); openRoot = null; }
    var root = t.content.firstElementChild.cloneNode(true);
    var host = doc.getElementById('main_MF') || body;
    var sb = doc.getElementById('SCROLL_TO_BOTTOM');
    host.insertBefore(root, sb && sb.parentNode === host ? sb : null);
    openRoot = root; lock(true);
    initGalleries(root);
    armMotion(root, true);
    var n = Object.keys(tpls[group]).length;
    root.addEventListener('click', function (e) {
      var b = e.target.closest('button,a');
      var lbl = b && (b.getAttribute('aria-label') || '');
      if (e.target.closest('[data-testid="popupCloseIconButtonRoot"]') || lbl === 'Close button') { e.preventDefault(); closePopup(); return; }
      if (lbl === 'previous post') { e.preventDefault(); openPopup(group, (i - 1 + n) % n); return; }
      if (lbl === 'next post') { e.preventDefault(); openPopup(group, (i + 1) % n); return; }
      if (!e.target.closest('.wixui-lightbox, [data-block-level-container], .pro-gallery')) closePopup();
    });
  }
  $$('[aria-haspopup="dialog"]:not(.item-action)').forEach(function (el, i) {
    el.addEventListener('click', function (e) { e.preventDefault(); openPopup('popup', i); });
  });

  /* ---------- phone menu ---------- */
  var tg = doc.getElementById('MENU_AS_CONTAINER_TOGGLE'), mc = doc.getElementById('MENU_AS_CONTAINER');
  if (tg && mc) {
    var ov = doc.getElementById('overlay-MENU_AS_CONTAINER'),
        ct = doc.getElementById('container-MENU_AS_CONTAINER'),
        ip = doc.getElementById('inlineContentParent-MENU_AS_CONTAINER');
    var setMenu = function (open) {
      tg.classList.toggle('d0L2ow', open);
      tg.setAttribute('aria-label', open ? 'Close navigation menu' : 'Open navigation menu');
      mc.setAttribute('data-undisplayed', open ? 'false' : 'true');
      mc.classList.toggle('I_VSKP', open); mc.classList.toggle('undefined', open);
      if (ov) ov.style.cssText = open ? 'opacity: 1; visibility: inherit;' : '';
      if (ct) ct.style.cssText = open ? 'visibility: inherit;' : '';
      if (ip) ip.style.cssText = open ? 'overscroll-behavior-y: contain;' : '';
      lock(open);
    };
    tg.addEventListener('click', function (e) { e.preventDefault(); setMenu(!mc.classList.contains('I_VSKP')); });
    if (ov) ov.addEventListener('click', function () { setMenu(false); });
    mc.addEventListener('click', function (e) { if (e.target.closest('a[href]')) setMenu(false); });
  }

  /* ---------- slideshow ---------- */
  $$('.wixui-slideshow').forEach(function (ss) {
    var slides = $$('[data-site-slide]', ss);
    if (slides.length < 2) return;
    var cur = slides.findIndex(function (s) { return s.hasAttribute('data-site-active'); });
    if (cur < 0) cur = 0;
    var abs = getComputedStyle(slides[0]).position === 'static';
    slides.forEach(function (s, i) {
      if (abs) { s.style.position = 'absolute'; s.style.top = '0'; s.style.left = '0'; }
      s.style.transition = 'opacity .9s ease-in-out';
      s.style.opacity = i === cur ? '1' : '0';
      s.style.visibility = i === cur ? 'visible' : 'hidden';
      s.style.zIndex = i === cur ? '1' : '0';
    });
    var dots = $$('nav li', ss);
    var show = function (n) {
      n = (n + slides.length) % slides.length; if (n === cur) return;
      var a = slides[cur], b = slides[n];
      b.style.visibility = 'visible'; b.style.zIndex = '1'; a.style.zIndex = '0';
      b.style.opacity = '1'; a.style.opacity = '0';
      setTimeout(function () { if (a.style.opacity === '0') a.style.visibility = 'hidden'; }, 950);
      dots.forEach(function (li) {
        var on = li.querySelector('a') && li.querySelector('a').getAttribute('href').indexOf(b.dataset.siteSlide) >= 0;
        if (on) li.setAttribute('aria-current', 'true'); else li.removeAttribute('aria-current');
        var link = li.querySelector('a'); if (link) link.classList.toggle('JPnvZO', on);
      });
      cur = n;
    };
    var timer = setInterval(function () { show(cur + 1); }, 4800);
    var reset = function () { clearInterval(timer); timer = setInterval(function () { show(cur + 1); }, 4800); };
    var nb = ss.querySelector('[data-testid="nextButton"]'), pb = ss.querySelector('[data-testid="prevButton"]');
    if (nb) nb.addEventListener('click', function (e) { e.preventDefault(); show(cur + 1); reset(); });
    if (pb) pb.addEventListener('click', function (e) { e.preventDefault(); show(cur - 1); reset(); });
    dots.forEach(function (li) {
      var a = li.querySelector('a'); if (!a) return;
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var id = a.getAttribute('href').split('#')[1];
        var n = slides.findIndex(function (s) { return s.dataset.siteSlide === id; });
        if (n >= 0) { show(n); reset(); }
      });
    });
    var x0 = null;
    ss.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    ss.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 40) { show(cur + (dx < 0 ? 1 : -1)); reset(); }
    });
  });

  /* ---------- galleries ---------- */
  var ARROW = '<svg viewBox="0 0 9 16" width="9" height="16" fill="currentColor"><path d="M0.7 0 0 0.7 7.3 8 0 15.3 0.7 16 8.7 8z"/></svg>';
  function initGalleries(root) {
    $$('.gallery-horizontal-scroll', root).forEach(function (sc) {
      if (sc.dataset.siteInit) return; sc.dataset.siteInit = '1';
      sc.style.overflowX = 'auto';
      var gal = sc.closest('.pro-gallery-parent-container') || sc.parentNode;
      var next = gal.querySelector('[data-hook="nav-arrow-next"]');
      var prev = gal.querySelector('[data-hook="nav-arrow-prev"]');
      if (next && !prev) {
        prev = next.cloneNode(true);
        prev.setAttribute('data-hook', 'nav-arrow-prev'); prev.setAttribute('aria-label', 'Previous Item');
        prev.style.right = 'auto'; prev.style.left = next.style.right || '24px';
        var sv = prev.querySelector('svg'); if (sv) sv.style.transform = 'scaleX(-1)';
        next.parentNode.insertBefore(prev, next);
      }
      var step = function (dir) {
        var item = sc.querySelector('.gallery-item-container');
        var w = item ? item.getBoundingClientRect().width + 10 : sc.clientWidth;
        sc.scrollBy({ left: dir * w, behavior: 'smooth' });
      };
      var upd = function () {
        if (prev) prev.style.display = sc.scrollLeft > 2 ? '' : 'none';
        if (next) next.style.display = sc.scrollLeft + sc.clientWidth < sc.scrollWidth - 2 ? '' : 'none';
      };
      if (next) next.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); step(1); });
      if (prev) prev.addEventListener('click', function (e) { e.preventDefault(); e.stopPropagation(); step(-1); });
      sc.addEventListener('scroll', upd, { passive: true }); upd();
      if (AUTOSLIDE[sc.id]) autoslide(sc);
    });
  }
  /* Ovadia + Raymond galleries auto-advance on desktop (2s cycle: 0.8s slide, pause on hover) */
  var AUTOSLIDE = { 'gallery-horizontal-scroll-comp-m9303usa': 1, 'gallery-horizontal-scroll-comp-m930gfol4': 1 };
  var isDesktop = ((doc.querySelector('meta[name=site-device]') || {}).content || 'desktop') === 'desktop';
  function autoslide(sc) {
    var inner = sc.querySelector('.gallery-horizontal-scroll-inner'), hover = false, busy = false;
    sc.addEventListener('mouseenter', function () { hover = true; });
    sc.addEventListener('mouseleave', function () { hover = false; });
    setInterval(function () {
      if (hover || busy || !inner) return;
      var left = sc.getBoundingClientRect().left, d = 0;
      $$('.gallery-item-container', sc).some(function (it) {
        var x = it.getBoundingClientRect().left - left - 5;
        if (x > 2) { d = x; return true; }
      });
      var max = sc.scrollWidth - sc.clientWidth;
      if (!d || sc.scrollLeft >= max - 2) { sc.scrollTo({ left: 0, behavior: 'smooth' }); return; }
      d = Math.min(d, max - sc.scrollLeft);
      busy = true;
      inner.style.transition = 'transform 800ms linear';
      inner.style.transform = 'translateX(' + (-d) + 'px)';
      setTimeout(function () {
        inner.style.transition = 'none'; inner.style.transform = 'translateX(0px)';
        sc.scrollLeft += d; busy = false;
      }, 810);
    }, 2010);
  }
  initGalleries(doc);

  /* full-screen photo viewer (Campus / Ovadia / Raymond galleries) */
  var viewer = null;
  function bestSrc(item) {
    var cands = [];
    $$('source, img', item).forEach(function (el) {
      (el.getAttribute('srcset') || '').split(/,\s+/).forEach(function (c) {
        var p = c.trim().split(/\s+/); if (p[0]) cands.push([p[0], parseFloat(p[1]) || 1]);
      });
      if (el.getAttribute('src')) cands.push([el.getAttribute('src'), 1]);
    });
    cands.sort(function (a, b) { return b[1] - a[1]; });
    return cands.length ? cands[0][0] : '';
  }
  function closeViewer() { if (viewer) { viewer.remove(); viewer = null; lock(false); } }
  function openViewer(items, i) {
    closeViewer();
    var mobile = /mobile/.test((doc.querySelector('meta[name=site-device]') || {}).content || '');
    viewer = doc.createElement('div');
    viewer.className = 'site-viewer' + (mobile ? ' site-viewer--m' : '');
    viewer.innerHTML =
      '<button class="sv-close" aria-label="Close">' + (mobile
        ? '<svg viewBox="0 0 24 24" width="28" height="28"><path d="M22 11.5H3.9l6.3-6.3-.7-.7L2 12l7.5 7.5.7-.7-6.3-6.3H22z" fill="currentColor"/></svg>'
        : '<svg viewBox="0 0 24 24" width="22" height="22"><path d="M19.3 4 12 11.3 4.7 4 4 4.7 11.3 12 4 19.3l.7.7 7.3-7.3 7.3 7.3.7-.7-7.3-7.3L20 4.7z" fill="currentColor"/></svg>') + '</button>' +
      (mobile ? '' : '<button class="sv-full" aria-label="Full screen"><svg viewBox="0 0 24 24" width="20" height="20"><path d="M4 14v6h6v-1H5.7l5.15-5.15-.7-.7L5 18.3V14zM14 4v1h4.3l-5.15 5.15.7.7L19 5.7V10h1V4z" fill="currentColor"/></svg></button>') +
      '<button class="sv-prev" aria-label="Previous">' + ARROW + '</button>' +
      '<button class="sv-next" aria-label="Next">' + ARROW + '</button>' +
      '<div class="sv-stage"><img alt=""></div>';
    body.appendChild(viewer); lock(true);
    var img = viewer.querySelector('img');
    var go = function (n) { i = (n + items.length) % items.length; img.src = bestSrc(items[i]); img.alt = (items[i].querySelector('img') || {}).alt || ''; };
    go(i);
    viewer.querySelector('.sv-close').onclick = closeViewer;
    viewer.querySelector('.sv-prev').onclick = function () { go(i - 1); };
    viewer.querySelector('.sv-next').onclick = function () { go(i + 1); };
    var fs = viewer.querySelector('.sv-full');
    if (fs) fs.onclick = function () { if (doc.fullscreenElement) doc.exitFullscreen(); else viewer.requestFullscreen && viewer.requestFullscreen(); };
    var x0 = null;
    viewer.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    viewer.addEventListener('touchend', function (e) {
      if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 40) go(i + (dx < 0 ? 1 : -1));
    });
  }
  doc.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { closeViewer(); closePopup(); }
    if (viewer && e.key === 'ArrowRight') viewer.querySelector('.sv-next').click();
    if (viewer && e.key === 'ArrowLeft') viewer.querySelector('.sv-prev').click();
  });

  /* clicks on gallery items: Instagram feed -> post pop-up, photo galleries -> viewer */
  var instaItems = $$('.wixui-gallery .item-action');
  doc.addEventListener('click', function (e) {
    var cont = e.target.closest('.gallery-item-container');
    var act = e.target.closest('.item-action') || (cont && cont.querySelector('.item-action'));
    if (!act || (openRoot && openRoot.contains(act))) return;
    e.preventDefault();
    var k = instaItems.indexOf(act);
    if (k >= 0) { openPopup('insta', k); return; }
    var gal = act.closest('.pro-gallery-parent-container') || act.closest('.pro-gallery');
    var items = $$('.gallery-item-container', gal);
    var item = act.closest('.gallery-item-container') || act.parentNode;
    openViewer(items, Math.max(0, items.indexOf(item)));
  }, true);
})();
