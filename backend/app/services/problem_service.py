from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Problem, Decision, Intervention, Outcome, Evidence
from .engines import EvolutionEngine, SentimentEngine
class ProblemService:
    async def detail(self,db,problem_id):
        p=await db.get(Problem,problem_id)
        if not p:return None
        decisions=(await db.execute(select(Decision).where(Decision.problem_id==problem_id).order_by(Decision.timestamp))).scalars().all()
        ints=(await db.execute(select(Intervention).where(Intervention.problem_id==problem_id).order_by(Intervention.timestamp))).scalars().all(); outcomes=[]
        for i in ints: outcomes += list((await db.execute(select(Outcome).where(Outcome.intervention_id==i.id).order_by(Outcome.timestamp))).scalars().all())
        return {'problem':{'id':p.id,'canonical_title':p.canonical_title,'canonical_description':p.canonical_description,'product_area':p.product_area,'severity':p.severity,'status':p.status,'occurrence_count':p.occurrence_count,'first_seen_at':p.first_seen_at,'last_seen_at':p.last_seen_at,'customer_segments':p.customer_segments,'current_state':p.current_state},'decisions':[d.__dict__ for d in decisions],'historical_interventions':[i.__dict__ for i in ints],'outcomes':[o.__dict__ for o in outcomes],'sentiment_trend':await SentimentEngine().trend(db,problem_id),'evolution':await EvolutionEngine().graph(db,problem_id)}
