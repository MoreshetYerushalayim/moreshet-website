// Latest posts from @moreshet_yerushalayim via the official Instagram API.
// The access key lives in the Cloudflare setting IG_TOKEN (never in this code).
const IG_USER = "17841403152425458";
const FIELDS = "id,caption,media_type,media_url,thumbnail_url,permalink,timestamp";

export async function onRequestGet({ request, env, waitUntil }) {
  const cache = caches.default;
  const key = new Request(new URL("/api/instagram?v=1", request.url).toString());
  const hit = await cache.match(key);
  if (hit) return hit;
  if (!env.IG_TOKEN) return json({ error: "not configured", posts: [] }, 503);
  const api = `https://graph.facebook.com/v21.0/${IG_USER}/media?fields=${FIELDS}&limit=9&access_token=${encodeURIComponent(env.IG_TOKEN)}`;
  const r = await fetch(api);
  if (!r.ok) return json({ error: "instagram " + r.status, posts: [] }, 502);
  const d = await r.json();
  const posts = (d.data || []).map(p => ({
    link: p.permalink,
    img: p.media_type === "VIDEO" ? p.thumbnail_url : p.media_url,
    caption: (p.caption || "").slice(0, 140),
    date: p.timestamp,
  })).filter(p => p.img);
  const res = json({ posts }, 200, "public, max-age=600");
  waitUntil(cache.put(key, res.clone()));
  return res;
}

function json(obj, status, cc = "no-store") {
  return new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json", "cache-control": cc } });
}
