#!/usr/bin/env python3
"""Generate the redesigned Moreshet site (responsive, one page per URL) into redesign/out."""
import html, io, json, os, re
import requests
from PIL import Image

R = "/home/claude/redesign"
OUT = R + "/out"
SP = "/home/claude/site_preview"
CAP = "/home/claude/cap"
E = html.escape
os.makedirs(OUT + "/media/rd", exist_ok=True)

ALLCAP = "".join(open(f).read() for f in [CAP + "/desktop/%s/page.html" % p for p in
                 ["home", "campus", "ovadiabuddysutton", "raymondmosseri", "copy-of-ovaida-buddy-sutton", "donate", "alumni"]])

def hires(local, w=1600):
    """Upgrade a captured Wix image to a sharper copy (max w px), saved under /media/rd/."""
    m = re.search(r"(a4810d_[a-f0-9]{32})", local)
    if not m:
        return local
    wid = m.group(1)
    dst = "/media/rd/%s-%d.webp" % (wid, w)
    if os.path.exists(OUT + dst):
        return dst
    ext = re.search(wid + r"~mv2\.(\w+)", ALLCAP)
    ext = ext.group(1) if ext else "jpg"
    url = "https://static.wixstatic.com/media/%s~mv2.%s/v1/fit/w_%d,h_%d,q_88/x.%s" % (wid, ext, w, w, ext)
    try:
        r = requests.get(url, timeout=60); r.raise_for_status()
        im = Image.open(io.BytesIO(r.content)).convert("RGB")
        im.save(OUT + dst, quality=82, method=6)
        return dst
    except Exception as e:
        print("hires fail", local, e)
        return local

# ---------------------------------------------------------------- shared chrome
NAV = [
    ("Home", "/", []),
    ("Team", "/team", []),
    ("Student Life", "/student-life", [("Weekly Schedule", "/student-life#schedule"), ("Special Events", "/student-life#events"), ("Code of Conduct", "/codeofconduct")]),
    ("Campus", "/campus", []),
    ("Application", "/application", [("Application Steps", "/application#steps"), ("Before You Fly", "/application#checklist"), ("Visa Information", "/visainformation")]),
    ("Media", "/media", [("Recorded Shiurim", "/media#shiurim"), ("Moreshet Magazine", "/media#magazine"), ("Instagram", "/media#instagram")]),
    ("FAQ", "/faq", []),
    ("Alumni", "/alumni", [("Giving Back", "/alumni#giving"), ("Request a Transcript", "/alumni#transcript"), ("Testimonials", "/alumni#testimonials")]),
    ("Donate", "/donate", []),
]
LOGO = "/media/rd/logo.webp"
APPLY = "https://www.yeshivaapplication.org/"
WA = "https://chat.whatsapp.com/E8A9Q9Ur58lKCF0xgrJNPX"
IG = "https://www.instagram.com/moreshet_yerushalayim/"
WA_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>'
IG_SVG = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7.0301.084c-1.2768.0602-2.1487.264-2.911.5634-.7888.3075-1.4575.72-2.1228 1.3877-.6652.6677-1.075 1.3368-1.3802 2.127-.2954.7638-.4956 1.6365-.552 2.914-.0564 1.2775-.0689 1.6882-.0626 4.947.0062 3.2586.0206 3.6671.0825 4.9473.061 1.2765.264 2.1482.5635 2.9107.308.7889.72 1.4573 1.388 2.1228.6679.6655 1.3365 1.0743 2.1285 1.38.7632.295 1.6361.4961 2.9134.552 1.2773.056 1.6884.069 4.9462.0627 3.2578-.0062 3.668-.0207 4.9478-.0814 1.28-.0607 2.147-.2652 2.9098-.5633.7889-.3086 1.4578-.72 2.1228-1.3881.665-.6682 1.0745-1.3378 1.3795-2.1284.2957-.7632.4966-1.636.552-2.9124.056-1.2809.0692-1.6898.063-4.948-.0063-3.2583-.021-3.6668-.0817-4.9465-.0607-1.2797-.264-2.1487-.5633-2.9117-.3084-.7889-.72-1.4568-1.3876-2.1228C21.2982 1.33 20.628.9208 19.8378.6165 19.074.321 18.2017.1197 16.9244.0645 15.6471.0093 15.236-.005 11.977.0014 8.718.0076 8.31.0215 7.0301.0839m.1402 21.6932c-1.17-.0509-1.8053-.2453-2.2287-.408-.5606-.216-.96-.4771-1.3819-.895-.422-.4178-.6811-.8186-.9-1.378-.1644-.4234-.3624-1.058-.4171-2.228-.0595-1.2645-.072-1.6442-.079-4.848-.007-3.2037.0053-3.583.0607-4.848.05-1.169.2456-1.805.408-2.2282.216-.5613.4762-.96.895-1.3816.4188-.4217.8184-.6814 1.3783-.9003.423-.1651 1.0575-.3614 2.227-.4171 1.2655-.06 1.6447-.072 4.848-.079 3.2033-.007 3.5835.005 4.8495.0608 1.169.0508 1.8053.2445 2.228.408.5608.216.96.4754 1.3816.895.4217.4194.6816.8176.9005 1.3787.1653.4217.3617 1.056.4169 2.2263.0602 1.2655.0739 1.645.0796 4.848.0058 3.203-.0055 3.5834-.061 4.848-.051 1.17-.245 1.8055-.408 2.2294-.216.5604-.4763.96-.8954 1.3814-.419.4215-.8181.6811-1.3783.9-.4224.1649-1.0577.3617-2.2262.4174-1.2656.0595-1.6448.072-4.8493.079-3.2045.007-3.5825-.006-4.848-.0608M16.953 5.5864A1.44 1.44 0 1 0 18.39 4.144a1.44 1.44 0 0 0-1.437 1.4424M5.8385 12.012c.0067 3.4032 2.7706 6.1557 6.173 6.1493 3.4026-.0065 6.157-2.7701 6.1506-6.1733-.0065-3.4032-2.771-6.1565-6.174-6.1498-3.403.0067-6.156 2.771-6.1496 6.1738M8 12.0077a4 4 0 1 1 4.008 3.9921A3.9996 3.9996 0 0 1 8 12.0077"/></svg>'
HAND_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 15h2a2 2 0 1 0 0-4h-3c-.6 0-1.1.2-1.4.6L3 17"/><path d="m7 21 1.6-1.4c.3-.4.8-.6 1.4-.6h4c1.1 0 2.1-.4 2.8-1.2l4.6-4.4a2 2 0 0 0-2.75-2.91l-4.2 3.9"/><path d="m2 16 6 6"/><circle cx="16" cy="9" r="2.9"/><circle cx="6" cy="5" r="3"/></svg>'
ARROW = '<svg viewBox="0 0 30 10" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M0 5h28M24 1l4 4-4 4"/></svg>'

def header(cur):
    items = []
    for label, href, subs in NAV:
        cur_attr = ' aria-current="page"' if href == cur else ""
        sub = ""
        if subs:
            sub = '<ul class="sub">' + "".join('<li><a href="%s">%s</a></li>' % (h, E(l)) for l, h in subs) + "</ul>"
        items.append('<li><a href="%s"%s>%s</a>%s</li>' % (href, cur_attr, E(label), sub))
    mitems = []
    for label, href, subs in NAV:
        cur_attr = ' aria-current="page"' if href == cur else ""
        btn = '<button type="button" aria-expanded="false" aria-label="Show %s pages">+</button>' % E(label) if subs else ""
        sub = '<div class="subm">' + "".join('<a href="%s">%s</a>' % (h, E(l)) for l, h in subs) + "</div>" if subs else ""
        mitems.append('<li><div class="row"><a href="%s"%s>%s</a>%s</div>%s</li>' % (href, cur_attr, E(label), btn, sub))
    return """
<header class="hdr">
  <div class="hdr-top"><a href="/"><img src="%(logo)s" alt="Yeshivat Moreshet Yerushalayim, home" width="112" height="112"></a></div>
  <nav aria-label="Main"><ul class="nav">%(items)s</ul></nav>
  <div class="mbar">
    <a class="brand" href="/"><img src="%(logo)s" alt="Yeshivat Moreshet Yerushalayim, home" width="52" height="52"></a>
    <button type="button" id="menu-open" aria-label="Open menu" aria-expanded="false" aria-controls="menu"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
  </div>
</header>
<div class="menu" id="menu" role="dialog" aria-modal="true" aria-label="Menu">
  <div class="top"><img src="%(logo)s" alt=""><button type="button" id="menu-close" aria-label="Close menu"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19"/></svg></button></div>
  <ul>%(mitems)s</ul>
</div>""" % {"logo": LOGO, "items": "".join(items), "mitems": "".join(mitems)}

FOOTER = """
<footer class="ftr">
  <div class="wrap">
    <img class="logo" src="%(logo)s" alt="" width="150" height="150">
    <div class="col"><b>ISRAEL</b>Yeshivat Moreshet Yerushalayim<br>Korazin Street 22, Jerusalem, Israel<br><a href="mailto:Office@moreshetyerushalayim.com">Office@moreshetyerushalayim.com</a></div>
    <div class="col"><b>AMERICA / BUSINESS OFFICE</b>American Friends of Yeshivat Moreshet Yerushalayim<br>1385 Broadway, 16th Floor, NY, NY 10018<br><a href="mailto:vmosseri@moreshetyerushalayim.com">vmosseri@moreshetyerushalayim.com</a></div>
    <div class="soc"><a href="%(wa)s" aria-label="WhatsApp">%(wasvg)s</a><a href="%(ig)s" aria-label="Instagram">%(igsvg)s</a></div>
    <div class="copy">© Yeshivat Moreshet Yerushalayim</div>
  </div>
</footer>
<nav class="dock" aria-label="Quick actions">
  <a href="%(apply)s"><svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6M9 14h6M9 18h4"/></svg>APPLY</a>
  <a href="%(ig)s" class="ig">%(igsvg)sCONNECT</a>
  <a href="/donate">%(hand)sDONATE</a>
</nav>""" % {"wa": WA, "ig": IG, "logo": LOGO, "wasvg": WA_SVG, "igsvg": IG_SVG, "hand": HAND_SVG, "apply": APPLY}

def page(path, title, cur, body, desc="Yeshivat Moreshet Yerushalayim, a Sephardic post-high school yeshivah in Jerusalem."):
    body = body.replace("@@SHIURIMG@@", hires("/media/715d03e73e-a4810d_972ab573c1c2477f8eb295cbe9d5e9f4~.webp", 1400)).replace("@@ALUMIMG@@", hires("/media/962328bc9d-a4810d_fc7aac0f587e4d468de8872709e12437~.webp", 1400))
    doc = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s | Yeshivat Moreshet Yerushalayim</title>
<meta name="description" content="%s">
<meta name="robots" content="noindex">
<link rel="icon" href="%s">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:wght@400;600;700;800&family=Roboto+Serif:opsz,wght@8..144,600;8..144,700;8..144,800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/rd.css?v=17">
</head>
<body>
%s
<main id="main">
%s
</main>
%s
<script src="/assets/rd.js?v=14" defer></script>
</body>
</html>
""" % (E(title), E(desc), LOGO, header(cur), body, FOOTER)
    open(OUT + path, "w").write(doc)

def H(title, kind="h2", sub=""):
    return '<div class="h-center rv"><%s class="%s">%s</%s><div class="rule" aria-hidden="true"></div>%s</div>' % (kind, kind.replace("h", "h"), E(title), kind, sub)

def rich(t):
    """[[A url]]..[[/A]] / [[B]] markers from the extractor -> html."""
    t = E(t)
    t = re.sub(r"\[\[A (.*?)\]\]", lambda m: '<a href="%s">' % m.group(1).replace("&amp;", "&"), t)
    return t.replace("[[/A]]", "</a>").replace("[[B]]", "<b>").replace("[[/B]]", "</b>").replace("[[BR]]", "<br>")

# ---------------------------------------------------------------- data
team = json.load(open("/home/claude/team.json"))
bios = json.load(open("/home/claude/bios.json"))
pages = json.load(open(R + "/pages.json"))
rj = json.load(open(R + "/rich.json"))
mags = json.load(open(R + "/mags.json"))
insta = json.load(open(R + "/insta.json"))

def slug(n):
    return n.lower().replace("dr. ", "").replace("rabbi ", "").replace(" ", "-")

# ---------------------------------------------------------------- HOME
ALUMNI_Q = [("A big thing for me was seeing the history of Israel through actually seeing it, so I loved the hikes and the trips at Yeshivat Moreshet Yerushalayim.", "Daniel Braha", "Class of 2020"),
     ("Over two incredible years at Yeshivat Moreshet Yerushalayim, I didn’t just learn Torah. I found a home, mentors I trust, and friendships that last forever.", "Sol Terzi", "Class of 2025"),
     ("To me, Yeshivat Moreshet Yerushalayim was more than a year in Israel. It’s a lifetime investment that I continuously find paying returns throughout life.", "Ely Mamiye", "Class of 2023"),
     ("Yeshivat Moreshet Yerushalayim helped teach me about my heritage and helped me figure out my next steps.", "Victor Cohen", "Class of 2022"),
     ("Yeshivat Moreshet Yerushalayim gave me the foundation to one day, BeEzrat Hashem, lead a halakhic home.", "Albert Kroub", "Class of 2024"),
     ("My year in Yeshivat Moreshet Yerushalayim was transformative... The love I developed for the land of Israel will stay with me always, forming a foundation that will guide and strengthen me for the rest of my life.", "Jacob Cayre", "Class of 2025"),
     ("Yeshivat Moreshet Yerushalayim helped me understand the importance of Torah and Israel in our daily lives.", "Saul Bibi", "Class of 2022"),
     ("Yeshivat Moreshet Yerushalayim offers the once in a lifetime opportunity to live in Israel while learning from some of the top rabbis in the community. It lets you grow into who you want to be and have a great time doing it.", "Sam Setton", "Class of 2026")]

def quotes_band(link=True):
    one = "".join('<figure class="quote%s"><p>“%s”</p><cite>%s, %s</cite></figure>' % (" on" if i == 0 else "", E(q), E(n), E(c)) for i, (q, n, c) in enumerate(ALUMNI_Q))
    more = '<p style="text-align:center;margin:26px 0 0"><a class="pill" href="/alumni">More about our alumni %s</a></p>' % ARROW if link else ""
    return """<section class="band lilac" id="testimonials" aria-label="What our alumni say">
  <div class="wrap"><div class="quotes" aria-live="polite">%s</div>%s</div>
</section>""" % (one, more)

def home():
    hero = hires("/media/118bc2130c-a4810d_e78af485456e483c9c7ed59a2e5bc954~.webp", 2000)
    pil = [
        ("Love of Torah &amp; Learning", "/media/0384fc45ea-a4810d_3b44c764e6a846eb86cad5384954216a~.webp",
         "At Yeshivat Moreshet Yerushalayim, we are dedicated to cultivating a deep love for Torah and learning by fostering an environment of intellectual curiosity and spiritual growth. Our dynamic curriculum, taught by passionate rabbis, challenges students to engage with Torah texts at the highest level while building strong connections to Jewish roots. Through personalized mentorship and a supportive community, we inspire students to develop a lifelong commitment to Torah study and personal development.",
         'All Torah that is studied at Yeshivat Moreshet Yerushalayim is in loving memory of <a href="/ovadiabuddysutton" style="color:inherit">Ovadia Buddy Sutton A"H</a>.'),
        ("Israel: Past, Present &amp; Future", "/media/ad3059e73f-a4810d_cb74348d975f40ff936a9301da1f9be6~.webp",
         "At Yeshivat Moreshet Yerushalayim, we believe there’s no better place to foster a deep connection to Torah than in the heart of Israel. Our students explore the land through meaningful trips, from walking to the Kotel on Shabuot to special Yom Ha’asmaut celebrations, allowing them to experience the rich culture and history firsthand. These experiences help students develop a profound love for the Land of Israel, strengthening both their Jewish identity and connection to the heritage that surrounds them.", ""),
        ("Rabbi-Student Relationships", "/media/6cb5b0d28a-a4810d_642a80b1475d445aad919c65a670d0f8~.webp",
         "The bond between students and rabbis goes well beyond the Bet Midrash. Whether it’s seeking advice, joining the rabbis for Shabbat meals or celebrating holidays together, our rabbis are deeply involved in students’ lives, offering personal guidance and mentorship. This close-knit relationship continues long after the year ends, with students and rabbis connecting on a weekly basis.", ""),
        ("Preserving Sephardic Heritage", "/media/7d2df6d1fc-a4810d_09c1e8f4e0484006874827245de6fc17~.webp",
         "Our approach to Torah at Yeshivat Moreshet Yerushalayim is rooted in the rich traditions of Sephardic heritage. We teach Gemara, Tur and Bet Yosef through the Sephardic approach. In Halakha classes, there is a strong emphasis on community minhagim. Students are taught hazzanut and taamim. Every year, several students learn how to read the Megillah for Purim, ensuring that these treasured traditions are passed down through the generations.", ""),
        ("Sports &amp; Recreation", "/media/24c14a253f-a4810d_365262cb9bff4f6fb6913d98078393cf~.webp",
         "Beyond rigorous Torah study, students stay active with daily gym sessions, a Friday football league, Saturday night pickup basketball, and Tuesday night basketball leagues, ensuring they stay physically fit while having fun. After all, it’s not just about strengthening your mind—it’s about keeping your body healthy and energized too!", ""),
        ("Beyond the Year", "/media/d0e1aa04b5-a4810d_b67b2b4201e642d3b23b35549a92a16c~.webp",
         "The journey at Yeshivat Moreshet Yerushalayim doesn’t end with the completion of the year. We offer summer learning opportunities, spearheaded by alumni, in Deal, New Jersey. We have reunions, both formal and informal. It's not uncommon for students to come visit the school during the college breaks to learn and reconnect with each other, which we love! When the year concludes, it’s just the beginning of a lifelong journey of Torah learning, personal growth, meaningful friendships and continued community involvement.", ""),
    ]
    rows = ""
    for n, (t, img, p, ded) in enumerate(pil):
        rows += """<details class="pil rv" name="pillars"%s><summary><span class="num">%d</span><span class="pt">%s</span></summary><div class="pa"><p>%s</p>%s</div></details>""" % (
            "", n + 1, t, E(p), ('<p class="ded">%s</p>' % ded) if ded else "")
    tiles = "".join('<button type="button" class="pt-tile" data-pd="%d" aria-expanded="false" aria-controls="pt-panel" style="order:%d"><img src="%s" alt="" loading="lazy"><span class="pt-cap"><span class="num">%d</span>%s</span><span class="pt-plus" aria-hidden="true"></span></button>' % (n, 1 if n < 3 else 3, hires(img, 900), n + 1, t) for n, (t, img, p, ded) in enumerate(pil))
    texts = "".join('<div class="pt-tx" data-pd="%d" hidden><h3>%s</h3><p>%s</p>%s</div>' % (n, t, E(p), ('<p class="ded">%s</p>' % ded) if ded else "") for n, (t, img, p, ded) in enumerate(pil))
    desk = '<div class="pil-desk">%s<div class="pt-panel" id="pt-panel" role="region" aria-live="polite" hidden>%s</div></div>' % (tiles, texts)
    quotes = [
        ("Over two incredible years at Yeshivat Moreshet Yerushalayim, I didn’t just learn Torah. I found a home, mentors I trust, and friendships that last forever.", "Sol Terzi, Class of 2025"),
        ("To me, Yeshivat Moreshet Yerushalayim was more than a year in Israel. It’s a lifetime investment that I continuously find paying returns throughout life.", "Ely Mamiye, Class of 2023"),
        ("My year in Yeshivat Moreshet Yerushalayim was transformative. The love I developed for the land of Israel will stay with me always.", "Jacob Cayre, Class of 2025"),
        ("Yeshivat Moreshet Yerushalayim gave me the foundation to one day, BeEzrat Hashem, lead a halakhic home.", "Albert Kroub, Class of 2024"),
    ]
    q = "".join('<figure class="quote"><p>“%s”</p><cite>%s</cite></figure>' % (E(a), E(b)) for a, b in quotes)
    d = "".join('<button type="button" aria-label="Quote %d"></button>' % (i + 1) for i in range(len(quotes)))
    body = """
<section class="hero">
  <img class="hero-img" src="%s" alt="Students in front of the Yeshivah building in Jerusalem">
  <div class="hero-box rv">
    <h1 class="sr">Yeshivat Moreshet Yerushalayim</h1>
    <p>Yeshivat Moreshet Yerushalayim is a Sephardic post-high school yeshivah located in Jerusalem, dedicated to preparing young men for college, business and life with a strong foundation in Torah and <i>misvot</i>. Rooted in the rich traditions of Aram Soba, we strive to cultivate future leaders, Bnei Torah, who will carry their experience of living and learning in Eres Yisrael into every aspect of their lives.</p>
    <div class="acts"><a class="btn gold big" href="%s">APPLY NOW</a></div>
  </div>
</section>
<section class="band purple" aria-labelledby="pillars-h">
  <div class="wrap">
    <div class="h-center rv"><h2 class="h2" id="pillars-h">The Six Pillars of<br>Yeshivat Moreshet Yerushalayim</h2><div class="rule" aria-hidden="true"></div></div>
    <div class="pillars">%s</div>%s
  </div>
</section>
%s""" % (hero, APPLY, rows, desk, quotes_band(True))
    page("/index.html", "Home", "/", body)

# ---------------------------------------------------------------- TEAM
def team_page():
    groups = {}
    for i, p in enumerate(team):
        g = "madrichim" if p["section"] == "Madrichim" else "rabbis"
        role = "Head Madrich" if g == "madrichim" else p["role"]
        bio = " ".join(bios[str(i)][1:]).replace("\xa0", " ").strip()
        groups[p["name"]] = dict(name=p["name"], role=role, group=g, img="/media/team2/%s.webp" % slug(p["name"]), bio=bio)
    lead = groups.pop("Rabbi Harold Sutton")
    staff = [dict(name="R’ Victor Mosseri", role="Director of Finance", group="staff", img="", ini="VM", bio="Director of Finance, Staff in America."),
             dict(name="Victor Dweck", role="Director of Marketing", group="staff", img="", ini="VD", bio="Director of Marketing, Staff in America.")]
    people = list(groups.values())
    def last(n):
        n = n.replace("R’ ", "").replace("Rabbi ", "").replace("Dr. ", "")
        parts = n.split()
        return (parts[-1], n)
    people.sort(key=lambda p: last(p["name"]))
    cards, prev = "", ""
    for p in people:
        L = last(p["name"])[0][0]
        ph = '<img src="%s" alt="" loading="lazy">' % p["img"] if p["img"] else '<span class="ini">%s</span>' % p["ini"]
        cards += """<button type="button" class="person" data-group="%s" data-name="%s" data-role="%s" data-img="%s" data-bio="%s"><span class="ph">%s</span><span class="nm">%s</span><span class="rl">%s</span><span class="more">VIEW BIO ⟶</span></button>""" % (
            p["group"], E(p["name"]), E(p["role"]), p["img"], E(p["bio"]), ph, E(p["name"]), E(p["role"]))
    board = ["Ezra S. Ashkenazi, Co-Founder", "Isaac S. Chera", "Nathan M. Dweck", "Joey A. Franco", "Norman L. Jemal", "Solomon R. Mosseri", "Joseph Oved", "Jesse Salem"]
    staffhtml = "".join('<div class="st"><b>%s</b><span>%s</span></div>' % (E(s["name"]), E(s["role"])) for s in staff)
    body = """
<section class="band lilac">
  <div class="wrap lead">
    <button type="button" class="person leadp rv" data-name="Rabbi Harold Sutton" data-img="%s" data-bio="%s"><span class="ph"><img src="%s" alt=""></span><span class="kicker">ROSH YESHIVAH &amp; FOUNDER</span><h1 class="nm">Rabbi Harold Sutton</h1><span class="more">VIEW BIO ⟶</span></button>
  </div>
</section>
<section class="band purple" id="rabbis">
  <div class="wrap">
    <div class="h-center rv"><h2 class="h2">Our Team</h2><div class="rule" aria-hidden="true"></div><p class="az">(listed in alphabetical order)</p></div>
    <div class="grid-team" id="madrichim">%s</div>
  </div>
</section>
<section class="band purple tight" id="staff" style="padding-top:0">
  <div class="wrap">%s<div class="staff rv">%s</div></div>
</section>
<section class="band lilac" id="board">
  <div class="wrap">%s<div class="board rv">%s</div></div>
</section>
<dialog class="bio" id="bio" aria-labelledby="bio-name">
  <div class="bio-in"><div class="ph" id="bio-ph"><img id="bio-img" src="" alt=""></div>
  <div class="tx"><h2 id="bio-name"></h2><p id="bio-text"></p></div></div>
  <button type="button" class="x" id="bio-x" aria-label="Close"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.8" stroke-linecap="round" aria-hidden="true"><path d="M5 5l14 14M19 5L5 19"/></svg></button>
</dialog>""" % (lead["img"], E(lead["bio"]), lead["img"], cards, H("Staff in America", "h3"), staffhtml, H("Board of Trustees"), "".join("<div>%s</div>" % E(b) for b in board))
    page("/team.html", "Our Team", "/team", body)

# ---------------------------------------------------------------- STUDENT LIFE
SCHED_ROWS = [
    ("7:45AM", [("Shahrit followed by breakfast", 5, "t")], ("Shahrit followed by breakfast", "t")),
    ("9:15AM", [("Electives", 5, "")], ("10:00AM<br>Football League", "")),
    ("10:30AM", [("Gemara Shiur", 5, "")], None),
    ("12:45PM", [("Parasha Shiur", 2, ""), ("<small>12:00PM–1:00PM</small>Tur / Bet Yosef Shiur with Rabbi Alouf", 2, ""), ("Parasha Shiur", 1, "")], None),
    ("1:00PM", [("Lunch Break", 5, "break")], None),
    ("3:20PM", [("Minha", 2, "t"), ("<small>4:00PM</small>Minha", 1, "t"), ("Minha", 2, "t")], None),
    ("3:45PM", [("Halakha Shiur", 2, ""), ("<small>4:20PM</small>Parashat HaShabuah", 1, ""), ("Halakha Shiur", 2, "")], None),
    ("5:15PM", [("Independent Learning Groups", 2, ""), ("Pirke Abot", 1, ""), ("Independent Learning Groups", 2, "")], None),
    ("6:30PM", [("Dinner Break", 2, "break"), ("<small>6:00PM</small>Dinner Break", 1, "break"), ("Dinner Break", 2, "break")], None),
    ("7:45PM", [("Arbit", 5, "t")], None),
    ("8:00PM", [("Timely Topics", 1, ""), ("Gemara Bekiut", 3, ""), ("<small>8:00PM</small>Gemara Bekiut<small style='margin-top:6px'>9:15PM</small>Mishmar Speaker", 1, "")], None),
    ("10:00PM", [("", 1, ""), ("", 1, ""), ("Basketball League", 1, ""), ("", 1, ""), ("Mishmar Dinner", 1, "break")], None),
]
DAYS = {
    "sun": [("7:45AM", "Shahrit followed by breakfast", "t"), ("9:15AM", "Electives", ""), ("10:30AM", "Gemara Shiur", ""), ("12:45PM", "Parasha Shiur", ""), ("1:00PM", "Lunch Break", "break"), ("3:20PM", "Minha", "t"), ("3:45PM", "Halakha Shiur", ""), ("5:15PM", "Independent Learning Groups", ""), ("6:30PM", "Dinner Break", "break"), ("7:45PM", "Arbit", "t"), ("8:00PM", "Timely Topics", "")],
    "mon": [("7:45AM", "Shahrit followed by breakfast", "t"), ("9:15AM", "Electives", ""), ("10:30AM", "Gemara Shiur", ""), ("12:45PM", "Parasha Shiur", ""), ("1:00PM", "Lunch Break", "break"), ("3:20PM", "Minha", "t"), ("3:45PM", "Halakha Shiur", ""), ("5:15PM", "Independent Learning Groups", ""), ("6:30PM", "Dinner Break", "break"), ("7:45PM", "Arbit", "t"), ("8:00PM", "Gemara Bekiut", "")],
    "tue": [("7:45AM", "Shahrit followed by breakfast", "t"), ("9:15AM", "Electives", ""), ("10:30AM", "Gemara Shiur", ""), ("12:00PM", "Tur / Bet Yosef Shiur with Rabbi Alouf", ""), ("1:00PM", "Lunch Break", "break"), ("4:00PM", "Minha", "t"), ("4:20PM", "Parashat HaShabuah", ""), ("5:15PM", "Pirke Abot", ""), ("6:00PM", "Dinner Break", "break"), ("7:45PM", "Arbit", "t"), ("8:00PM", "Gemara Bekiut", ""), ("10:00PM", "Basketball League", "")],
    "wed": [("7:45AM", "Shahrit followed by breakfast", "t"), ("9:15AM", "Electives", ""), ("10:30AM", "Gemara Shiur", ""), ("12:00PM", "Tur / Bet Yosef Shiur with Rabbi Alouf", ""), ("1:00PM", "Lunch Break", "break"), ("3:20PM", "Minha", "t"), ("3:45PM", "Halakha Shiur", ""), ("5:15PM", "Independent Learning Groups", ""), ("6:30PM", "Dinner Break", "break"), ("7:45PM", "Arbit", "t"), ("8:00PM", "Gemara Bekiut", "")],
    "thu": [("7:45AM", "Shahrit followed by breakfast", "t"), ("9:15AM", "Electives", ""), ("10:30AM", "Gemara Shiur", ""), ("12:45PM", "Parasha Shiur", ""), ("1:00PM", "Lunch Break", "break"), ("3:20PM", "Minha", "t"), ("3:45PM", "Halakha Shiur", ""), ("5:15PM", "Independent Learning Groups", ""), ("6:30PM", "Dinner Break", "break"), ("7:45PM", "Arbit", "t"), ("8:00PM", "Gemara Bekiut", ""), ("9:15PM", "Mishmar Speaker", ""), ("10:00PM", "Mishmar Dinner", "break")],
    "fri": [("7:45AM", "Shahrit followed by breakfast", "t"), ("10:00AM", "Football League", "")],
}
EVENTS = ["Three Day Eilat Trip", "Hebron Shabbaton", "Safed Shabbaton", "Gush Etzion Shabbaton", "Hiking Masada", "Yam LeYam", "Selihot at the Kotel",
          "Tour of City of David", "Kotel Tunnels", "Kayaking Trip", "Yom HaAsmaut Celebrations", "Yom Yerushalayim Celebrations", "Purim Parties", "Hanukkah Parties",
          "Har Hertzl", "Yad Vashem Museum", "Ammunition Hill", "Machon HaMikdash", "Tu BiShbat Planting", "Lag LaOmer Trip", "Sisit Tying Workshop",
          "Food Packaging", "Shabuot Learning", "Hoshana Rabba Learning"]

def student_life():
    thead = "<thead><tr><th scope='col'><span class='sr'>Time</span></th>" + "".join("<th scope='col'>%s</th>" % d for d in ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]) + "</tr></thead>"
    rows = ""
    for i, (tm, cells, fri) in enumerate(SCHED_ROWS):
        tds = "".join("<td colspan='%d' class='%s'>%s</td>" % (span, "k-break" if k == "break" else "", txt) for txt, span, k in cells)
        if i == 0:
            tds += "<td>Shahrit followed by breakfast</td>"
        elif i == 1:
            tds += "<td rowspan='11' class='fri-top'><small>10:00AM</small>Football League</td>"
        rows += "<tr><th scope='row'>%s</th>%s</tr>" % (tm, tds)
    table = "<table class='week rv'><caption class='sr'>Sample weekly schedule</caption>%s<tbody>%s</tbody></table>" % (thead, rows)
    tabs = "".join("<button type='button' role='tab' data-day='%s' aria-selected='false'>%s</button>" % (d, d.capitalize()) for d in DAYS)
    lists = "".join("<ol class='daylist' data-day='%s' hidden>%s</ol>" % (d, "".join("<li><b>%s</b>%s</li>" % (t, E(w)) for t, w, k in items)) for d, items in DAYS.items())
    ev = "".join("<li class='rv'>%s</li>" % E(e) for e in EVENTS)
    body = """
<section class="band" id="schedule">
  <div class="wrap">%s
    <div class="days" role="tablist" aria-label="Day of the week">%s</div>%s%s
    <p class="note">Note that this is a sample schedule that is subject to change</p>
  </div>
</section>
<section class="band purple" id="events">
  <div class="wrap">%s<ul class="events">%s</ul>
  </div>
</section>
<section class="band lilac tight">
  <div class="wrap partner"><p style="margin:0;font-family:var(--serif);font-weight:800;font-size:24px">Code of Conduct</p><a class="btn gold" href="/codeofconduct">CLICK HERE</a></div>
</section>""" % (H("Sample Weekly Schedule", "h1"), tabs, table, lists,
                 H("Special Events", "h2", '<p class="lede">See below for some of the tiyulim, holiday celebrations, Shabbatons and special events we try to plan for our students each year, combining to make the year an incredible experience.</p>'), ev)
    page("/student-life.html", "Student Life", "/student-life", body)

# ---------------------------------------------------------------- CAMPUS
def gallery(imgs):
    out = ""
    for a, alt in imgs:
        big = hires(a, 1600)
        out += '<button type="button" aria-label="Enlarge photo"><img src="%s" data-full="%s" alt="%s" loading="lazy"></button>' % (big, big, E(alt or "Campus photo"))
    return out

LIGHTBOX = """<dialog class="lb" id="lb" aria-label="Photo viewer"><img id="lb-img" src="" alt="">
<div class="lb-nav"><button type="button" id="lb-prev" aria-label="Previous photo">‹</button><button type="button" id="lb-x" aria-label="Close">✕</button><button type="button" id="lb-next" aria-label="Next photo">›</button></div></dialog>"""

def campus():
    body = """
<section class="band purple">
  <div class="wrap">%s
    <p class="lede" style="font-family:var(--serif);font-weight:700;font-size:21px;color:#fff;margin-bottom:18px">Yeshivat Moreshet Yerushalayim is perfectly located in the heart of Jerusalem, in walking distance of so many iconic, historic and spiritual sites.</p>
    <p class="lede">Nestled in the picturesque streets of Nachlaot, Gan Saker (an enormous public park with many athletic fields) is right across the street. The fabled Shuk is a 5 minute walk. The Kotel? About 30 minutes. Ben Yehuda Street is about 12 minutes.</p>
  </div>
</section>
<iframe class="map" title="Map: Korazin Street 22, Jerusalem" loading="lazy" src="https://maps.google.com/maps?q=Korazin%%20St%%2022%%2C%%20Jerusalem%%2C%%20Israel&amp;z=16&amp;output=embed"></iframe>
<section class="band purple">
  <div class="wrap">%s<div class="slider"><div class="gallery">%s</div></div></div>
</section>%s""" % (H("Location, Location, Location", "h1"), H("Snapshots of our Campus"), gallery(pages["campus"]["imgs"]), LIGHTBOX)
    page("/campus.html", "Campus", "/campus", body)

# ---------------------------------------------------------------- APPLICATION
def application():
    checks = [
        ("visa", "Student visa", "You will be processed for a student visa shortly after the school year begins. Enter Israel on an ETA-IL.", "/visainformation", "Visa information"),
        ("insurance", "Medical insurance", "All students must carry full medical insurance. If your American health insurance does not apply in Israel, please see AIM.", "https://www.aim.co.il/apply-now", "AIM application"),
        ("phone", "Israeli phone", "While you may choose any service you wish, we recommend using HOTmobile.", "https://www.hotisraelsim.com/hot-mobile-Israel-sim-card", "HOTmobile"),
        ("linen", "Linens &amp; towels (optional)", "Order linen, towels and more delivered to the Yeshivah (Korazin 22, Jerusalem). Have it arrive one day before you do.", "", '<a href="https://www.blanketexpressplus.com/">Blanket Express</a> or <a href="https://www.israelxpress.com/">Israelxpress</a>'),
        ("pack", "Pack (no more than two suitcases)", "That is all that fits in a dorm room. Weekday, Shabbat, trip and miscellaneous lists are in the FAQ.", "/faq#packing", "Packing list"),
        ("conduct", "Read the Code of Conduct", "Including curfew, leaving the Yeshivah and visits.", "/codeofconduct", "Code of Conduct"),
    ]
    cl = "".join("""<div class="check rv"><div><b class="ct">%s</b><p>%s</p>%s</div></div>""" % (t, d, ('<a href="%s">%s ⟶</a>' % (h, l)) if h else '<span class="lk">%s</span>' % l) for i, t, d, h, l in checks)
    body = """
<section class="band wash" id="steps">
  <div class="wrap">%s
    <div class="steps">
      <div class="step rv"><div class="n">1</div><h3>Application</h3><p>Yeshivat Moreshet Yerushalayim participates in the Common Application process.</p><a class="btn purple" href="%s">OPEN THE APPLICATION</a></div>
      <div class="step rv"><div class="n">2</div><h3>Sign “Commitment to Attend”</h3><p>In your acceptance letter, you will receive a link to confirm your commitment to attend Yeshivat Moreshet Yerushalayim.</p></div>
      <div class="step rv"><div class="n">3</div><h3>Pay Deposit</h3><p>Once you have confirmed your commitment to attend, you will be billed for a deposit. Your spot for the upcoming school year is only confirmed upon payment of the deposit.</p></div>
    </div>
  </div>
</section>
<section class="band wash" id="checklist">
  <div class="wrap">%s
    <div class="checks">%s</div>
  </div>
</section>""" % (H("Application Steps", "h1"), APPLY, H("Before You Fly", "h2", '<p class="lede">Please review the information below to ensure a smooth transition to an incredible year.</p>'), cl)
    page("/application.html", "Application", "/application", body)

# ---------------------------------------------------------------- MEDIA
def media():
    order = ["Year 11, Issue 1", "Year in Review 5786", "Year 10, Issue 5", "Year 10, Issue 4", "Year 10, Issue 3", "Year 10, Issue 2", "Year 10, Issue 1", "Year in Review 5785", "Issue 4", "Issue 3", "Issue 2", "Issue 1"]
    def key(m):
        t = " ".join(m["lines"][:1]).replace("/", "").strip()
        for i, o in enumerate(order):
            if t.startswith(o):
                return i
        return 99
    cards = ""
    for m in sorted(mags, key=key):
        L = [x.replace("/", "").strip() for x in m["lines"]]
        if L[0].startswith("Year in Review"):
            title, sub, ded = L[0], L[1].replace("-", "–"), ""
        else:
            title, sub, ded = ("Year 9, " + L[0]) if L[0].startswith("Issue") else L[0], "", "\n".join(L[1:])
        cards += """<article class="mag rv"><a class="cv" href="%s" aria-label="Read %s"><img src="%s" alt="Cover of %s" loading="lazy"></a><div class="mt"><h3 class="t">%s</h3>%s%s</div><a class="btn purple" href="%s">READ THIS ISSUE</a></article>""" % (
            m["pdf"], E(title), hires(m["img"], 800), E(title), E(title), ('<div class="s">%s</div>' % E(sub)) if sub else "", ('<p class="d">%s</p>' % E(ded)) if ded else "", m["pdf"])
    ig = "".join('<a href="%s" aria-label="Open on Instagram"><img src="%s" alt="%s" loading="lazy"><span>%s</span></a>' % (p["link"], p["img"], E(p["caption"][:120]), E(p["date"] or "")) for p in insta)
    body = """
<section class="band lilac" id="shiurim">
  <div class="wrap shiur-wrap"><img class="shiur-img rv" src="@@SHIURIMG@@" alt="A student listening to a shiur with an earbud"><div class="shiur-tx">%s
    <p class="lede">Listen to recorded shiurim from our rabbis on Spotify. For sponsorship opportunities, contact <a style="color:#fff" href="mailto:Media@moreshetyerushalayim.com?subject=Sponsoring%%20Spotify%%20Class">Media@moreshetyerushalayim.com</a>.</p>
    <p style="text-align:center;margin:24px 0 0"><a class="btn gold" href="https://open.spotify.com/show/3qxWYUnkE2yQlAdpIBqewX">LISTEN ON SPOTIFY</a></p>
  </div></div>
</section>
<section class="band wash" id="magazine">
  <div class="wrap">%s<div class="mags">%s</div></div>
</section>
<section class="band" id="instagram">
  <div class="wrap">%s<div class="insta">%s</div>
  <p style="text-align:center;margin:24px 0 0"><a class="btn purple" href="%s">FOLLOW @MORESHET_YERUSHALAYIM</a></p></div>
</section>""" % (H("Recorded Shiurim", "h1"),
                 H("Moreshet Magazine", "h2", '<p class="lede">To sponsor an upcoming issue, contact <a href="mailto:office@moreshetyerushalayim.com">office@moreshetyerushalayim.com</a>.</p><a class="btn gold" href="https://docs.google.com/forms/d/e/1FAIpQLSe1nD46qdmTmh7BfT7m6Akg6kf49Y3-iHU5VHY8uCFwh-fwWQ/viewform">JOIN OUR MAILING LIST</a>'),
                 cards, H("Follow us on Instagram"), ig, IG)
    page("/media.html", "Media", "/media", body)

# ---------------------------------------------------------------- FAQ
PACK = {"Weekday": ["Polo shirts", "Button down shirts", "School pants", "Underwear, undershirts, socks", "Sisit", "Kippot", "Sweatshirts", "Casual shoes"],
        "Shabbat / Holidays": ["Dress pants", "Dress shirts", "Suit(s) and/or sports jacket(s)", "Tie", "Belt", "Dress shoes"],
        "Trips / Hikes": ["Bathing suit", "Shorts", "T-shirts", "Baseball cap", "Hiking sneakers", "Slides/sandals", "Duffle bag", "Small knapsack", "Sunscreen"],
        "Miscellaneous": ["Koracha", "Passport", "Winter jacket", "Rain coat", "Toiletry bag", "Toiletries (all American brands can be purchased in Israel)", "Medications (bring a copy of your prescriptions as well!)", "Mahazorim for holidays", "Adapters, electronics, chargers, headphones etc", "Battery/external charger for phone"]}

def faq():
    pack = '<div class="pack">' + "".join("<div><b>%s</b>%s</div>" % (k, "<br>".join(E(x) for x in v)) for k, v in PACK.items()) + "</div>"
    Q = [
        ("learning", "Learning &amp; Credits", [
            (False, "Who are the rabbis and teachers?", "<p>Many of our rabbis and teachers grew up in our community before making aliyah, so they know our families and our way of life. They are joined by leading Torah scholars in Israel. Together, they bring Torah to life for every student, in the Bet Midrash and well beyond it.</p><p>For more about our staff, <a href='/team'>click here</a>.</p>"),
            (False, "I’m excited to attend, but to be honest, the learning looks very intense. Does that mean Yeshivat Moreshet Yerushalayim isn’t for me?", "<p>Learning at Yeshivat Moreshet Yerushalayim is different from spending an entire day in school. Most learning takes place in interactive small groups, carefully designed to ensure a blend of abilities, interests and personalities. There are breaks throughout the day, allowing you to decompress and stretch, and return to the Bet Midrash refreshed and re-invigorated.</p>"),
            (False, "Can students receive college credits upon completing the year at Yeshivat Moreshet Yerushalayim?", "<p>There are two options for students to receive college credits:</p><p>1) If a student is enrolled in the <a href='https://www.yu.edu/israel-program'>Yeshiva University S. Daniel Abraham program</a>, they automatically receive a full year of credit upon entering Yeshiva University.</p><p>2) An official transcript can be sent to any college or university. Note that it is that institution’s choice whether or not to grant transfer credit. For more information, please contact our registrar at <a href='mailto:office@moreshetyerushalayim.com'>office@moreshetyerushalayim.com</a>.</p>"),
            (False, "I saw a lot of “free time” on the schedule. What do students usually do during that time?", "<p>Some use the time to learn. Others exercise in a nearby gym, unwind, spend time in beautiful Sacher Park, shop, or spend time with friends and family exploring Jerusalem through the eyes of a “local.”</p>"),
        ]),
        ("cost", "Cost &amp; Financial Aid", [
            (False, "What does the year cost?", "<p>Upon applying, families receive the full cost of the year, as it differs from year to year.</p>"),
            (False, "Is financial aid available at Yeshivat Moreshet Yerushalayim?", "<p>Students enrolled in the <a href='https://www.yu.edu/israel-program'>Yeshiva University S. Daniel Abraham</a> program receive the same financial aid they would receive when attending an American university. In addition, there is some community-funded need-based tuition assistance available. For further details, please contact our office at <a href='mailto:office@moreshetyerushalayim.com'>office@moreshetyerushalayim.com</a>.</p>"),
        ]),
        ("life", "Daily Life", [
            (False, "What are Shabbat’s like during the year?", "<p>Shabbat in Israel is a weekly experience not to be missed! In general, one out of three Shabbats are “In-Shabbat,” which means that the Yeshivah caters meals, has minyanim and offers programming throughout the Shabbat. On “Out-Shabbat,” students are hosted by faculty, friends and family. The dorms remain open during Out-Shabbat, allowing those who are eating within walking distance to sleep “at home.” Of course, our Shabbatonim, when we move the entire Yeshivah family to a hotel in a different area of Israel, are highlights of the year.</p>"),
            (False, "How’s the food at Yeshivat Moreshet Yerushalayim and what meals are covered?", "<p>Our food is delicious! Three meals a day are included. Breakfast is available in all dorms and the Bet Midrash. Lunch and dinner are catered. We often have deluxe sponsored meals for Mishmars and Siyumim. On holidays and Shabbat, our traditional favorites are served.</p>"),
            (False, "What are the dorms like?", "<p>Our dorms have between two and four students in a room with a bathroom attached. Dorms are cleaned by a cleaning crew on a regular basis. There is Wi-Fi access in all rooms.</p>"),
            (False, "How do we clean our clothes?", "<p>Every dorm has easy-to-use washing machines and dryers. There are also several laundry/dry cleaning establishments near the Yeshivah.</p>"),
            (False, "I've never packed for an entire year before. What do I bring?!", "<p>The first thing to remember is that you can buy things in Israel as well, so don’t worry. We recommend bringing no more than two suitcases; that’s all that will fit in the dorm room, and, in reality, is all you will need. You can buy linens etc. through a service like <a href='https://www.blanketexpressplus.com/'>Blanket Express</a> or <a href='https://www.israelxpress.com/'>Israelxpress</a>.</p><p>Here is our suggested packing list:</p>" + pack + "<p style='margin-top:12px'><b>Please do NOT bring x-box or other gaming consoles</b> as they are not permitted on the school's premises.</p>"),
            (False, "What phone plan should my son get?", "<p>While you may choose any service you wish, we recommend using <a href='https://www.hotisraelsim.com/hot-mobile-Israel-sim-card'>HOTmobile</a>.</p>"),
        ]),
        ("safety", "Health &amp; Safety", [
            (False, "What is security like at Yeshivat Moreshet Yerushalayim?", "<p>All premises are under constant video surveillance. All dorms are locked at all times. Safety procedures are reviewed at the beginning of the year, including shelter locations. Most of our staff are armed, carrying guns. Our madrichim have served in the army, and continue to be called up for reserve duty. The student WhatsApp group allows us to maintain close contact in case of emergency.</p>"),
            (False, "What happens if my son has a medical emergency?", "<p>Every student is required to carry full medical insurance. The Yeshivah is visited weekly by a doctor, who is available for non-emergency issues. In case of emergency, your child will be accompanied by an adult member of the staff to the doctor/emergency room/hospital (as determined by emergency response personnel), and will not be left alone at any time. Of course, parents will be notified immediately.</p>"),
            (False, "Is medical insurance required?", "<p>All students must carry full medical insurance while in attendance. If your American health insurance does not apply in Israel, please see <a href='https://www.aim.co.il/apply-now'>AIM</a>.</p>"),
        ]),
        ("parents", "Parents &amp; Travel", [
            (False, "Can I visit my son in Israel during the year?", "<p>Yes! We would love to have you join us for some of the learning as well! We just ask that you inform us prior to coming, and that you abide by the procedures specified in the <a href='/codeofconduct'>Code of Conduct</a> for visits.</p>"),
            (False, "How do parents stay updated during the year?", "<p>There are several ways to stay connected:</p><ul><li>Follow us on Instagram, <a href='https://www.instagram.com/moreshet_yerushalayim/'>@moreshet_yerushalayim</a>, for photos and highlights from the year.</li><li>A WhatsApp group strictly for parents to communicate with one another.</li><li><a href='"+WA+"'>Our updates WhatsApp group</a> for announcements from the Yeshivah.</li><li><a href='/media#magazine'>Moreshet Magazine</a>, with stories and photos from the year.</li></ul><p>To be added to the WhatsApp groups, contact <a href='mailto:office@moreshetyerushalayim.com'>office@moreshetyerushalayim.com</a>.</p>"),
        ]),
    ]
    secs = ""
    for cat, title, items in Q:
        secs += '<div data-cat="%s"><h3>%s</h3>' % (cat, title)
        for new, q, a in items:
            idattr = ' id="packing"' if q.startswith("I've never packed") else ""
            secs += "<details name='faq'%s><summary>%s%s</summary><div class='a'>%s</div></details>" % (idattr, E(q), "<span class='new'>NEW</span>" if new else "", a)
        secs += "</div>"
    topics = '<button type="button" data-topic="all" aria-pressed="true">All</button>' + "".join('<button type="button" data-topic="%s" aria-pressed="false">%s</button>' % (c, t) for c, t, _ in Q)
    body = """
<section class="band">
  <div class="wrap">%s
    <div class="faq-tools"><label class="sr" for="faq-q">Search the questions</label><input id="faq-q" type="search" placeholder="Search: Shabbat, laundry, credits…"><div class="filters" role="group" aria-label="Topic">%s</div></div>
    <div class="faq">%s<p id="faq-none" hidden>No questions match that search.</p></div>
  </div>
</section>
<section class="band purple tight"><div class="wrap partner"><p style="margin:0;font-family:var(--serif);font-weight:800;font-size:24px">Still have a question?</p><a class="btn gold" href="mailto:Office@moreshetyerushalayim.com">EMAIL THE OFFICE</a></div></section>""" % (H("Frequently Asked Questions", "h1"), topics, secs)
    page("/faq.html", "FAQ", "/faq", body)

# ---------------------------------------------------------------- ALUMNI
def alumni():
    logos = [a for a, b in pages["alumni_logos"]][1:]
    NEW = ["bmg-medical-halacha", "jersey-shore-hatzalah", "makom-torah", "mitnadev-israel", "rochel-leah-chesed-fund", "shaare-zion", "zoa", "gesher", "kollel"]
    for pos, n in zip([8, 11, 15, 19, 23, 27, 31, 36, 41], NEW):
        logos.insert(pos - 1, "/media/alumni-%s.webp" % n)
    lg = "".join('<li class="rv"><img src="%s" alt="Organization our alumni support" loading="lazy"></li>' % a for a in logos)
    body = """
<section class="band purple" id="giving"><div class="wrap"><div class="alum-top"><img class="alum-img rv" src="@@ALUMIMG@@" alt="Alumni with Rabbi Harold Sutton"><div class="alum-h">%s</div></div><ul class="logos">%s</ul></div></section>
<section class="band wash" id="transcript"><div class="wrap">%s<p style="text-align:center;margin:0"><a class="btn purple" href="%s">FILL OUT THE REQUEST FORM</a></p></div></section>
%s""" % (
        H("Our Alumni", "h1", '<p class="lede">Our alumni love to give back. Here are just a few places where they have made an impact since their year at Yeshivat Moreshet Yerushalayim:</p>'), lg,
        H("Request a Transcript", "h2", '<p class="lede">Need an official transcript sent to a college or university? Fill out our short form and our office will take care of it.</p>'), "https://docs.google.com/forms/d/e/1FAIpQLSdHzK1cipmzxFaKg4R-G5xciw-eaU1EetRMIppaGByibHWEVQ/viewform", quotes_band(False))
    page("/alumni.html", "Alumni", "/alumni", body)

# ---------------------------------------------------------------- DONATE
def donate():
    body = """
<section class="band purple">
  <div class="wrap give">
    <div class="rv"><h1 class="h1" style="color:var(--gold)">Support our School</h1><div class="rule" style="margin:16px 0 20px;background:#fff"></div>
      <p style="font-family:var(--serif);font-size:19px;line-height:1.7;color:#EFE9F5;margin:0">Your support of Yeshivat Moreshet Yerushalayim directly empowers the next generation of community Torah scholars, ensuring that our students receive the highest level of education and guidance. By donating, you help us continue to foster a vibrant community rooted in Jewish values, tradition, and intellectual growth, both in Israel and beyond.</p></div>
    <div class="card rv">
      <b>American Friends of Yeshivat Moreshet Yerushalayim</b>
      <span>EIN: 87-1062571</span><span>1385 Broadway, 16th floor<br>New York, NY 10018</span>
      <form action="https://www.paypal.com/donate" method="post" target="_top" style="margin-top:8px">
        <input type="hidden" name="hosted_button_id" value="S472FAZV2S7W2">
        <input type="image" src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" name="submit" title="PayPal - The safer, easier way to pay online!" alt="Donate with PayPal button">
      </form>
    </div>
  </div>
</section>"""
    page("/donate.html", "Donate", "/donate", body)

# ---------------------------------------------------------------- memorial + text pages
def memorial(path, title, blocks, portrait, gal, cur=""):
    text = "".join("<p>%s</p>" % rich(t) for k, t in blocks if k == "p")
    galhtml = ('<section class="band lilac"><div class="wrap"><div class="slider"><div class="gallery">%s</div></div></div></section>%s' % (gallery(gal), LIGHTBOX)) if gal else ""
    body = """
<section class="band purple"><div class="wrap memorial">
  <div class="ph rv"><img src="%s" alt="%s"></div>
  <div class="rv"><h1 class="h1">%s</h1><div class="rule" style="margin:16px 0 22px;background:#fff"></div>%s</div>
</div></section>%s""" % (hires(portrait, 900), E(title), E(title), text, galhtml)
    page(path, title.replace(' A"H', ""), cur, body)

def textpage(path, title, blocks, cur):
    out = ""
    in_list = False
    for k, t in blocks[1:]:
        t2 = rich(t)
        if k == "li":
            if not in_list:
                out += "<ul>"; in_list = True
            out += "<li>%s</li>" % t2
            continue
        if in_list:
            out += "</ul>"; in_list = False
        if re.fullmatch(r"[A-Za-z/ ]{3,30}:", t.strip()):
            out += "<h3>%s</h3>" % t2[:-1]
        elif t.startswith("Failure to comply with this policy may result in expulsion. Visitors:"):
            out += "<p>Failure to comply with this policy may result in expulsion.</p><h3>Visitors</h3>"
        elif t.startswith("Alcohol/Smoking:"):
            out += "<h3>Alcohol / Smoking</h3><p>%s</p>" % t2[len("Alcohol/Smoking:"):].strip()
        else:
            out += "<p>%s</p>" % t2
    if in_list:
        out += "</ul>"
    body = '<section class="band lilac tight"><div class="wrap">%s</div></section><section class="band"><div class="wrap prose rv">%s</div></section>' % (H(title, "h1"), out)
    page(path, title, cur, body)

def notfound():
    body = '<section class="band purple" style="min-height:50vh"><div class="wrap">%s<p class="lede">We can’t find the page you’re looking for. Check the URL, or head back home.</p><p style="text-align:center;margin-top:24px"><a class="btn gold" href="/">GO HOME</a></p></div></section>' % H("There’s Nothing Here…", "h1")
    page("/404.html", "Page not found", "", body)

if __name__ == "__main__":
    logo = Image.open(SP + "/media/ce1b8c14c1-Yeshivat_Moreshet_Yerushalayim.webp")
    hl = hires("a4810d_" + "x", 600)  # no-op guard
    # sharper logo from the captured header
    lm = re.search(r"https://static\.wixstatic\.com/media/(a4810d_[a-f0-9]{32})~mv2\.(\w+)/[^\"]*Yeshivat%20Moreshet%20Yerushalayim", open(CAP + "/desktop/home/page.html").read())
    if lm:
        r = requests.get("https://static.wixstatic.com/media/%s~mv2.%s/v1/fit/w_400,h_400,q_90/x.%s" % (lm.group(1), lm.group(2), lm.group(2)), timeout=60)
        Image.open(io.BytesIO(r.content)).save(OUT + LOGO, quality=90)
    else:
        logo.save(OUT + LOGO)
    home(); team_page(); student_life(); campus(); application(); media(); faq(); alumni(); donate(); notfound()
    oi = pages["ovadiabuddysutton"]["imgs"]
    memorial("/ovadiabuddysutton.html", 'Ovadia Buddy Sutton A"H', rj["ovadiabuddysutton"], oi[0][0], oi[1:11])
    ri = pages["raymondmosseri"]["imgs"]
    memorial("/raymondmosseri.html", 'Raymond Mosseri A"H', [], ri[0][0], ri[1:])
    si = pages["copy-of-ovaida-buddy-sutton"]["imgs"]
    memorial("/copy-of-ovaida-buddy-sutton.html", 'Saul E. Ashkenazi A"H', rj["copy-of-ovaida-buddy-sutton"], si[0][0], [])
    textpage("/visainformation.html", "Visa Information", rj["visainformation"], "/application")
    textpage("/codeofconduct.html", "Code of Conduct", rj["codeofconduct"], "/student-life")
    print("done")
