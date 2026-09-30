export type ProblemStatus = 'RECURRING'|'EMERGING'|'IMPROVING'|'REGRESSING'|'UNRESOLVED'|'RESOLVED'|'EVOLVING';
export type EventType = 'feedback'|'decision'|'change'|'outcome'|'recurrence';
export interface Feedback { id:string; date:string; channel:string; segment:string; text:string; sentiment:number; problemId:string; }
export interface TimelineEvent { id:string; date:string; type:EventType; title:string; detail:string; impact:string; }
export interface Problem { id:string; name:string; feature:string; status:ProblemStatus; severity:'Critical'|'High'|'Medium'|'Low'; firstDetected:string; lastDetected:string; feedbackCount:number; sentiment:number; segments:string[]; summary:string; trend:number[]; timeline:TimelineEvent[]; previousSolutions:{name:string; outcome:'Successful'|'Partial'|'Failed'; detail:string; date:string}[]; }

export const problems:Problem[] = [
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

export const feedback:Feedback[] = [
 {id:'f1',date:'2026-09-18',channel:'App review',segment:'Mobile shoppers',text:'I keep opening different screens to find delivery and promo details before paying.',sentiment:-0.7,problemId:'checkout-mobile'},
 {id:'f2',date:'2026-09-16',channel:'Support',segment:'New customers',text:'Checkout feels like it keeps hiding the information I need.',sentiment:-0.6,problemId:'checkout-mobile'},
 {id:'f3',date:'2026-09-15',channel:'Survey',segment:'Returning customers',text:'Search is much better than before. Exact product names now usually appear first.',sentiment:0.5,problemId:'search-relevance'},
 {id:'f4',date:'2026-09-21',channel:'Support',segment:'Tier-2 cities',text:'The date said Thursday, then changed after I paid. I had planned around it.',sentiment:-0.8,problemId:'delivery-window'},
 {id:'f5',date:'2026-09-20',channel:'App review',segment:'Gift buyers',text:'Gift card works until I add a promo code, then redemption fails.',sentiment:-0.4,problemId:'gift-cards'},
 {id:'f6',date:'2026-07-03',channel:'Survey',segment:'Subscribers',text:'Cancellation is finally easy to find and the final bill is clear.',sentiment:0.7,problemId:'subscription-cancel'}
];

export const dashboardTrend = [
 {month:'Jan',feedback:78,sentiment:-0.42},{month:'Feb',feedback:92,sentiment:-0.31},{month:'Mar',feedback:105,sentiment:-0.25},{month:'Apr',feedback:98,sentiment:-0.12},{month:'May',feedback:121,sentiment:-0.08},{month:'Jun',feedback:133,sentiment:-0.02},{month:'Jul',feedback:149,sentiment:-0.07},{month:'Aug',feedback:164,sentiment:-0.12},{month:'Sep',feedback:181,sentiment:-0.16}
];

export function formatDate(date:string){ return new Intl.DateTimeFormat('en',{month:'short',day:'numeric',year:'numeric'}).format(new Date(date+'T00:00:00')); }
export function statusTone(status:ProblemStatus){ return {RECURRING:'danger',EMERGING:'info',IMPROVING:'good',REGRESSING:'danger',UNRESOLVED:'warn',RESOLVED:'good',EVOLVING:'info'}[status]; }
