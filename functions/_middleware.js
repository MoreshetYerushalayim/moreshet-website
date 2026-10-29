// Cloudflare Pages middleware: phones get the phone layout at the SAME address,
// exactly like Wix (which picks desktop or mobile layout from the browser type).
const PHONE = /iPhone|iPod|Android.*Mobile|Windows Phone|BlackBerry|BB10|Opera Mini|IEMobile|webOS/i;

// Magazine PDFs too large for one Cloudflare Pages file (25 MB limit) are stored as
// numbered pieces in /_chunks/ and joined back together here, at their original Wix address.
// [disposition, download name, number of pieces, total bytes]
const BIG_PDFS = {
  "a4810d_0a2ac0a49015432e97194e7aacd13d0c.pdf": ["attachment", "Moreshet Magazine Issue 1.pdf", 6, 131345459],
  "a4810d_6a7eefba1cb041ab9548a85ebc18521c.pdf": ["inline", "Yeshivat Moreshet Yerushalayim Year in Review 2025.pdf", 2, 30841616],
  "a4810d_6de6c1601d5149d591bd0251e2135685.pdf": ["inline", "Moreshet Magazine Issue 2.pdf", 2, 34022263],
  "a4810d_7a1a5581815e4ad8a7d9fd9247bebe7f.pdf": ["attachment", "Moreshet Magazine Year 10- Issue 2.pdf", 4, 76924468],
  "a4810d_7a252b826a3047d0a0e1825cbe5009d8.pdf": ["inline", "Yeshivat Moreshet Yerushalayim Year in Review 2026.pdf", 2, 41244014],
  "a4810d_841ea3f0d091452995f9bd5d4b9ce60d.pdf": ["inline", "Moreshet Magazine Year 10- Issue 4.pdf", 2, 27088765],
  "a4810d_ce57eade9be7478e85f132686a30684b.pdf": ["inline", "Moreshet Magazine Issue 3.pdf", 2, 40815816],
  "a4810d_f1286e7b69654978be30c2e0121dda66.pdf": ["attachment", "Moreshet Magazine Year 10- Issue 3.pdf", 4, 74042895],
};

function bigPdf(name, ctx) {
  const [mode, title, parts, size] = BIG_PDFS[name];
  const origin = new URL(ctx.request.url).origin;
  const { readable, writable } = new FixedLengthStream(size);
  ctx.waitUntil((async () => {
    for (let i = 0; i < parts; i++) {
      const r = await ctx.env.ASSETS.fetch(new URL(`/_chunks/${name}.${String(i).padStart(3, "0")}`, origin));
      await r.body.pipeTo(writable, { preventClose: i < parts - 1 });
    }
  })());
  const h = new Headers();
  h.set("Content-Type", "application/pdf");
  h.set("Content-Length", String(size));
  h.set("Content-Disposition", `${mode}; filename="${encodeURIComponent(title)}"; filename*=UTF-8''${encodeURIComponent(title)}`);
  h.set("Cache-Control", "public, max-age=86400");
  return new Response(readable, { status: 200, headers: h });
}

export async function onRequest(ctx) {
  const url = new URL(ctx.request.url);
  const p = url.pathname;
  const m = p.match(/^\/_files\/ugd\/([^/]+\.pdf)$/);
  if (m && BIG_PDFS[m[1]]) return bigPdf(m[1], ctx);
  const ua = ctx.request.headers.get("user-agent") || "";
  const isPage = !p.startsWith("/_m/") && !/\.[a-z0-9]+$/i.test(p);
  if (!isPage) return ctx.next();
  if (PHONE.test(ua)) {
    const target = p === "/" ? "/_m/index" : "/_m" + p.replace(/\/$/, "");
    let r = await ctx.env.ASSETS.fetch(new URL(target, url.origin));
    let status = 200;
    if (!r.ok) {
      const real = await ctx.next();
      if (real.status !== 404) return real; // e.g. redirects
      r = await ctx.env.ASSETS.fetch(new URL("/_m/404", url.origin));
      status = 404;
    }
    const h = new Headers(r.headers);
    h.set("Vary", "User-Agent");
    return new Response(r.body, { status, headers: h });
  }
  const res = await ctx.next();
  const h = new Headers(res.headers);
  h.set("Vary", "User-Agent");
  return new Response(res.body, { status: res.status, headers: h });
}
