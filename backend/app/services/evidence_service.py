from sqlalchemy import select
from ..models import Evidence, Intervention, Outcome, Decision
class EvidenceService:
    async def for_problem(self,db,problem_id):
        intervention_ids={x.id for x in (await db.execute(select(Intervention).where(Intervention.problem_id==problem_id))).scalars().all()}
        outcome_ids={x.id for x in (await db.execute(select(Outcome).where(Outcome.intervention_id.in_(intervention_ids)))).scalars().all()} if intervention_ids else set()
        decision_ids={x.id for x in (await db.execute(select(Decision).where(Decision.problem_id==problem_id))).scalars().all()}
        rows=(await db.execute(select(Evidence).order_by(Evidence.timestamp.desc()))).scalars().all()
        allowed=intervention_ids|outcome_ids|decision_ids|{problem_id}
        return [self.serialize(x) for x in rows if x.source_id in allowed or x.source_type=='problem']
    def serialize(self,e): return {'id':e.id,'source_type':e.source_type,'source_id':e.source_id,'evidence_type':e.evidence_type,'content':e.content,'timestamp':e.timestamp,'relevance':e.relevance,'confidence':e.confidence}
