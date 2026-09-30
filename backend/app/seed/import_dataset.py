import argparse, asyncio, csv, json
from datetime import datetime
from pathlib import Path
from ..database import SessionLocal
from ..services.feedback_service import FeedbackService
from ..schemas.api import FeedbackIn

async def run(path):
    rows=json.loads(Path(path).read_text()) if path.endswith('.json') else list(csv.DictReader(Path(path).open(encoding='utf-8-sig')))
    async with SessionLocal() as db:
        svc=FeedbackService(); ingested=0; duplicates=0
        for row in rows:
            item=FeedbackIn(source=row.get('source','manually_entered'),text=row['text'],timestamp=datetime.fromisoformat(row['timestamp'].replace('Z','+00:00')).replace(tzinfo=None),source_external_id=row.get('source_external_id'),customer_id=row.get('customer_id'),product_id=row.get('product_id'),product_version=row.get('product_version'),rating=float(row['rating']) if row.get('rating') else None,sentiment=row.get('sentiment'),metadata={})
            _,created=await svc.ingest(db,item); ingested+=created; duplicates+=not created
        await db.commit(); print({'rows':len(rows),'ingested':ingested,'duplicates':duplicates})
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('path'); args=ap.parse_args(); asyncio.run(run(args.path))
