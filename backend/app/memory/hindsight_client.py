import httpx
from ..config import settings

class HindsightUnavailable(RuntimeError):
    pass

class HindsightClient:
    """Small vendor boundary for the documented Hindsight HTTP API."""
    def __init__(self):
        self.base=settings.hindsight_base_url.rstrip('/')
        self.key=settings.hindsight_api_key
        self.bank=settings.hindsight_bank_id
    @property
    def configured(self): return bool(self.key and self.bank)
    async def _request(self,method,path,payload=None):
        if not self.configured: raise HindsightUnavailable('Hindsight is not configured. Set HINDSIGHT_API_KEY and HINDSIGHT_BANK_ID.')
        headers={'Authorization':f'Bearer {self.key}','Accept':'application/json','Content-Type':'application/json'}
        async with httpx.AsyncClient(timeout=30) as client:
            r=await client.request(method,f'{self.base}/v1/default/banks/{self.bank}{path}',headers=headers,json=payload)
            r.raise_for_status(); return r.json()
    async def retain(self,content,context='TRACE product event',timestamp=None):
        item={'content':content,'context':context}
        if timestamp is not None: item['timestamp']=timestamp.isoformat() if hasattr(timestamp,'isoformat') else timestamp
        return await self._request('POST','/memories',{'items':[item],'async':False})
    async def recall(self,query,context='',limit=10,query_timestamp=None):
        payload={'query':query,'trace':True,'budget':'mid','types':['world','experience','observation']}
        if context: payload['context']=context
        if query_timestamp: payload['query_timestamp']=query_timestamp.isoformat() if hasattr(query_timestamp,'isoformat') else query_timestamp
        result=await self._request('POST','/memories/recall',payload)
        if isinstance(result,dict) and isinstance(result.get('results'),list): result['results']=result['results'][:limit]
        return result
    async def reflect(self,query,context=''):
        payload={'query':query,'budget':'mid'}
        if context: payload['context']=context
        return await self._request('POST','/reflect',payload)
