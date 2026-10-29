#!/usr/bin/env python3
"""Turn captured Wix pages into a standalone static site.

MODE=prod    -> root-absolute links (/team), served by Cloudflare Pages + _middleware
MODE=preview -> relative links (team.html), phone pages reached by JS redirect
"""
import hashlib, html, json, os, re, shutil, sys, mimetypes
import urllib.parse as up
from concurrent.futures import ThreadPoolExecutor
import requests

CAP = "/home/claude/cap"
TOOLS = "/home/claude/tools"
OUT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/site"
MODE = os.environ.get("MODE", "prod")
CACHE = "/home/claude/dlcache"
os.makedirs(CACHE, exist_ok=True)
SITE = "https://www.moreshetyerushalayim.com"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"

PAGES = {  # capture folder -> output file stem
    "home": "index", "team": "team", "student-life": "student-life", "campus": "campus",
    "application": "application", "media": "media", "faq": "faq", "alumni": "alumni",
    "donate": "donate", "ovadiabuddysutton": "ovadiabuddysutton",
    "raymondmosseri": "raymondmosseri", "visainformation": "visainformation",
    "codeofconduct": "codeofconduct", "copy-of-ovaida-buddy-sutton": "copy-of-ovaida-buddy-sutton",
    "this-page-does-not-exist-404": "404",
}
ROUTES = {v: ("/" if v == "index" else "/" + v) for v in PAGES.values()}
REDIRECTS = {"/about-5": "/ovadiabuddysutton", "/copy-of-student-life": "/codeofconduct",
             "/general-4": "/faq", "/ourteam": "/team", "/ovadiabuttysutton": "/ovadiabuddysutton",
             "/s-projects-side-by-side": "/media", "/team-3": "/team", "/home": "/"}
MAP_EMBED = os.environ.get("MAP_EMBED", "")

ASSET_RE = re.compile(r'(?:https?:)?//(?:static\.wixstatic\.com|static\.parastorage\.com|siteassets\.parastorage\.com|[a-z0-9-]+\.cdninstagram\.com|www\.moreshetyerushalayim\.com/_files)/[^\s"\'()<>\\]+')

S = requests.Session()
S.headers.update({"User-Agent": UA, "Accept": "image/webp,image/png,image/jpeg,image/svg+xml,*/*;q=0.5"})

def cache_get(url):
    k = hashlib.sha1(url.encode()).hexdigest()
    p = os.path.join(CACHE, k)
    if os.path.exists(p + ".meta"):
        meta = json.load(open(p + ".meta"))
        return (open(p, "rb").read() if meta["ok"] else None), meta.get("ct", "")
    try:
        r = S.get(url, timeout=60)
        ok = r.status_code == 200
        if ok:
            open(p, "wb").write(r.content)
        json.dump({"ok": ok, "ct": r.headers.get("content-type", ""), "status": r.status_code}, open(p + ".meta", "w"))
        return (r.content if ok else None), r.headers.get("content-type", "")
    except Exception as e:
        print("  fetch fail", url[:120], e)
        return None, ""

EXT_BY_CT = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp", "image/avif": ".avif",
             "image/gif": ".gif", "image/svg+xml": ".svg", "font/woff2": ".woff2", "font/woff": ".woff",
             "application/font-woff2": ".woff2", "application/font-woff": ".woff", "font/ttf": ".ttf",
             "text/css": ".css", "application/pdf": ".pdf", "image/x-icon": ".ico", "image/vnd.microsoft.icon": ".ico"}

def norm(tok):
    u = html.unescape(tok)
    if u.startswith("//"):
        u = "https:" + u
    return u

local_of = {}      # absolute url -> site path (starting with /)
written = set()
by_content = {}

def out_write(path, data):
    full = os.path.join(OUT, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "wb").write(data)
    written.add(path)

def css_rewrite(css, css_url, css_path):
    """Localize url(...) inside a downloaded stylesheet, relative to css_path."""
    def rep(m):
        raw = m.group(2).strip()
        if raw.startswith("data:") or raw.startswith("#"):
            return m.group(0)
        absu = up.urljoin(css_url, html.unescape(raw))
        if not absu.startswith("http"):
            return m.group(0)
        lp = localize_url(absu)
        if not lp:
            return m.group(0)
        rel = os.path.relpath(lp, os.path.dirname(css_path))
        return f"url({m.group(1)}{rel}{m.group(1)})"
    return re.sub(r'url\((["\']?)([^)"\']+)\1\)', rep, css)

def localize_url(u):
    if u in local_of:
        return local_of[u]
    pu = up.urlparse(u)
    if pu.netloc == "www.moreshetyerushalayim.com" and pu.path.startswith("/_files/"):
        data, ct = cache_get(u)
        if data is None:
            local_of[u] = None; return None
        lp = pu.path
        out_write(lp, data); local_of[u] = lp; return lp
    data, ct = cache_get(u)
    if data is None:
        local_of[u] = None
        return None
    ct = ct.split(";")[0].strip().lower()
    base = os.path.basename(up.unquote(pu.path)) or "file"
    base = re.sub(r"[^A-Za-z0-9._~-]", "_", base)[-60:]
    stem, ext = os.path.splitext(base)
    ext = EXT_BY_CT.get(ct, ext or ".bin")
    h = hashlib.sha1(u.encode()).hexdigest()[:10]
    folder = "/media" if ("wixstatic" in pu.netloc or "cdninstagram" in pu.netloc) else "/assets"
    if "cdninstagram" in pu.netloc:
        folder = "/media/instagram"
    if ext != ".css":
        ch = hashlib.sha1(data).hexdigest()
        if ch in by_content:
            local_of[u] = by_content[ch]
            return by_content[ch]
    lp = f"{folder}/{h}-{stem[:40]}{ext}"
    local_of[u] = lp
    if ext == ".css":
        css = data.decode("utf-8", "replace")
        data = css_rewrite(css, u, lp).encode()
    else:
        by_content[ch] = lp
    out_write(lp, data)
    return lp

def prefetch(urls):
    with ThreadPoolExecutor(16) as ex:
        list(ex.map(lambda u: cache_get(u), urls))

# ---------- string helpers ----------
def find_elem(h, start_tag_pos, tag="div"):
    """Return (start, end) of the element whose start tag begins at start_tag_pos (balanced on `tag`)."""
    depth = 0
    for m in re.compile(rf"<{tag}\b|</{tag}>").finditer(h, start_tag_pos):
        if m.group(0).startswith("</"):
            depth -= 1
            if depth == 0:
                return start_tag_pos, m.end()
        else:
            depth += 1
    raise ValueError("unbalanced")

def elem_by_attr(h, attr_text, tag="div"):
    i = h.find(attr_text)
    if i < 0:
        return None
    s = h.rfind(f"<{tag}", 0, i)
    return find_elem(h, s, tag)

def inner_range(h, start, end):
    gt = h.find(">", start) + 1
    close = h.rfind("<", start, end)
    return gt, close

def strip_wix(h):
    h = re.sub(r'<script\b(?![^>]*application/ld\+json)[^>]*>.*?</script>', "", h, flags=re.S | re.I)
    h = re.sub(r'<link\b[^>]*rel="(?:preload|modulepreload|prefetch|preconnect|dns-prefetch)"[^>]*>', "", h, flags=re.I)
    h = re.sub(r'<noscript\b[^>]*>.*?</noscript>', "", h, flags=re.S | re.I)
    h = re.sub(r'<meta\b[^>]*http-equiv="X-Wix[^"]*"[^>]*>', "", h, flags=re.I)
    return h

def fix_links(h):
    def a_tag(m):
        t = m.group(0)
        def hr(mm):
            url = html.unescape(mm.group(1))
            pu = up.urlparse(url)
            if pu.netloc in ("www.moreshetyerushalayim.com", "moreshetyerushalayim.com") and not pu.path.startswith("/_files/"):
                path = pu.path.rstrip("/") or "/"
                path = REDIRECTS.get(path, path)
                frag = ("#" + pu.fragment) if pu.fragment else ""
                return f'href="@@PAGE:{path}@@{frag}"'
            return mm.group(0)
        return re.sub(r'href="([^"]*)"', hr, t)
    return re.sub(r"<a\b[^>]*>", a_tag, h)

def collect_assets(h):
    return {norm(m.group(0).split("&quot;")[0]) for m in ASSET_RE.finditer(h)}

def localize_doc(h):
    def rep(m):
        tok = m.group(0)
        cut = tok.find("&quot;")
        rest = ""
        if cut >= 0:
            tok, rest = tok[:cut], tok[cut:]
        lp = localize_url(norm(tok))
        return ("@@ROOT@@" + lp + rest) if lp else m.group(0)
    return ASSET_RE.sub(rep, h)

def head_inject(h, dev, popups_css=""):
    extra = f'<meta name="site-device" content="{dev}">'
    extra += '<link rel="stylesheet" href="@@ROOT@@/assets/site.css">'
    if dev == "mobile":
        extra += '<link rel="stylesheet" href="@@ROOT@@/assets/mobile-compact.css">'
    if MODE == "preview" and dev == "desktop":
        extra = ('<script>(function(){if(/iPhone|iPod|Android.*Mobile|Windows Phone|BlackBerry|BB10|Opera Mini|IEMobile|webOS/i.test(navigator.userAgent)){'
                 'var f=location.pathname.split("/").pop()||"index.html";location.replace("_m/"+f+location.search+location.hash);}})();</script>') + extra
    extra += popups_css
    h = re.sub(r"<head\b[^>]*>", lambda m: m.group(0) + extra, h, count=1)
    h = h.replace("</body>", '<script src="@@ROOT@@/assets/site.js"></script></body>', 1)
    return h

def finalize(h, dev):
    prefix = "/" if MODE == "prod" else ("" if dev == "desktop" else "../")
    root = "" if MODE == "prod" else prefix.rstrip("/")
    def page(m):
        path = m.group(1)
        if MODE == "prod":
            return path
        stem = "index" if path == "/" else path.lstrip("/")
        return f"{prefix}{stem}.html"
    h = re.sub(r"@@PAGE:([^@]*)@@", page, h)
    # absolute URLs required in social meta tags
    h = re.sub(r'(<meta\b[^>]*content=")@@ROOT@@', lambda m: m.group(1) + SITE, h)
    h = h.replace("@@ROOT@@", root if MODE == "preview" else "")
    return h

# ---------- feature builders ----------
def build_popups(name, dev, h):
    d = os.path.join(CAP, dev, name)
    files = sorted([f for f in os.listdir(d) if re.match(r"(popup|insta)\d+\.html$", f)],
                   key=lambda f: (f[:5], int(re.findall(r"\d+", f)[0])))
    if not files:
        return h, ""
    base_styles = set(re.findall(r'<style id="([^"]+)"', h))
    base_anon = set(re.findall(r'<style>(.*?)</style>', h, flags=re.S))
    styles, tpl = {}, ""
    for f in files:
        p = open(os.path.join(d, f)).read()
        s, e = elem_by_attr(p, 'id="POPUPS_ROOT"')
        root = p[s:e]
        outside = p[:s] + p[e:]
        for sid, body in re.findall(r'<style id="([^"]+)"[^>]*>(.*?)</style>', outside, flags=re.S):
            if sid not in base_styles:
                styles[sid] = body
        for body in re.findall(r'<style>(.*?)</style>', outside, flags=re.S):
            if body not in base_anon:
                styles["anon-" + hashlib.sha1(body.encode()).hexdigest()[:8]] = body
        for ln in re.findall(r'<link\b[^>]*rel="stylesheet"[^>]*>', outside):
            if ln not in h:
                styles["link-" + hashlib.sha1(ln.encode()).hexdigest()[:8]] = ("LINK", ln)
        group = "insta" if f.startswith("insta") else "popup"
        idx = int(re.findall(r"\d+", f)[0])
        tpl += f'<template class="site-popup" data-popup-group="{group}" data-popup-index="{idx}">{root}</template>'
    h = h.replace("</body>", tpl + "</body>", 1)
    css = "".join(v[1] if isinstance(v, tuple) else f'<style id="{k}">{v}</style>' for k, v in styles.items())
    return h, css

def build_slides(name, dev, h):
    if name != "alumni":
        return h
    if dev == "desktop":
        caps = json.load(open(f"{CAP}/extra/desktop_slides.json"))
        by = {}
        for inner in caps:
            pos = 0
            kids = []
            while True:
                s = inner.find("<div", pos)
                if s < 0: break
                s2, e2 = find_elem(inner, s)
                kids.append(inner[s2:e2]); pos = e2
            if len(kids) == 1:
                sid = re.search(r'id="([^"]+)"', kids[0]).group(1)
                by.setdefault(sid, kids[0])
    else:
        by = json.load(open(f"{CAP}/extra/mobile_slides_byid.json"))
    rng = elem_by_attr(h, 'data-testid="slidesWrapper"')
    s, e = rng
    gs, ge = inner_range(h, s, e)
    nav_ids = re.findall(r'href="\./#(comp-[a-z0-9]+)"', h[e:e + 4000]) or list(by)
    order = [i for i in nav_ids if i in by]
    missing = [i for i in nav_ids if i not in by]
    if missing:
        print("  WARNING missing slides", dev, missing)
    cur = re.search(r'id="(comp-[a-z0-9]+)"', h[gs:ge])
    first = cur.group(1) if cur else order[0]
    slides = "".join(by[i].replace("<div", f'<div data-site-slide="{i}"' + (' data-site-active="1"' if i == first else ""), 1) for i in order)
    return h[:gs] + slides + h[ge:]

def build_gallery_data(h):
    """Attach full-size image + caption to every pro-gallery item for the viewer."""
    def rep(m):
        tag = m.group(0)
        return tag
    return h

def build_map(h):
    if not MAP_EMBED:
        return h
    return re.sub(r'(<iframe\b[^>]*src=")https://static\.parastorage\.com/services/editor-elements-library/dist/thunderbolt/media/googleMap[^"]*(")',
                  lambda m: m.group(1) + html.escape(MAP_EMBED) + m.group(2), h)

def build_donate(h):
    return h.replace("https://www-moreshetyerushalayim-com.filesusr.com/html/a4810d_5285aced8166c88e2ddb43c5c03d43f8.html",
                     "@@ROOT@@/embeds/donate.html")


# ---------- menu sub-items that jump to a section of a page ----------
ANCHOR_OVERRIDES = {"dataItem-m92ysos5": "comp-m92ysor2"}  # "Instagram" item -> section labelled "Insatgram" on Wix
_anchor_map = None
def anchor_map():
    global _anchor_map
    if _anchor_map is not None:
        return _anchor_map
    m = dict(ANCHOR_OVERRIDES)
    home = open(os.path.join(CAP, "desktop", "home", "page.html")).read()
    for da, href, label in re.findall(r'<a\b[^>]*data-anchor="([^"]+)"[^>]*href="([^"]+)"[^>]*>.*?__label">([^<]+)<', home, flags=re.S):
        if da in m:
            continue
        path = href.split(".com")[-1].strip("/") or "home"
        try:
            t = open(os.path.join(CAP, "desktop", path, "page.html")).read()
        except OSError:
            continue
        r = re.search(r'id="(comp-[a-z0-9]+)" class="[^"]*" role="region" tabindex="-1" aria-label="' + re.escape(label.strip()) + '"', t)
        if r:
            m[da] = r.group(1)
    _anchor_map = m
    return m

def build_anchors(h):
    am = anchor_map()
    return re.sub(r'data-anchor="([^"]+)"', lambda mm: mm.group(0) + (f' data-site-anchor="{am[mm.group(1)]}"' if mm.group(1) in am else ""), h)

# Page names Wix had wrong (shown on the browser tab and in Google)
TITLE_FIX = {"codeofconduct": "Code of Conduct", "visainformation": "Visa Information",
             "ovadiabuddysutton": "Ovadia Buddy Sutton", "copy-of-ovaida-buddy-sutton": "Saul E. Ashkenazi"}
def fix_title(name, h):
    if name not in TITLE_FIX:
        return h
    t = TITLE_FIX[name] + " | Yeshivat Moreshet Yerushalayim"
    h = re.sub(r"<title>[^<]*</title>", "<title>" + t + "</title>", h, count=1)
    h = re.sub(r'(<meta\b[^>]*(?:property|name)="(?:og:title|twitter:title)"[^>]*content=")[^"]*(")', lambda m: m.group(1) + t + m.group(2), h)
    h = re.sub(r'(<meta\b[^>]*content=")[^"]*("[^>]*(?:property|name)="(?:og:title|twitter:title)")', lambda m: m.group(1) + t + m.group(2), h)
    return h

def process(name, dev):
    raw = open(os.path.join(CAP, dev, name, "page.html")).read()
    h = strip_wix(raw)
    h = fix_links(h)
    h = build_anchors(h)
    h = fix_title(name, h)
    h, pcss = build_popups(name, dev, h)
    h = build_slides(name, dev, h)
    h = build_map(h)
    h = build_donate(h)
    h = head_inject(h, dev, pcss)
    # re-arm Wix entrance animations (played by site.js when each element scrolls into view)
    h = h.replace(' data-motion-enter="done"', ' data-motion-enter="pending"')
    # Wix's script pins images to the pixel size of the 1280px capture; restore its fluid sizing
    h = re.sub(r'(<img\b[^>]*style=")width: ?\d+(?:\.\d+)?px; ?height: ?\d+(?:\.\d+)?px;( ?object-fit)',
               r'\1width:100%;height:100%;\2', h)
    return h

def main():
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    docs = {}
    for name, stem in PAGES.items():
        for dev in ("desktop", "mobile"):
            docs[(stem, dev)] = process(name, dev)
    allu = set()
    for h in docs.values():
        allu |= collect_assets(h)
    print("assets referenced:", len(allu))
    prefetch(sorted(allu))
    for (stem, dev), h in docs.items():
        h = localize_doc(h)
        h = finalize(h, dev)
        path = f"/{stem}.html" if dev == "desktop" else f"/_m/{stem}.html"
        out_write(path, h.encode())
    # static support files
    for f in ("site.js", "site.css", "mobile-compact.css"):
        shutil.copy(os.path.join(TOOLS, f), os.path.join(OUT, "assets", f))
    os.makedirs(os.path.join(OUT, "embeds"), exist_ok=True)
    shutil.copy(os.path.join(TOOLS, "donate.html"), os.path.join(OUT, "embeds", "donate.html"))
    if MODE == "prod":
        open(os.path.join(OUT, "_redirects"), "w").write("".join(f"{a} {b} 301\n" for a, b in REDIRECTS.items()))
        os.makedirs(os.path.join(OUT, "functions"), exist_ok=True)
        shutil.copy(os.path.join(TOOLS, "_middleware.js"), os.path.join(OUT, "functions", "_middleware.js"))
    missing = [u for u, v in local_of.items() if v is None]
    print("written files:", len(written), "missing:", len(missing))
    for u in missing[:40]:
        print("  MISSING", u[:160])

if __name__ == "__main__":
    main()
