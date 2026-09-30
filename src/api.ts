/** Single JSON POST helper shared by every backend call. */
export const postJson = (url: string, body?: unknown) =>
  fetch(url, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

/** Reads a fetch Response as JSON without throwing on empty/non-JSON bodies; reports the HTTP status instead. */
export async function readJson(r: Response): Promise<any> {
  const text = await r.text();
  if (!text) throw new Error(`Empty response from server (HTTP ${r.status}). The API function may not be deployed or it crashed - check Vercel function logs.`);
  try { return JSON.parse(text); }
  catch { throw new Error(`Server returned non-JSON (HTTP ${r.status}): ${text.slice(0, 120)}`); }
}
