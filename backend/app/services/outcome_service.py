from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Outcome
class OutcomeService:
    async def create(self,db,body):
        o=Outcome(**body.model_dump()); db.add(o); await db.commit(); await db.refresh(o); return o
