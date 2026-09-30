import handle from '../server/trace-api.mjs';

// Single serverless entry point. vercel.json rewrites every /api/* request here
// and passes the original path as ?path=..., which is restored below.
export default async function handler(req, res) {
  process.env.TRACE_SERVER_MODE = 'vercel';
  try {
    const u = new URL(req.url, 'http://localhost');
    const p = u.searchParams.get('path');
    if (p !== null) {
      u.searchParams.delete('path');
      req.url = '/api/' + p.replace(/^\/+/, '') + u.search;
    }
    return await handle(req, res);
  } catch (e) {
    res.statusCode = 500;
    res.setHeader('content-type', 'application/json');
    res.end(JSON.stringify({ error: { code: 'INTERNAL_ERROR', message: e?.message || 'Server error' } }));
  }
}
