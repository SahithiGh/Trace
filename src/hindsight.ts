import { postJson, readJson } from './api';

export interface HindsightResponse { configured:boolean; text?:string; result?:unknown; }
export async function reflectMemory(query:string):Promise<HindsightResponse>{
  const r=await postJson('/api/v1/memory/reflect',{query,context:'TRACE historical product intelligence'});
  const data=await readJson(r);
  if(!r.ok) throw new Error(data?.error?.message||'Memory service unavailable');
  return data;
}
