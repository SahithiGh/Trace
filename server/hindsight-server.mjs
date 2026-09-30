import http from 'node:http';
import { URL } from 'node:url';

const PORT = Number(process.env.HINDSIGHT_PORT || 8787);
const BASE = (process.env.HINDSIGHT_BASE_URL || 'https://api.hindsight.vectorize.io').replace(/\/$/, '');
const KEY = process.env.HINDSIGHT_API_KEY || '';
const BANK = process.env.HINDSIGHT_BANK_ID || 'trace-demo';

function send(res, status, body) {
  res.writeHead(status, {'content-type':'application/json','access-control-allow-origin':'*'});
  res.end(JSON.stringify(body));
}
async function body(req) { const chunks=[]; for await (const c of req) chunks.push(c); return JSON.parse(Buffer.concat(chunks).toString() || '{}'); }
async function hindsight(path, payload) {
  if (!KEY) return { configured:false, results:[], message:'Hindsight is not configured. TRACE is running in local demo memory mode.' };
  const r = await fetch(`${BASE}/v1/default/banks/${encodeURIComponent(BANK)}${path}`, {
    method:'POST', headers:{'Authorization':`Bearer ${KEY}`,'Content-Type':'application/json'}, body:JSON.stringify(payload)
  });
  const text = await r.text(); let data; try { data=JSON.parse(text); } catch { data={raw:text}; }
  if (!r.ok) throw new Error(data?.detail || `Hindsight request failed (${r.status})`);
  return { configured:true, ...data };
}
const server = http.createServer(async (req,res)=>{
  if (req.method==='OPTIONS') { res.writeHead(204, {'access-control-allow-origin':'*','access-control-allow-methods':'POST,OPTIONS','access-control-allow-headers':'content-type'}); return res.end(); }
  try {
    const url = new URL(req.url, `http://localhost:${PORT}`);
    if (req.method==='GET' && url.pathname==='/api/health') return send(res,200,{ok:true,configured:Boolean(KEY),bankId:BANK});
    if (req.method!=='POST') return send(res,404,{error:'Not found'});
    const data = await body(req);
    if (url.pathname==='/api/hindsight/retain') return send(res,200,await hindsight('/memories', {items:[{content:data.content, context:data.context, timestamp:data.timestamp}], async:false}));
    if (url.pathname==='/api/hindsight/recall') return send(res,200,await hindsight('/memories/recall', {query:data.query, trace:true}));
    if (url.pathname==='/api/hindsight/reflect') return send(res,200,await hindsight('/reflect', {query:data.query}));
    return send(res,404,{error:'Not found'});
  } catch (e) { return send(res,500,{error:e?.message || 'Server error'}); }
});
server.listen(PORT,()=>console.log(`TRACE Hindsight bridge listening on http://localhost:${PORT}`));
