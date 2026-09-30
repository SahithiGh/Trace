from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Intervention
class InterventionService:
    async def create(self,db,body):
        i=Intervention(**body.model_dump()); db.add(i); await db.commit(); await db.refresh(i); return i
    async def list(self,db,problem_id=None):
        q=select(Intervention).order_by(Intervention.timestamp.desc())
        if problem_id:q=q.where(Intervention.problem_id==problem_id)
        return (await db.execute(q)).scalars().all()
