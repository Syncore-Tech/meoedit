// Static assets answer a Range request with the whole file (200). Safari on iPhone
// only plays <video> when it gets 206 Partial Content, so /docs/* goes through here.
export default {
  async fetch(request, env) {
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
