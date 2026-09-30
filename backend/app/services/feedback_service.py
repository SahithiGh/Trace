from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Feedback

class FeedbackService:
    async def ingest(self,db,item):
        if item.source_external_id:
            existing=(await db.execute(select(Feedback).where(Feedback.source==item.source,Feedback.source_external_id==item.source_external_id))).scalar_one_or_none()
            if existing: return existing,False
        f=Feedback(**item.model_dump(exclude={'metadata'}),metadata_json=item.metadata); db.add(f); await db.flush(); return f,True
