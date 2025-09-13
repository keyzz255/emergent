export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 1) coba serve file dari assets (frontend/build)
    const assetResp = await env.ASSETS.fetch(request);
    if (assetResp.status !== 404) return assetResp;

    // 2) SPA fallback: route yg bukan file diarahkan ke /index.html
    if (!url.pathname.includes(".")) {
      const indexReq = new Request(new URL("/index.html", url), request);
      return env.ASSETS.fetch(indexReq);
    }

    return new Response("Not Found", { status: 404 });
  },
};
