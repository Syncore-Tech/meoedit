// Static assets answer a Range request with the whole file (200). Safari on iPhone
// only plays <video> when it gets 206 Partial Content, so /docs/* goes through here.
// /ping counts installs: the engine calls it once per version (skill/engine/meo/ping.py).
// /meomeo/* is the Meomeo app (its own Worker, repo Syncore-Tech/meomeo), reached through a service binding.
const OSES = ["mac", "windows", "linux", "other"];
const CMDS = ["doctor", "templates", "probe", "thumbs", "video", "image", "capcut"];

async function ping(request, env) {
  const url = new URL(request.url);
  const v = url.searchParams.get("v") ?? "";
  const ua = request.headers.get("user-agent") ?? "";
  // Only the engine sends "meoedit/<version>"; anything else (scanners, browsers) is not counted.
  if (request.method !== "GET" || !/^\d{1,3}\.\d{1,3}\.\d{1,3}$/.test(v) || ua !== `meoedit/${v}`) {
    return new Response(null, { status: 404 });
  }
  const os = OSES.includes(url.searchParams.get("os")) ? url.searchParams.get("os") : "other";
  const cmd = CMDS.includes(url.searchParams.get("cmd")) ? url.searchParams.get("cmd") : "other";
  const country = /^[A-Z]{2}$/.test(request.cf?.country ?? "") ? request.cf.country : "XX";
  const day = new Date().toISOString().slice(0, 10);
  await env.DB.prepare(
    "INSERT INTO pings (day, version, os, cmd, country, n) VALUES (?, ?, ?, ?, ?, 1) " +
      "ON CONFLICT (day, version, os, cmd, country) DO UPDATE SET n = n + 1",
  )
    .bind(day, v, os, cmd, country)
    .run();
  return new Response(null, { status: 204 });
}

export default {
  async fetch(request, env) {
    const path = new URL(request.url).pathname;
    if (path === "/ping") return ping(request, env);
    if (path === "/meomeo" || path.startsWith("/meomeo/")) return env.MEOMEO.fetch(request);
    const res = await env.ASSETS.fetch(request);
    const range = request.headers.get("range");
    const headers = new Headers(res.headers);
    headers.set("accept-ranges", "bytes");
    if (!range || request.method !== "GET" || res.status !== 200) {
      return new Response(res.body, { status: res.status, headers });
    }
    const buf = await res.arrayBuffer();
    const size = buf.byteLength;
    const m = /^bytes=(\d*)-(\d*)$/.exec(range.trim());
    let start, end;
    if (m && m[1] === "" && m[2] !== "") {
      start = Math.max(size - Number(m[2]), 0);
      end = size - 1;
    } else if (m && m[1] !== "") {
      start = Number(m[1]);
      end = m[2] === "" ? size - 1 : Math.min(Number(m[2]), size - 1);
    }
    if (start === undefined || start > end || start >= size) {
      headers.set("content-range", `bytes */${size}`);
      headers.delete("content-length");
      return new Response(null, { status: 416, headers });
    }
    headers.set("content-range", `bytes ${start}-${end}/${size}`);
    headers.set("content-length", String(end - start + 1));
    return new Response(buf.slice(start, end + 1), { status: 206, headers });
  },
};
