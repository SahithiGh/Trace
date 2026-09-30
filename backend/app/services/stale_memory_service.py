from sqlalchemy import select
from ..models import MemoryRecord
class StaleMemoryService:
    async def list(self,db):
        rows=(await db.execute(select(MemoryRecord).where(MemoryRecord.is_stale.is_(True)).order_by(MemoryRecord.updated_at.desc()))).scalars().all()
        return [self.serialize(r) for r in rows]
    async def flag(self,db,memory_id):
        m=await db.get(MemoryRecord,memory_id)
        if not m:return None
        m.is_stale=True; await db.commit(); await db.refresh(m); return self.serialize(m)
    def serialize(self,m): return {'id':m.id,'type':m.memory_type,'content':m.content,'confidence':m.confidence,'stale':m.is_stale,'provenance':m.provenance}
