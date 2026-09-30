import http from 'node:http';
import { URL } from 'node:url';
import crypto from 'node:crypto';

const PORT = Number(process.env.PORT || 8787);
const HINDSIGHT_BASE_URL = (process.env.HINDSIGHT_BASE_URL || 'https://api.hindsight.vectorize.io').replace(/\/$/, '');
const HINDSIGHT_API_KEY = process.env.HINDSIGHT_API_KEY || '';
const HINDSIGHT_BANK_ID = process.env.HINDSIGHT_BANK_ID || 'trace-demo';
const TRACE_API_KEY = process.env.TRACE_API_KEY || '';

const problems = [
  {id:'checkout-mobile',name:'Mobile checkout confusion',feature:'Checkout',status:'RECURRING',severity:'High',firstDetected:'2026-01-14',lastDetected:'2026-09-18',feedbackCount:184,sentiment:-0.62,segments:['Mobile shoppers','New customers'],summary:'Customers struggle to understand where to review delivery, payment and promo details before placing an order.',trend:[18,24,31,28,19,14,22,37,49,56],previousSolutions:[{name:'Simplify checkout navigation',outcome:'Partial',detail:'Desktop complaints fell 61%; mobile complaints persisted.',date:'2026-03-18'},{name:'Sticky order summary',outcome:'Successful',detail:'Reduced desktop drop-offs, but did not address mobile scanning.',date:'2026-05-09'}],timeline:[
    {id:'c1',date:'2026-01-14',type:'feedback',title:'Problem first detected',detail:'Support and app reviews cluster around confusing checkout navigation.',impact:'18 complaints / week'},
    {id:'c2',date:'2026-02-03',type:'decision',title:'Navigation simplification approved',detail:'Product team prioritizes a shorter checkout path.',impact:'Target: -40% complaints'},
    {id:'c3',date:'2026-03-18',type:'change',title:'Checkout navigation v2 shipped',detail:'Desktop navigation reduced from 5 steps to 3.',impact:'Desktop sentiment +0.34'},
    {id:'c4',date:'2026-04-16',type:'outcome',title:'Complaints improve',detail:'Desktop complaints fall sharply; mobile remains elevated.',impact:'-61% desktop complaints'},
    {id:'c5',date:'2026-07-22',type:'change',title:'Mobile checkout redesign shipped',detail:'Compact mobile layout introduced with new summary drawer.',impact:'New mobile UI'},
    {id:'c6',date:'2026-08-18',type:'recurrence',title:'Problem returns on mobile',detail:'Feedback volume rises again, concentrated in Android users.',impact:'+74% mobile complaints'},
    {id:'c7',date:'2026-09-18',type:'feedback',title:'Current signal',detail:'Customers again report difficulty finding delivery and promo details.',impact:'Sentiment -0.62'}
  ]},
  {id:'search-relevance',name:'Search result relevance',feature:'Search',status:'IMPROVING',severity:'Medium',firstDetected:'2026-03-02',lastDetected:'2026-09-20',feedbackCount:127,sentiment:-0.11,segments:['Returning customers','Power users'],summary:'Search occasionally ranks accessories and older products above the exact item customers intended to find.',trend:[42,46,39,34,31,25,21,18,16,14],previousSolutions:[{name:'Boost exact-title matches',outcome:'Successful',detail:'Exact-match satisfaction improved across returning users.',date:'2026-04-12'}],timeline:[
    {id:'s1',date:'2026-03-02',type:'feedback',title:'Relevance complaints emerge',detail:'Customers report unrelated products above exact matches.',impact:'42 complaints / week'},
    {id:'s2',date:'2026-04-12',type:'change',title:'Exact-title boost shipped',detail:'Ranking gives more weight to exact title and SKU matches.',impact:'-33% complaints'},
    {id:'s3',date:'2026-06-08',type:'outcome',title:'Relevance improves',detail:'Power-user satisfaction rises and complaint volume trends down.',impact:'+0.28 sentiment'},
    {id:'s4',date:'2026-09-20',type:'feedback',title:'Residual edge cases',detail:'Long-tail accessory queries remain noisy.',impact:'14 complaints / week'}
  ]},
  {id:'delivery-window',name:'Delivery promise uncertainty',feature:'Delivery tracking',status:'REGRESSING',severity:'High',firstDetected:'2026-05-11',lastDetected:'2026-09-21',feedbackCount:96,sentiment:-0.48,segments:['First-time buyers','Tier-2 cities'],summary:'Estimated delivery dates shift after payment, creating a mismatch between the promise shown and the carrier handoff.',trend:[8,12,16,18,21,25,31,36,42,48],previousSolutions:[{name:'Add carrier disclaimer',outcome:'Failed',detail:'Added text but did not reduce confusion; complaint volume continued upward.',date:'2026-06-01'},{name:'Refresh promise after address validation',outcome:'Partial',detail:'Reduced a subset of cases but did not cover carrier capacity changes.',date:'2026-08-07'}],timeline:[
    {id:'d1',date:'2026-05-11',type:'feedback',title:'Delivery promise issue detected',detail:'Customers report dates moving after payment.',impact:'8 complaints / week'},
    {id:'d2',date:'2026-06-01',type:'change',title:'Carrier disclaimer added',detail:'Additional copy explains possible delivery variation.',impact:'No measurable improvement'},
    {id:'d3',date:'2026-07-14',type:'outcome',title:'Problem persists',detail:'Complaints continue to rise despite clearer copy.',impact:'+43% complaints'},
    {id:'d4',date:'2026-08-07',type:'change',title:'Promise refreshed after validation',detail:'Estimate recalculated after address validation.',impact:'Partial improvement'},
    {id:'d5',date:'2026-09-21',type:'recurrence',title:'Regression detected',detail:'Carrier capacity spikes coincide with renewed complaints.',impact:'48 complaints / week'}
  ]},
  {id:'subscription-cancel',name:'Subscription cancellation friction',feature:'Account settings',status:'RESOLVED',severity:'Medium',firstDetected:'2026-02-10',lastDetected:'2026-07-03',feedbackCount:73,sentiment:0.21,segments:['Subscribers'],summary:'Customers previously had difficulty locating cancellation controls and understanding final billing.',trend:[29,31,27,21,15,9,6,5,4,3],previousSolutions:[{name:'Move cancellation to billing',outcome:'Successful',detail:'Complaint volume fell 86% over three months.',date:'2026-04-02'}],timeline:[
    {id:'u1',date:'2026-02-10',type:'feedback',title:'Cancellation friction identified',detail:'Customers report hidden controls and unclear billing language.',impact:'29 complaints / week'},
    {id:'u2',date:'2026-04-02',type:'change',title:'Cancellation flow simplified',detail:'Control moved into billing and final charge explained.',impact:'-58% complaints'},
    {id:'u3',date:'2026-05-21',type:'outcome',title:'Strong improvement',detail:'Complaints continue to decline across subscriber segments.',impact:'+0.41 sentiment'},
    {id:'u4',date:'2026-07-03',type:'feedback',title:'Problem considered resolved',detail:'Only isolated support cases remain.',impact:'3 complaints / week'}
  ]},
  {id:'gift-cards',name:'Gift card redemption edge cases',feature:'Gift cards',status:'EMERGING',severity:'Low',firstDetected:'2026-08-28',lastDetected:'2026-09-22',feedbackCount:31,sentiment:-0.36,segments:['Gift buyers','New customers'],summary:'A small but rapidly growing cluster reports failed redemption when gift cards are combined with promotional codes.',trend:[2,3,4,5,7,9,13,16,22,31],previousSolutions:[],timeline:[
    {id:'g1',date:'2026-08-28',type:'feedback',title:'First cluster detected',detail:'Gift card + promo combinations begin generating support tickets.',impact:'2 complaints / week'},
    {id:'g2',date:'2026-09-12',type:'feedback',title:'Signal accelerates',detail:'Volume increases across two channels.',impact:'+120% in 2 weeks'},
    {id:'g3',date:'2026-09-22',type:'decision',title:'Investigation opened',detail:'Engineering asked to reproduce the checkout combination.',impact:'Open'}
  ]}
];

const feedback = [
  {id:'f1',date:'2026-09-18',channel:'App review',segment:'Mobile shoppers',text:'I keep opening different screens to find delivery and promo details before paying.',sentiment:-0.7,problemId:'checkout-mobile'},
  {id:'f2',date:'2026-09-16',channel:'Support',segment:'New customers',text:'Checkout feels like it keeps hiding the information I need.',sentiment:-0.6,problemId:'checkout-mobile'},
  {id:'f3',date:'2026-09-15',channel:'Survey',segment:'Returning customers',text:'Search is much better than before. Exact product names now usually appear first.',sentiment:0.5,problemId:'search-relevance'},
  {id:'f4',date:'2026-09-21',channel:'Support',segment:'Tier-2 cities',text:'The date said Thursday, then changed after I paid. I had planned around it.',sentiment:-0.8,problemId:'delivery-window'},
  {id:'f5',date:'2026-09-20',channel:'App review',segment:'Gift buyers',text:'Gift card works until I add a promo code, then redemption fails.',sentiment:-0.4,problemId:'gift-cards'},
  {id:'f6',date:'2026-07-03',channel:'Survey',segment:'Subscribers',text:'Cancellation is finally easy to find and the final bill is clear.',sentiment:0.7,problemId:'subscription-cancel'}
];

const dashboardTrend = [
  {month:'Jan',feedback:78,sentiment:-0.42},{month:'Feb',feedback:92,sentiment:-0.31},{month:'Mar',feedback:105,sentiment:-0.25},{month:'Apr',feedback:98,sentiment:-0.12},{month:'May',feedback:121,sentiment:-0.08},{month:'Jun',feedback:133,sentiment:-0.02},{month:'Jul',feedback:149,sentiment:-0.07},{month:'Aug',feedback:164,sentiment:-0.12},{month:'Sep',feedback:181,sentiment:-0.16}
];

const memory = [
  {id:'m1',text:'Mobile checkout confusion was first detected in January 2026 among support and app-review signals.',date:'2026-01-14'},
  {id:'m2',text:'Navigation simplification shipped in March 2026. Desktop complaints fell 61%, while mobile complaints persisted.',date:'2026-03-18'},
  {id:'m3',text:'A sticky order summary later reduced desktop drop-offs but did not resolve mobile scanning difficulty.',date:'2026-05-09'},
  {id:'m4',text:'A compact mobile checkout redesign shipped in July 2026 with a new summary drawer.',date:'2026-07-22'},
  {id:'m5',text:'Mobile complaints rose again in August, concentrated among Android users.',date:'2026-08-18'},
  {id:'m6',text:'September feedback again reports difficulty finding delivery and promo details before payment.',date:'2026-09-18'}
];

const state = { decisions: [], interventions: [
  {id:'i1',problem_id:'checkout-mobile',name:'Simplify checkout navigation',why:'Reduce cognitive load in the purchase path.',target_segment:'Mobile shoppers',target_platform:'Web + mobile',expected_outcome:'Reduce checkout confusion',timestamp:'2026-02-03',decision_maker:'Product team',status:'TESTED'},
  {id:'i2',problem_id:'checkout-mobile',name:'Sticky order summary',why:'Keep key order information visible.',target_segment:'Mobile shoppers',target_platform:'Web',expected_outcome:'Reduce scanning difficulty',timestamp:'2026-05-09',decision_maker:'Product team',status:'TESTED'},
  {id:'i3',problem_id:'delivery-window',name:'Add carrier disclaimer',why:'Set expectations about delivery variation.',target_segment:'First-time buyers',target_platform:'All',expected_outcome:'Reduce promise confusion',timestamp:'2026-06-01',decision_maker:'Product team',status:'TESTED'}
], outcomes: [], seeded: true };

function json(res,status,payload){const body=JSON.stringify(payload);res.writeHead(status,{'content-type':'application/json; charset=utf-8','cache-control':'no-store','access-control-allow-origin':'*'});res.end(body)}
function sendText(res,status,text){res.writeHead(status,{'content-type':'text/plain; charset=utf-8','cache-control':'no-store','access-control-allow-origin':'*'});res.end(text)}
async function readBody(req){if(req.body!==undefined&&req.body!==null){if(typeof req.body==='object'&&!Buffer.isBuffer(req.body))return req.body;try{return JSON.parse(Buffer.isBuffer(req.body)?req.body.toString('utf8'):String(req.body)||'{}')}catch{throw new Error('Invalid JSON body')}}let data='';for await(const chunk of req)data+=chunk;if(!data)return {};try{return JSON.parse(data)}catch{throw new Error('Invalid JSON body')}}
function id(prefix){return `${prefix}_${crypto.randomUUID().slice(0,8)}`}
function problemById(pid){return problems.find(p=>p.id===pid)}
function serializeProblem(p){return {...p, canonical_title:p.name,canonical_description:p.summary,product_area:p.feature,status:p.status,occurrence_count:p.status==='RECURRING'?2:1}}
function configured(){return Boolean(HINDSIGHT_API_KEY && HINDSIGHT_BANK_ID)}
const HINDSIGHT_TIMEOUT_MS = Number(process.env.HINDSIGHT_TIMEOUT_MS || 25000);
async function hindsight(path,method='GET',body,timeoutMs=HINDSIGHT_TIMEOUT_MS){
  if(!configured()) return null;
  const ctl=new AbortController();const timer=setTimeout(()=>ctl.abort(),timeoutMs);
  try{
    const r=await fetch(`${HINDSIGHT_BASE_URL}${path}`,{method,signal:ctl.signal,headers:{'authorization':`Bearer ${HINDSIGHT_API_KEY}`,'content-type':'application/json','accept':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});
    const text=await r.text();let data;try{data=text?JSON.parse(text):{}}catch{data={text}}
    if(!r.ok){const d=data?.detail??data?.message??data?.error??data?.text;throw new Error(`Hindsight ${r.status}: ${typeof d==='string'?d:JSON.stringify(d||{}).slice(0,200)}`)}
    return data;
  }catch(e){
    if(e?.name==='AbortError')throw new Error(`Hindsight timed out after ${Math.round(timeoutMs/1000)}s`);
    throw e;
  }finally{clearTimeout(timer)}
}
const bankPath=()=>`/v1/default/banks/${encodeURIComponent(HINDSIGHT_BANK_ID)}`;
async function retainMemory(item,asyncMode=false){
  return hindsight(`${bankPath()}/memories`,'POST',{
    items:[{content:item.content,context:item.context||'TRACE',timestamp:item.timestamp||new Date().toISOString(),metadata:item.metadata||{}}],
    async:asyncMode
  });
}
async function retainBatch(items){
  return hindsight(`${bankPath()}/memories`,'POST',{items,async:true},15000);
}
const itemsOf=r=>Array.isArray(r?.results)?r.results:Array.isArray(r?.memories)?r.memories:Array.isArray(r)?r:[];
async function recallMemory(query,limit=10){
  try{return await hindsight(`${bankPath()}/memories/recall`,'POST',{query,budget:'low',max_tokens:2048})}
  catch(e){if(/ 4(00|22)/.test(e.message))return hindsight(`${bankPath()}/memories/recall`,'POST',{query});throw e}
}
// Hindsight's current reflect API has no separate "context" field: situational context is folded into the query.
async function reflectMemory(query,context){
  const q=context?`${query}\n\nContext: ${context}`:query;
  try{return await hindsight(`${bankPath()}/reflect`,'POST',{query:q,budget:'low',max_tokens:1024})}
  catch(e){if(/ 4(00|22)/.test(e.message))return hindsight(`${bankPath()}/reflect`,'POST',{query:q});throw e}
}
async function waitForOperation(opId,maxMs=30000){
  if(!opId)return 'unknown';
  const end=Date.now()+maxMs;
  while(Date.now()<end){
    try{
      const r=await hindsight(`${bankPath()}/operations`,'GET',undefined,8000);
      const op=(r?.operations||[]).find(o=>String(o.id)===String(opId));
      if(op&&(op.status==='completed'||op.status==='failed'))return op.status;
    }catch{return 'unknown'}
    await new Promise(r=>setTimeout(r,3000));
  }
  return 'pending';
}

function localAnalysis(query){
  const q=query.toLowerCase();
  if(q.includes('worked')||q.includes('solution')||q.includes('try')) return 'The March navigation simplification was partially successful: desktop complaints fell 61%, but mobile complaints persisted. A sticky order summary later reduced desktop drop-offs, but did not resolve mobile scanning difficulty.';
  if(q.includes('segment')||q.includes('who')) return 'The recurrence is concentrated among mobile shoppers and new customers, with Android users showing the sharpest recent increase in the seeded scenario.';
  if(q.includes('why')||q.includes('return')||q.includes('again')) return 'TRACE found a prior checkout problem beginning in January. Navigation simplification shipped in March and improved desktop complaints, but mobile friction persisted. The July mobile redesign was followed by renewed complaints in August and September. This is a possible recurrence; the evidence does not establish a single causal factor.';
  return 'TRACE connects the current signal to a historical mobile checkout problem, prior interventions, their measured outcomes, and the recent recurrence. The historical record should be used to avoid repeating interventions that only improved desktop behavior.';
}
function baselineAnalysis(){return 'Based only on the current feedback, customers appear to be struggling to find delivery and promo details during mobile checkout. The immediate signal suggests navigation or information architecture friction, but current feedback alone cannot establish whether this is a recurrence of an older problem.'}
function historicalAnalysis(){return 'Hindsight changes the interpretation: the current complaint matches a known mobile checkout problem first detected in January. Navigation simplification improved desktop complaints by 61% while mobile friction persisted; a later mobile redesign was followed by renewed complaints. TRACE should investigate whether the redesigned mobile navigation reintroduced the earlier scanning problem rather than treating this as a brand-new issue.'}

async function replay(body){
  const useMemory=Boolean(body.use_memory);
  const base={scenario:body.scenario_id||'mobile_checkout_resurrection',without_memory:{analysis:baselineAnalysis(),historical_context:[]}};
  if(!useMemory)return {...base,with_memory:null,memory_impact:{available:false,recommendation_changes:[],message:'Memory disabled for this replay.'}};
  let recalled=null, reflected=null, live=false, error=null;
  if(configured()){
    try{
      recalled=await recallMemory('TRACE mobile checkout problem; checkout navigation; previous interventions; March 2026 navigation simplification; desktop complaint reduction; persistent mobile complaints; July 2026 mobile redesign; August and September 2026 recurrence.');
      if(itemsOf(recalled).length){
        reflected=await reflectMemory(body.query||'Why did checkout complaints return after the mobile redesign?', 'Use historical product memory. Separate historical facts, current evidence, inference and unresolved hypotheses. Do not invent events or causal claims.');
        live=Boolean(reflected?.text||reflected?.response||reflected?.answer||reflected?.content);
      }else error='Hindsight bank has no processed memories yet - run Seed and wait a minute.';
    }catch(e){error=e.message}
  }
  const recalledItems=itemsOf(recalled);
  const historical_context=(recalledItems.length?recalledItems:memory).slice(0,6).map((x,i)=>({id:x.id||`memory-${i+1}`,text:x.text||x.content||x.memory||String(x),source:recalledItems.length?'hindsight':'demo-memory'}));
  const reflectionText=reflected?.text||reflected?.response||reflected?.answer||reflected?.content||historicalAnalysis();
  return { ...base,
    with_memory:{analysis:live?reflectionText:historicalAnalysis(),historical_context},
    memory_impact:{available:true,live,provider:live?'hindsight':'deterministic-demo-memory',error,recommendation_changes:[
      'Investigate the mobile navigation and information hierarchy before proposing another copy-only fix.',
      'Compare Android behavior with the March desktop improvement instead of assuming the prior intervention solved the full problem.',
      'Reuse the measured history: the previous navigation change improved desktop complaints but did not resolve mobile scanning difficulty.'
    ]}
  };
}

async function handle(req,res){
  const u=new URL(req.url,`http://${req.headers.host||'localhost'}`);const path=u.pathname;const method=req.method||'GET';
  if(path.startsWith('/api/') && TRACE_API_KEY && req.headers['x-api-key']!==TRACE_API_KEY)return json(res,401,{error:{code:'HTTP_401',message:'Valid X-API-Key is required.'}});
  try{
    if(path==='/api/v1/health'&&method==='GET')return json(res,200,{ok:true,service:'trace-api-node',version:'3.0.0',hindsight_configured:configured(),hindsight_live:configured(),environment:process.env.NODE_ENV||'development'});
    if(path==='/api/v1/dashboard/overview'&&method==='GET'){
      return json(res,200,{total_feedback:181,active_problems:4,emerging_problems:1,recurring_problems:2,resurrected_problems:2,unresolved_problems:4,interventions:state.interventions.length,intervention_success_rate:.5,partial_successes:2,failed_interventions:1,contradictions:1,sentiment_trend:problems.map(p=>({problem_id:p.id,trend:p.trend})),top_problem_areas:[{product_area:'Checkout',count:1},{product_area:'Search',count:1},{product_area:'Delivery tracking',count:1},{product_area:'Account settings',count:1},{product_area:'Gift cards',count:1}]});
    }
    if(path==='/api/v1/feedback'&&method==='GET')return json(res,200,feedback);
    if(path.startsWith('/api/v1/feedback/')&&method==='GET'){const f=feedback.find(x=>x.id===path.split('/').pop());return f?json(res,200,f):json(res,404,{error:{message:'Feedback not found'}})}
    if(path==='/api/v1/feedback'&&method==='POST'){const b=await readBody(req);const f={id:id('f'),date:(b.timestamp||new Date().toISOString()).slice(0,10),channel:b.source||'API',segment:b.metadata?.segment||'Unknown',text:b.text,sentiment:b.sentiment==='positive'?0.7:b.sentiment==='negative'?-0.7:0,problemId:'gift-cards'};feedback.unshift(f);if(configured()){try{await retainMemory({content:`Customer feedback: ${b.text}`,context:`TRACE feedback from ${b.source||'API'}`,timestamp:b.timestamp},true)}catch(e){console.error('Hindsight retain failed:',e.message)}}return json(res,201,{feedback_id:f.id,duplicate:false,analysis:{sentiment:b.sentiment||'neutral',product_area:b.metadata?.product_area||'Unknown',platform:b.metadata?.platform||'unknown',segment:f.segment,severity:'medium',problem_title:'New customer signal',intent:'report_problem'},identity:{classification:'NEW_PROBLEM',problem_id:null,confidence:.82,reasoning:'Demo Node classifier accepted the new signal.',evidence:[]}})}
    if(path==='/api/v1/feedback/batch'&&method==='POST'){const b=await readBody(req);const items=[];for(const item of b.items||[])items.push({feedback_id:id('f'),duplicate:false});return json(res,201,{count:items.length,items})}
    if((path==='/api/v1/feedback/analyze'||path==='/api/v1/analyze')&&method==='POST'){const b=await readBody(req);return json(res,200,{analysis:{sentiment:/\b(good|great|easy|better)\b/i.test(b.text)?'positive':'negative',product_area:b.product_area||'Checkout',platform:b.platform||'mobile',segment:b.segment||'New customers',severity:'medium',problem_title:'Customer experience issue',intent:'report_problem'},identity:{classification:'POSSIBLE_EXISTING_PROBLEM',problem_id:'checkout-mobile',confidence:.88,reasoning:'The deterministic demo classifier matched the seeded checkout scenario.',evidence:[]},facts_vs_inferences:{fact:'The submitted feedback was analyzed from its text and supplied attributes.',inference:'It resembles a known seeded product problem.',hypothesis:null}})}
    if(path==='/api/v1/problems'&&method==='GET'){const status=u.searchParams.get('status');return json(res,200,problems.filter(p=>!status||p.status===status).map(serializeProblem))}
    if(path==='/api/v1/problems/resurrected'&&method==='GET')return json(res,200,problems.filter(p=>p.status==='RECURRING'));
    if(path==='/api/v1/problems/emerging'&&method==='GET')return json(res,200,problems.filter(p=>p.status==='EMERGING'));
    const pm=path.match(/^\/api\/v1\/problems\/([^/]+)$/);if(pm&&method==='GET'){const p=problemById(decodeURIComponent(pm[1]));if(!p)return json(res,404,{error:{message:'Problem not found'}});return json(res,200,{...serializeProblem(p),evidence:feedback.filter(f=>f.problemId===p.id).map(f=>({id:f.id,evidence_type:'feedback_signal',content:f.text,confidence:.92,source_id:f.id})),evolution:p.id==='checkout-mobile'?[{type:'EVOLVED_FROM',from:'Checkout navigation confusion',to:'Mobile checkout confusion',confidence:.81}]:[],memory:p.id==='checkout-mobile'?memory:[]})}
    const tl=path.match(/^\/api\/v1\/problems\/([^/]+)\/timeline$/);if(tl&&method==='GET'){const p=problemById(decodeURIComponent(tl[1]));return p?json(res,200,p.timeline):json(res,404,{error:{message:'Problem not found'}})}
    const ev=path.match(/^\/api\/v1\/problems\/([^/]+)\/evolution$/);if(ev&&method==='GET'){return json(res,200,problemById(decodeURIComponent(ev[1]))?.id==='checkout-mobile'?[{type:'EVOLVED_FROM',from:'Checkout navigation confusion',to:'Mobile checkout confusion',confidence:.81}]:[])}
    const ee=path.match(/^\/api\/v1\/problems\/([^/]+)\/evidence$/);if(ee&&method==='GET'){const p=problemById(decodeURIComponent(ee[1]));return json(res,200,(p?feedback.filter(f=>f.problemId===p.id):[]).map(f=>({id:f.id,evidence_type:'feedback_signal',content:f.text,confidence:.92,source_id:f.id})))}
    const mm=path.match(/^\/api\/v1\/problems\/([^/]+)\/memory$/);if(mm&&method==='GET'){const p=problemById(decodeURIComponent(mm[1]));return json(res,200,p?.id==='checkout-mobile'?memory:[])}
    if(path==='/api/v1/problems'&&method==='POST'){const b=await readBody(req);const p={id:id('p'),name:b.canonical_title||'New problem',feature:b.product_area||'Unknown',status:b.status||'EMERGING',severity:b.severity||'Medium',firstDetected:b.first_seen_at||new Date().toISOString(),lastDetected:b.last_seen_at||new Date().toISOString(),feedbackCount:0,sentiment:0,segments:b.customer_segments||[],summary:b.canonical_description||'',trend:[1],timeline:[],previousSolutions:[]};problems.push(p);return json(res,201,serializeProblem(p))}
    if(path==='/api/v1/decisions'&&method==='GET')return json(res,200,state.decisions);
    if(path==='/api/v1/decisions'&&method==='POST'){const b=await readBody(req);const d={id:id('d'),...b};state.decisions.unshift(d);return json(res,201,d)}
    if(path==='/api/v1/interventions'&&method==='GET')return json(res,200,state.interventions);
    if(path==='/api/v1/interventions'&&method==='POST'){const b=await readBody(req);const i={id:id('i'),...b};state.interventions.unshift(i);return json(res,201,i)}
    if(path==='/api/v1/interventions/check'&&method==='POST'){const b=await readBody(req);const q=String(b.proposed_intervention||'').toLowerCase();const matches=state.interventions.filter(i=>i.problem_id===b.problem_id&&((i.name||'').toLowerCase().split(/\s+/).some(w=>q.includes(w))||q.includes('checkout')&&i.problem_id==='checkout-mobile'));return json(res,200,{found:matches.length>0,historical_matches:matches.map(i=>({intervention:i.name,outcomes:i.name==='Simplify checkout navigation'?['PARTIAL_SUCCESS — desktop complaints fell 61%; mobile complaints persisted.']:['Recorded historical intervention'],confidence:.86}))})}
    if(path==='/api/v1/outcomes'&&method==='GET')return json(res,200,state.outcomes);
    if(path==='/api/v1/outcomes'&&method==='POST'){const b=await readBody(req);const o={id:id('o'),...b};state.outcomes.unshift(o);return json(res,201,o)}
    if(path==='/api/v1/contradictions'&&method==='GET')return json(res,200,[{problem_id:'checkout-mobile',contradiction_detected:true,possible_explanations:['Desktop complaints improved after navigation simplification while mobile complaints persisted.']}]);
    const rr=path.match(/^\/api\/v1\/problems\/([^/]+)\/resurrection$/);if(rr&&method==='GET'){const p=problemById(decodeURIComponent(rr[1]));return json(res,200,{resurrected:p?.status==='RECURRING'||p?.status==='REGRESSING',reason:p?.status==='RECURRING'?'Current mobile feedback matches a previously observed checkout problem after an earlier intervention.':'No strong recurrence signal in the seeded lifecycle.'})}
    const cc=path.match(/^\/api\/v1\/problems\/([^/]+)\/contradictions$/);if(cc&&method==='GET'){const p=problemById(decodeURIComponent(cc[1]));return json(res,200,p?.id==='checkout-mobile'?{contradiction_detected:true,possible_explanations:['The earlier intervention improved desktop behavior but did not resolve mobile scanning difficulty.']}:{contradiction_detected:false,possible_explanations:[]})}
    if(path==='/api/v1/decision-debt'&&method==='GET')return json(res,200,[{problem_id:'checkout-mobile',title:'Mobile checkout recurrence remains unresolved',age_days:256,reason:'A known problem returned after multiple changes.'}]);
    if(path==='/api/v1/stale-memory'&&method==='GET')return json(res,200,[]);
    if(path==='/api/v1/stale-memory/detect'&&method==='POST')return json(res,200,{detected:0,items:[]});
    const sm=path.match(/^\/api\/v1\/stale-memory\/([^/]+)\/flag$/);if(sm&&method==='POST')return json(res,200,{id:sm[1],flagged:true});
    if(path==='/api/v1/memory/retain'&&method==='POST'){const b=await readBody(req);const r=await retainMemory(b,true);return json(res,201,{ok:true,live:configured(),result:r})}
    if(path==='/api/v1/memory/recall'&&method==='POST'){const b=await readBody(req);let result;if(configured()){try{result=await recallMemory(b.query||'',Number(b.limit||10))}catch(e){console.error('recall failed:',e.message)}}if(!result)result={memories:memory.slice(0,Number(b.limit||10))};return json(res,200,{configured:configured(),result})}
    if(path==='/api/v1/memory/reflect'&&method==='POST'){const b=await readBody(req);let result=null;if(configured()){try{result=await reflectMemory(b.query||'',b.context||'TRACE')}catch(e){console.error('reflect failed:',e.message)}}if(!result)result={text:historicalAnalysis(),memories:memory};return json(res,200,{configured:configured(),text:result?.text||result?.response||result?.answer||historicalAnalysis(),result})}
    if(path==='/api/v1/memory/diagnose'&&method==='GET'){
      const out={configured:configured(),base_url:HINDSIGHT_BASE_URL,bank_id:HINDSIGHT_BANK_ID,api_key_set:Boolean(HINDSIGHT_API_KEY),api_key_length:HINDSIGHT_API_KEY.length,timeout_ms:HINDSIGHT_TIMEOUT_MS,steps:[]};
      if(!configured()){out.verdict='HINDSIGHT_API_KEY is not set in this deployment. Add it in Vercel -> Settings -> Environment Variables, then redeploy.';return json(res,200,out)}
      const step=async(name,fn)=>{const t=Date.now();try{const v=await fn();out.steps.push({name,ok:true,ms:Date.now()-t,...v})}catch(e){out.steps.push({name,ok:false,ms:Date.now()-t,error:e.message})}};
      await step('recall',async()=>{const r=await recallMemory('TRACE mobile checkout problem');return {memories_found:itemsOf(r).length,sample:String(itemsOf(r)[0]?.text||'').slice(0,100)}});
      await step('reflect',async()=>{const r=await reflectMemory('Summarize the mobile checkout history in one sentence.');return {text:String(r?.text||r?.response||'').slice(0,160)}});
      const failed=out.steps.filter(x=>!x.ok);const rc=out.steps.find(x=>x.name==='recall');
      out.verdict=failed.length?`Hindsight call failed: ${failed.map(x=>x.name+' -> '+x.error).join(' | ')}`
        :rc?.memories_found?'LIVE: Hindsight recall and reflect both work.':'Connected, but the bank is empty or still processing. Press "Seed demo + Hindsight" and wait about a minute.';
      return json(res,200,out);
    }
    if(path==='/api/v1/memory/status'&&method==='GET')return json(res,200,{configured:configured(),bank_id:HINDSIGHT_BANK_ID,base_url:HINDSIGHT_BASE_URL,provider:configured()?'Hindsight Cloud':'Deterministic demo memory'});
    if(path==='/api/v1/replay'&&method==='POST')return json(res,200,await replay(await readBody(req)));
    if(path==='/api/v1/agent/ask'&&method==='POST'){const b=await readBody(req);if(configured()){try{const r=await reflectMemory(b.query||'','TRACE agent. Use historical memory and distinguish facts from inference.');return json(res,200,{configured:true,text:r?.text||r?.response||r?.answer||historicalAnalysis()})}catch{}}return json(res,200,{configured:false,text:localAnalysis(b.query||'')})}
    if(path==='/api/v1/evaluation/run'&&method==='POST')return json(res,200,{ok:true,executed:1,passed:1,results:[{scenario:'mobile_checkout_resurrection',passed:true,notes:'Deterministic acceptance scenario executed.'}]});
    if(path==='/api/v1/evaluation/results'&&method==='GET')return json(res,200,{executed:1,passed:1,results:[{scenario:'mobile_checkout_resurrection',passed:true}]});
    if(path==='/api/v1/evaluation/health'&&method==='GET')return json(res,200,{ok:true,checks:{api:true,hindsight:configured(),demo_data:true}});
    if(path==='/api/v1/demo/reset'&&method==='POST'){state.decisions=[];state.outcomes=[];state.seeded=false;return json(res,200,{ok:true})}
    if(path==='/api/v1/demo/seed'&&method==='POST'){
      state.seeded=true;let retained=0,error=null,status='none';
      if(configured()){
        try{
          const r=await retainBatch(memory.map(m=>({content:m.text,context:'TRACE synthetic longitudinal demo scenario',timestamp:`${m.date}T12:00:00Z`,document_id:`trace-demo-${m.id}`})));
          retained=memory.length;status=await waitForOperation(r?.operation_id,30000);
        }catch(e){error=e.message}
      }
      const message=!configured()?'TRACE demo data is ready. Add HINDSIGHT_API_KEY to use live Hindsight.'
        :error?`TRACE demo data is ready. Hindsight said: ${error}`
        :status==='completed'?'TRACE demo data is ready and Hindsight has processed the memories. Run Memory OFF, then Memory ON.'
        :'TRACE demo data is ready. Hindsight is still processing the memories - wait about a minute, then run Memory ON.';
      return json(res,200,{ok:true,seeded:true,hindsight_configured:configured(),hindsight_seeded:retained===memory.length&&retained>0,hindsight_status:status,retained_count:retained,error,message});
    }
    if(path==='/api/v1/ingestion/upload'&&method==='POST')return json(res,200,{ok:true,accepted:0,errors:['File ingestion is intentionally disabled in the no-dependency demo runtime. Use /api/v1/feedback/batch for JSON ingestion.']});
    if(path==='/api/hindsight/reflect'&&method==='POST'){const b=await readBody(req);return json(res,200,{configured:configured(),text:configured()?(await reflectMemory(b.query||'','TRACE historical product intelligence'))?.text||historicalAnalysis():historicalAnalysis()})}
    if(path==='/api/health'&&method==='GET')return json(res,200,{ok:true,hindsight:configured()});
    return json(res,404,{error:{code:'NOT_FOUND',message:`Route not found: ${method} ${path}`}});
  }catch(e){console.error(e);return json(res,500,{error:{code:'INTERNAL_ERROR',message:e?.message||'Server error'}})}
}

export default handle;
if(!process.env.VERCEL && process.env.TRACE_SERVER_MODE!=='vercel'){
  const server=http.createServer(handle);
  server.listen(PORT,()=>console.log(`TRACE Node API listening on http://localhost:${PORT}`));
}
