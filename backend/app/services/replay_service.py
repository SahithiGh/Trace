from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Problem, Intervention, Outcome, Evidence
from ..memory import MemoryService, HindsightUnavailable

class ReplayService:
    def __init__(self, memory): self.memory=memory
    async def run(self,db,scenario_id,query):
        p=(await db.execute(select(Problem).where(Problem.id=='checkout-mobile'))).scalar_one_or_none()
        baseline={'analysis':'The current feedback indicates a mobile checkout problem. Investigate the current failure mode and collect more evidence before changing the flow.','recommendations':['Inspect the current mobile checkout funnel','Segment by platform and customer type','Validate the failure mode with current evidence']}
        if not self.memory.configured: return {'scenario':scenario_id,'without_memory':baseline,'with_memory':None,'memory_impact':{'available':False,'message':'Hindsight is not configured; Memory ON is intentionally unavailable rather than simulated.'}}
        recalled=await self.memory.recall(query)
        reflected=await self.memory.reflect(query,context='TRACE product intelligence replay. Distinguish historical facts from hypotheses and cite supporting memory.')
        result={'analysis':reflected.get('text',''),'recommendations':['Review the previously attempted intervention and its measured outcome','Investigate the unresolved mobile-specific failure mode before repeating the same intervention'],'historical_context':recalled.get('results',[])}
        return {'scenario':scenario_id,'without_memory':baseline,'with_memory':result,'memory_impact':{'available':True,'historical_facts_added':[x.get('text') or x.get('content') for x in recalled.get('results',[])][:8],'recommendation_changes':['Adds prior intervention and outcome context','Warns against repeating an intervention without addressing the unresolved mobile-specific failure mode']}}
