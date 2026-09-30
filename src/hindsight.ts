import { postJson } from './api';

export interface MemoryResult { id?: string; text: string; type?: string; mentioned_at?: string; context?: string }
export interface HindsightResponse { configured: boolean; results?: MemoryResult[]; text?: string; based_on?: { memories?: MemoryResult[] }; message?: string }

export async function reflectMemory(query: string): Promise<HindsightResponse> {
  const r = await postJson('/api/hindsight/reflect', { query });
  if (!r.ok) throw new Error('Memory reflect failed');
  return r.json();
}
