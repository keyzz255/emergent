export const onRequest = async ({ request, env }) => {
  const url = new URL(request.url);

  // Forward path apa adanya (termasuk prefix /api) ke backend Render
  const target = new URL(url.pathname + url.search, env.UPSTREAM_API);

  const init: RequestInit = {
    method: request.method,
    headers: request.headers,
    body: ["GET","HEAD"].includes(request.method)
      ? undefined
      : await request.arrayBuffer(), // aman untuk POST/PUT
  };

  const resp = await fetch(target.toString(), init);

  // Same-origin feel + aman buat browser
  const headers = new Headers(resp.headers);
  headers.set("Access-Control-Allow-Origin", url.origin);
  headers.set("Access-Control-Allow-Credentials", "true");

  return new Response(resp.body, { status: resp.status, headers });
};
