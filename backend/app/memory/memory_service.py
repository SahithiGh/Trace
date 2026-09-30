from .hindsight_client import HindsightClient
from .memory_types import MemoryType

class MemoryService:
    """Only application boundary through which TRACE talks to Hindsight."""
    def __init__(self,client=None): self.client=client or HindsightClient()
    @property
    def configured(self): return self.client.configured
    async def retain(self,content,context='TRACE product event',timestamp=None,memory_type=MemoryType.FACT,provenance=None):
        kind=getattr(memory_type,'value',memory_type)
        enriched=f'[{kind}] {content}'
        if provenance: enriched += f' | provenance={provenance}'
        return await self.client.retain(enriched,context=context,timestamp=timestamp)
    async def recall(self,query,context='',limit=10,query_timestamp=None): return await self.client.recall(query,context=context,limit=limit,query_timestamp=query_timestamp)
    async def reflect(self,query,context=''): return await self.client.reflect(query,context=context)
