from datetime import datetime
from sqlalchemy import select
from ..models import Problem, Intervention, Outcome, Decision, Evidence, Feedback, Relationship, MemoryRecord

async def seed(db, reset=False):
    if reset:
        for model in [Evidence,Outcome,Intervention,Decision,Relationship,Feedback,MemoryRecord,Problem]:
            for obj in (await db.execute(select(model))).scalars().all(): await db.delete(obj)
        await db.commit()
    if (await db.execute(select(Problem))).scalars().first(): return
    p=Problem(id='checkout-mobile',canonical_title='Mobile checkout reliability',canonical_description='Customers cannot reliably complete checkout on mobile, especially Android.',problem_type='reliability',product_area='checkout',severity='high',status='RECURRING',first_seen_at=datetime(2026,1,14),last_seen_at=datetime(2026,9,18),occurrence_count=4,current_sentiment=-.62,historical_sentiment_summary={'jan':-.72,'apr':-.48,'sep':-.67},customer_segments=['mobile shoppers','returning customers','Android users'],current_state={'platform':'mobile','user_goal':'complete purchase','failure_mode':'performance/reliability','data_source':'synthetic_demo'})
    p2=Problem(id='checkout-payment',canonical_title='Checkout payment authentication failures',canonical_description='Payment authentication fails after the user reaches the verification step.',problem_type='reliability',product_area='checkout',severity='high',status='EVOLVING',first_seen_at=datetime(2026,5,10),last_seen_at=datetime(2026,9,10),occurrence_count=2,current_sentiment=-.58,historical_sentiment_summary={},customer_segments=['Android users'],current_state={'platform':'mobile','user_goal':'complete purchase','failure_mode':'payment failure','data_source':'synthetic_demo'})
    db.add_all([p,p2]); await db.flush()
    d=Decision(problem_id=p.id,decision='Redesign checkout flow',rationale='Abandonment and support volume increased.',decision_maker='Product Team',timestamp=datetime(2026,2,3))
    i=Intervention(problem_id=p.id,name='Checkout navigation simplification',why='Reduce checkout friction',target_segment='all shoppers',target_platform='web + mobile',expected_outcome='Reduce abandonment by 15%',timestamp=datetime(2026,3,18),decision_maker='Product Team',status='TESTED')
    i2=Intervention(problem_id=p.id,name='Sticky order summary',why='Reduce review-step confusion',target_segment='web shoppers',target_platform='web',expected_outcome='Reduce desktop drop-off by 10%',timestamp=datetime(2026,6,2),decision_maker='Product Team',status='TESTED')
    i3=Intervention(problem_id=p.id,name='Mobile checkout navigation redesign',why='Address unresolved mobile-specific friction after the partial desktop improvement',target_segment='mobile shoppers',target_platform='Android + iOS',expected_outcome='Reduce mobile checkout abandonment by 15%',timestamp=datetime(2026,7,12),decision_maker='Product Team',status='TESTED')
    db.add_all([d,i,i2,i3]); await db.flush()
    o=Outcome(intervention_id=i.id,outcome_type='PARTIAL_SUCCESS',qualitative_evidence='Desktop complaints fell 61%; mobile complaints persisted.',metric={'metric':'desktop_complaints','before':100,'after':39,'delta':-.61},measurement_window_days=30,timestamp=datetime(2026,4,16))
    o2=Outcome(intervention_id=i2.id,outcome_type='NO_MEASURABLE_CHANGE',qualitative_evidence='Desktop drop-off changed by less than the measurement threshold; Android remained unresolved.',metric={'metric':'desktop_dropoff','before':.22,'after':.21,'delta':-.01},measurement_window_days=30,timestamp=datetime(2026,7,2))
    o3=Outcome(intervention_id=i3.id,outcome_type='NO_MEASURABLE_CHANGE',qualitative_evidence='Mobile conversion improved only 2%, below the intended target; Android complaints remained unresolved.',metric={'metric':'mobile_conversion','before':.61,'after':.63,'delta':.02},measurement_window_days=30,timestamp=datetime(2026,8,14))
    db.add_all([o,o2,o3]); await db.flush()
    evidence=[Evidence(source_type='outcome',source_id=o.id,evidence_type='metric',content='Desktop complaints decreased 61%; mobile complaints persisted.',timestamp=o.timestamp,relevance=.95,confidence=.94),Evidence(source_type='outcome',source_id=o2.id,evidence_type='metric',content='Mobile conversion increased only 2%, below the target.',timestamp=o2.timestamp,relevance=.91,confidence=.9),Evidence(source_type='feedback',source_id='demo-sep-01',evidence_type='review',content='Checkout still fails on Android after the redesign.',timestamp=datetime(2026,9,18),relevance=.98,confidence=.97)]
    rel=Relationship(from_problem_id=p2.id,to_problem_id=p.id,relation_type='EVOLVED_FROM',confidence=.76,evidence=[{'source_id':evidence[2].id if evidence[2].id else 'pending'}])
    db.add_all(evidence); await db.flush(); rel.evidence=[{'source_type':'feedback','source_id':'demo-sep-01','reason':'same product area and user goal; distinct payment failure mode'}]; db.add(rel)
    fb=[Feedback(id='demo-jan-01',source='review',source_external_id='review-jan-01',customer_id='cust-1',product_id='storefront',product_version='4.1',timestamp=datetime(2026,1,14),text='Checkout keeps freezing on mobile.',rating=2,sentiment='negative',metadata_json={'platform':'mobile','segment':'mobile shoppers','data_source':'synthetic_demo','problem_id':'checkout-mobile'}),Feedback(id='demo-apr-01',source='support_ticket',source_external_id='support-apr-01',customer_id='cust-2',product_id='storefront',product_version='4.3',timestamp=datetime(2026,4,20),text='Desktop checkout is much better, but Android is still slow.',rating=3,sentiment='negative',metadata_json={'platform':'mobile','segment':'Android users','data_source':'synthetic_demo','problem_id':'checkout-mobile'}),Feedback(id='demo-sep-01',source='app_store',source_external_id='app-sep-01',customer_id='cust-3',product_id='storefront',product_version='5.0',timestamp=datetime(2026,9,18),text='Checkout still fails on Android after the redesign.',rating=1,sentiment='negative',metadata_json={'platform':'mobile','segment':'Android users','data_source':'synthetic_demo','problem_id':'checkout-mobile'})]
    db.add_all(fb)
    memories=[('FACT','Mobile checkout complaints were first detected in January 2026.',.98),('DECISION','The team chose checkout navigation simplification because abandonment and support volume increased.',.94),('INTERVENTION','Checkout navigation simplification shipped in March 2026.',.98),('OUTCOME','The intervention partially succeeded: desktop complaints fell 61%, while mobile complaints persisted.',.96),('CONTRADICTION','Historical improvement did not eliminate current Android complaints; the issue may have returned or evolved.',.88),('HYPOTHESIS','The latest mobile navigation may have reintroduced earlier usability friction.',.64)]
    for typ,content,conf in memories: db.add(MemoryRecord(memory_type=typ,content=content,confidence=conf,provenance={'data_source':'synthetic_demo','problem_id':p.id}))
    await db.commit()

if __name__ == '__main__':
    import asyncio
    from ..database import SessionLocal, engine
    from ..database import Base
    async def _run():
        if __import__('os').getenv('ENVIRONMENT') == 'development' and __import__('os').getenv('DATABASE_URL','').startswith('sqlite'):
            async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)
        async with SessionLocal() as db: await seed(db)
    asyncio.run(_run())
