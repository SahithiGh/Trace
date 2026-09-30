import httpx, json
from ..config import settings

class LLMClient:
    @property
    def configured(self): return bool(settings.llm_api_key and settings.llm_base_url and settings.llm_model)
    async def structured(self,system:str,user:str,schema:dict):
        if not self.configured: return None
        payload={'model':settings.llm_model,'messages':[{'role':'system','content':system},{'role':'user','content':user}],'response_format':{'type':'json_schema','json_schema':{'name':'trace_result','strict':True,'schema':schema}}}
        headers={'Authorization':f'Bearer {settings.llm_api_key}','Content-Type':'application/json'}
        async with httpx.AsyncClient(timeout=45) as client:
            r=await client.post(settings.llm_base_url.rstrip('/')+'/chat/completions',headers=headers,json=payload); r.raise_for_status(); data=r.json()
        content=data['choices'][0]['message']['content']; return json.loads(content)
