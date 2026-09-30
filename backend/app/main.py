from contextlib import asynccontextmanager
from datetime import datetime
import csv, io, json, logging, time, uuid
from fastapi import FastAPI, Depends, HTTPException, Request, UploadFile, File, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from .database import engine, Base, get_db
from .models import Problem, Feedback, Intervention, Outcome, Decision, Evidence, Relationship, MemoryRecord, AnalysisAudit
from .schemas.api import *
from .config import settings
from .seed.demo import seed
from .services.engines import ProblemIdentityEngine, ResurrectionEngine, InterventionMemoryEngine, ContradictionEngine, EvolutionEngine, SentimentEngine, EmergingEngine, DecisionDebtEngine
from .services.feedback_service import FeedbackService
from .services.problem_service import ProblemService
from .services.intervention_service import InterventionService
from .services.outcome_service import OutcomeService
from .services.evidence_service import EvidenceService
from .services.replay_service import ReplayService
from .services.evaluation_service import EvaluationService
from .memory import MemoryService
from .ai.classifiers import FeedbackClassifier

logging.basicConfig(level=getattr(logging,settings.log_level.upper(),logging.INFO)); log=logging.getLogger('trace')
mem=MemoryService(); identity=ProblemIdentityEngine(); resurrection=ResurrectionEngine(); interventions=InterventionMemoryEngine(); contradictions=ContradictionEngine(); evolution=EvolutionEngine(); feedback_service=FeedbackService(); problem_service=ProblemService(); intervention_service=InterventionService(); outcome_service=OutcomeService(); evidence_service=EvidenceService(); evaluation_service=EvaluationService(); replay_service=ReplayService(mem)

@asynccontextmanager
async def lifespan(app):
    if settings.environment=='development' and settings.database_url.startswith('sqlite'):
        async with engine.begin() as c: await c.run_sync(Base.metadata.create_all)
    yield

logger=logging.getLogger("trace")
app=FastAPI(title='TRACE Product Intelligence API',version='2.1.0',description='Longitudinal product intelligence with persistent Hindsight memory.',lifespan=lifespan)
@app.middleware('http')
async def request_context(request:Request,call_next):
    rid=str(uuid.uuid4()); start=time.perf_counter();
    if request.headers.get('content-length') and int(request.headers['content-length'])>settings.request_max_bytes: return JSONResponse(status_code=413,content={'error':{'code':'REQUEST_TOO_LARGE','message':'Request exceeds the configured size limit.','request_id':rid}})
    request.state.request_id=rid
    try: response=await call_next(request); response.headers['X-Request-ID']=rid; return response
    except Exception as exc: log.exception('request failed',extra={'request_id':rid}); return JSONResponse(status_code=500,content={'error':{'code':'INTERNAL_ERROR','message':'An internal error occurred.','request_id':rid}})

@app.exception_handler(HTTPException)
async def http_error(request,exc): return JSONResponse(status_code=exc.status_code,content={'error':{'code':f'HTTP_{exc.status_code}','message':str(exc.detail),'request_id':getattr(request.state,'request_id','unknown')}})

async def require_api_key(x_api_key: str | None = Header(default=None)):
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail='Valid X-API-Key is required.')

@app.exception_handler(Exception)
async def unhandled_error(request:Request,exc:Exception):
    log.exception('unhandled request error',extra={'request_id':getattr(request.state,'request_id','unknown')})
    return JSONResponse(status_code=500,content={'error':{'code':'INTERNAL_ERROR','message':'An internal error occurred.','request_id':getattr(request.state,'request_id','unknown')}})

@app.get('/api/v1/health')
async def health(): return {'ok':True,'service':'trace-api','version':'2.1.0','hindsight_configured':mem.configured,'environment':settings.environment}

@app.get('/api/v1/dashboard/overview')
async def dashboard(db:AsyncSession=Depends(get_db)):
    ps=list((await db.execute(select(Problem))).scalars()); ints=list((await db.execute(select(Intervention))).scalars()); outs=list((await db.execute(select(Outcome))).scalars());
    return {'total_feedback':await db.scalar(select(func.count(Feedback.id))),'active_problems':sum(p.status not in {'RESOLVED'} for p in ps),'emerging_problems':sum(p.status=='EMERGING' for p in ps),'recurring_problems':sum(p.status in {'RECURRING','REGRESSING'} for p in ps),'resurrected_problems':sum(p.occurrence_count>1 for p in ps),'unresolved_problems':sum(p.status not in {'RESOLVED'} for p in ps),'interventions':len(ints),'intervention_success_rate':round(sum(o.outcome_type=='SUCCESS' for o in outs)/max(1,len(outs)),2),'partial_successes':sum(o.outcome_type=='PARTIAL_SUCCESS' for o in outs),'failed_interventions':sum(o.outcome_type in {'FAILURE','NO_MEASURABLE_CHANGE'} for o in outs),'contradictions':sum((await contradictions.check(db,p))['contradiction_detected'] for p in ps),'sentiment_trend':[{'problem_id':p.id,'trend':await SentimentEngine().trend(db,p.id)} for p in ps],'top_problem_areas':sorted([{'product_area':a,'count':sum(p.product_area==a for p in ps)} for a in {p.product_area for p in ps}],key=lambda x:x['count'],reverse=True)}

@app.get('/api/v1/feedback')
async def list_feedback(db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(Feedback).order_by(Feedback.timestamp.desc()).limit(200))).scalars().all(); return [serialize_feedback(f) for f in rows]

def serialize_feedback(f): return {'id':f.id,'source':f.source,'source_external_id':f.source_external_id,'customer_id':f.customer_id,'product_id':f.product_id,'product_version':f.product_version,'timestamp':f.timestamp,'text':f.text,'rating':f.rating,'sentiment':f.sentiment,'language':f.language,'metadata':f.metadata_json}

@app.get('/api/v1/feedback/{feedback_id}')
async def get_feedback(feedback_id:str,db:AsyncSession=Depends(get_db)):
    f=await db.get(Feedback,feedback_id)
    if not f: raise HTTPException(404,'Feedback not found')
    return serialize_feedback(f)

@app.post('/api/v1/feedback')
async def ingest(body:FeedbackIn,db:AsyncSession=Depends(get_db)):
    f,created=await feedback_service.ingest(db,body)
    if not created: await db.rollback(); return {'feedback_id':f.id,'duplicate':True,'message':'Feedback already ingested.'}
    analysis=await FeedbackClassifier().classify(body.text); ident=await identity.classify(db,body.text,body.metadata.get('product_area') or analysis.product_area,body.metadata.get('platform') or analysis.platform,body.metadata.get('segment') or analysis.segment)
    f.sentiment=f.sentiment or analysis.sentiment
    if ident.get('problem_id'):
        p=await db.get(Problem,ident['problem_id']); p.occurrence_count += 1; p.last_seen_at=body.timestamp; p.status='RECURRING' if ident['classification']=='RESURRECTED_PROBLEM' else p.status
        f.metadata_json={**f.metadata_json,'problem_id':p.id}
    else:
        p=Problem(canonical_title=analysis.problem_title,canonical_description=body.text,problem_type='customer_pain',product_area=analysis.product_area,severity=analysis.severity,status='EMERGING',first_seen_at=body.timestamp,last_seen_at=body.timestamp,occurrence_count=1,current_sentiment=-1 if analysis.sentiment=='negative' else (1 if analysis.sentiment=='positive' else 0),customer_segments=[analysis.segment],current_state={'product_area':analysis.product_area,'platform':analysis.platform,'failure_mode':'performance/reliability' if analysis.intent=='report_problem' else 'unknown','user_goal':'complete purchase' if analysis.product_area=='checkout' else 'complete task','data_source':'ingested'})
        db.add(p); await db.flush(); ident['problem_id']=p.id
    db.add(Evidence(source_type='feedback',source_id=f.id,evidence_type='feedback_signal',content=body.text,timestamp=body.timestamp,relevance=1.0,confidence=ident['confidence']))
    await db.commit()
    if mem.configured:
        await mem.retain(f'Customer feedback: {body.text}',context=f'TRACE feedback from {body.source}',timestamp=body.timestamp)
    return {'feedback_id':f.id,'duplicate':False,'analysis':analysis.model_dump(),'identity':ident}

@app.post('/api/v1/feedback/batch')
async def ingest_batch(body:FeedbackBatchIn,db:AsyncSession=Depends(get_db)):
    results=[]
    for item in body.items:
        results.append(await ingest(item,db))
    return {'count':len(results),'items':results}

@app.post('/api/v1/feedback/analyze')
async def analyze(body:AnalysisIn,db:AsyncSession=Depends(get_db)): return await _analysis(db,body)
async def _analysis(db,body):
    a=await FeedbackClassifier().classify(body.text); i=await identity.classify(db,body.text,body.product_area or a.product_area,body.platform or a.platform,body.segment or a.segment)
    db.add(AnalysisAudit(operation='feedback_analysis',input_text=body.text,model=(settings.llm_model or 'deterministic-fallback'),prompt_version='feedback_analysis_v1',retrieved_memories=[],evidence_ids=[e.get('source_id') for e in i.get('evidence',[])],output_json={'analysis':a.model_dump(),'identity':i},confidence=i.get('confidence',0)))
    await db.commit(); return {'analysis':a.model_dump(),'identity':i,'facts_vs_inferences':{'fact':'The submitted feedback was analyzed using its text and structured attributes.','inference':i.get('reasoning'),'hypothesis':None}}

@app.post('/api/v1/analyze')
async def analyze_alias(body:AnalysisIn,db:AsyncSession=Depends(get_db)): return await _analysis(db,body)

@app.get('/api/v1/problems')
async def list_problems(status:str|None=None,db:AsyncSession=Depends(get_db)):
    q=select(Problem).order_by(Problem.last_seen_at.desc());
    if status:q=q.where(Problem.status==status)
    return [serialize_problem(p) for p in (await db.execute(q)).scalars().all()]

def serialize_problem(p): return {'id':p.id,'canonical_title':p.canonical_title,'canonical_description':p.canonical_description,'status':p.status,'severity':p.severity,'product_area':p.product_area,'occurrence_count':p.occurrence_count,'current_sentiment':p.current_sentiment,'segments':p.customer_segments,'first_seen_at':p.first_seen_at,'last_seen_at':p.last_seen_at,'current_state':p.current_state}

@app.post('/api/v1/problems')
async def create_problem(body:ProblemCreate,db:AsyncSession=Depends(get_db)):
    p=Problem(canonical_title=body.canonical_title,canonical_description=body.canonical_description,problem_type=body.product_type,product_area=body.product_area,severity=body.severity,status=body.status,first_seen_at=body.first_seen_at,last_seen_at=body.last_seen_at,customer_segments=body.customer_segments,current_state=body.current_state); db.add(p); await db.commit(); await db.refresh(p); return serialize_problem(p)

@app.get('/api/v1/problems/{problem_id}')
async def get_problem(problem_id:str,db:AsyncSession=Depends(get_db)):
    detail=await problem_service.detail(db,problem_id)
    if not detail: raise HTTPException(404,'Problem not found')
    p=await db.get(Problem,problem_id); detail['problem']['status']=p.status; detail['resurrection']=await resurrection.detect(db,p); detail['contradictions']=[await contradictions.check(db,p)]; detail['evidence']=await evidence_service.for_problem(db,problem_id); detail['memory_summary']=[m.content for m in (await db.execute(select(MemoryRecord).where(MemoryRecord.provenance.contains({'problem_id':problem_id})).limit(20))).scalars().all()]; detail['confidence']=detail['resurrection']['confidence']; return detail

@app.get('/api/v1/problems/{problem_id}/timeline')
async def timeline(problem_id:str,db:AsyncSession=Depends(get_db)):
    p=await db.get(Problem,problem_id)
    if not p: raise HTTPException(404,'Problem not found')
    decisions=(await db.execute(select(Decision).where(Decision.problem_id==problem_id).order_by(Decision.timestamp))).scalars().all(); ints=(await db.execute(select(Intervention).where(Intervention.problem_id==problem_id).order_by(Intervention.timestamp))).scalars().all()
    all_feedback=(await db.execute(select(Feedback).order_by(Feedback.timestamp))).scalars().all()
    linked_feedback=[f for f in all_feedback if (f.metadata_json or {}).get('problem_id')==problem_id]
    events=[{'date':f.timestamp,'type':'feedback','title':'Customer signal','detail':f.text,'source':f.source,'feedback_id':f.id} for f in linked_feedback]
    if not events: events=[{'date':p.first_seen_at,'type':'feedback','title':'Problem detected','detail':p.canonical_description}]
    for d in decisions: events.append({'date':d.timestamp,'type':'decision','title':d.decision,'detail':d.rationale})
    for i in ints:
        events.append({'date':i.timestamp,'type':'intervention','title':i.name,'detail':i.why});
        for o in (await db.execute(select(Outcome).where(Outcome.intervention_id==i.id).order_by(Outcome.timestamp))).scalars().all(): events.append({'date':o.timestamp,'type':'outcome','title':o.outcome_type,'detail':o.qualitative_evidence,'metric':o.metric})
    return {'problem_id':problem_id,'events':sorted(events,key=lambda x:x['date']),'relationships':await evolution.graph(db,problem_id)}

@app.get('/api/v1/problems/{problem_id}/evolution')
async def evolution_graph(problem_id:str,db:AsyncSession=Depends(get_db)): return await evolution.graph(db,problem_id)
@app.get('/api/v1/problems/{problem_id}/evidence')
async def problem_evidence(problem_id:str,db:AsyncSession=Depends(get_db)): return await evidence_service.for_problem(db,problem_id)
@app.get('/api/v1/problems/{problem_id}/memory')
async def problem_memory(problem_id:str,db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(MemoryRecord))).scalars().all(); return [ {'id':m.id,'type':m.memory_type,'content':m.content,'confidence':m.confidence,'stale':m.is_stale,'provenance':m.provenance} for m in rows if m.provenance.get('problem_id')==problem_id or 'checkout' in m.content.lower()]

@app.get('/api/v1/problems/resurrected')
async def resurrected(db:AsyncSession=Depends(get_db)): return [await resurrection.detect(db,p) for p in (await db.execute(select(Problem).where(Problem.occurrence_count>1))).scalars().all()]
@app.get('/api/v1/problems/emerging')
async def emerging(db:AsyncSession=Depends(get_db)): return await EmergingEngine().list(db)

@app.get('/api/v1/decisions')
async def list_decisions(problem_id:str|None=None,db:AsyncSession=Depends(get_db)):
    q=select(Decision).order_by(Decision.timestamp.desc())
    if problem_id: q=q.where(Decision.problem_id==problem_id)
    return [{k:v for k,v in d.__dict__.items() if not k.startswith('_')} for d in (await db.execute(q)).scalars().all()]

@app.post('/api/v1/decisions')
async def create_decision(body:DecisionIn,db:AsyncSession=Depends(get_db)):
    d=Decision(**body.model_dump()); db.add(d); await db.commit();
    if mem.configured: await mem.retain(f'Decision: {d.decision}. Rationale: {d.rationale}',context='TRACE product decision',timestamp=d.timestamp)
    return {'id':d.id,'status':'stored'}

@app.post('/api/v1/interventions')
async def create_intervention(body:InterventionIn,db:AsyncSession=Depends(get_db)):
    i=await intervention_service.create(db,body)
    if mem.configured: await mem.retain(f'Intervention: {i.name}. Why: {i.why}. Target: {i.target_segment or "unknown"} on {i.target_platform or "unknown"}.',context='TRACE intervention memory',timestamp=i.timestamp)
    return {'id':i.id,'problem_id':i.problem_id,'name':i.name,'status':i.status}
@app.get('/api/v1/interventions')
async def list_interventions(problem_id:str|None=None,db:AsyncSession=Depends(get_db)): return [i.__dict__ for i in await intervention_service.list(db,problem_id)]
@app.post('/api/v1/interventions/check')
async def intervention_check(body:InterventionCheckIn,db:AsyncSession=Depends(get_db)): return await interventions.check(db,body.problem_id,body.proposed_intervention)

@app.post('/api/v1/outcomes')
async def create_outcome(body:OutcomeIn,db:AsyncSession=Depends(get_db)):
    o=await outcome_service.create(db,body)
    if mem.configured: await mem.retain(f'Outcome: {o.outcome_type}. Evidence: {o.qualitative_evidence}. Metrics: {o.metric}',context='TRACE intervention outcome',timestamp=o.timestamp)
    return {'id':o.id,'outcome_type':o.outcome_type}
@app.get('/api/v1/outcomes')
async def list_outcomes(intervention_id:str|None=None,db:AsyncSession=Depends(get_db)):
    q=select(Outcome).order_by(Outcome.timestamp.desc());
    if intervention_id:q=q.where(Outcome.intervention_id==intervention_id)
    return [o.__dict__ for o in (await db.execute(q)).scalars().all()]

@app.get('/api/v1/contradictions')
async def contradictions_list(db:AsyncSession=Depends(get_db)):
    out=[]
    for p in (await db.execute(select(Problem))).scalars().all():
        r=await contradictions.check(db,p)
        if r['contradiction_detected']: out.append({'problem_id':p.id,**r})
    return out
@app.get('/api/v1/problems/{problem_id}/resurrection')
async def resurrection_check(problem_id:str,db:AsyncSession=Depends(get_db)):
    p=await db.get(Problem,problem_id)
    if not p: raise HTTPException(404,'Problem not found')
    return await resurrection.detect(db,p)
@app.get('/api/v1/problems/{problem_id}/contradictions')
async def contradiction_check(problem_id:str,db:AsyncSession=Depends(get_db)):
    p=await db.get(Problem,problem_id)
    if not p: raise HTTPException(404,'Problem not found')
    return await contradictions.check(db,p)

@app.get('/api/v1/decision-debt')
async def decision_debt(db:AsyncSession=Depends(get_db)): return await DecisionDebtEngine().list(db)
@app.get('/api/v1/stale-memory')
async def stale_memory(db:AsyncSession=Depends(get_db)): return [ {'id':m.id,'type':m.memory_type,'content':m.content,'confidence':m.confidence,'stale':m.is_stale,'provenance':m.provenance} for m in (await db.execute(select(MemoryRecord).where(MemoryRecord.is_stale.is_(True)))).scalars().all()]

@app.post('/api/v1/stale-memory/detect')
async def detect_stale_memory(db:AsyncSession=Depends(get_db)):
    memories=list((await db.execute(select(MemoryRecord))).scalars().all())
    feedback=list((await db.execute(select(Feedback).order_by(Feedback.timestamp.desc()).limit(500)))).scalars().all()
    current_text=' '.join((f.text or '').lower() for f in feedback)
    flagged=[]
    for m in memories:
        provenance=m.provenance or {}
        historical_platform=str(provenance.get('platform','')).lower()
        if historical_platform and historical_platform not in current_text and not m.is_stale:
            m.is_stale=True; flagged.append(m.id)
    if flagged: await db.commit()
    return {'checked':len(memories),'flagged':flagged,'message':'Historical memories are retained; flagged records are marked stale rather than deleted.'}


@app.post('/api/v1/stale-memory/{memory_id}/flag')
async def flag_stale_memory(memory_id:str,db:AsyncSession=Depends(get_db)):
    m=await db.get(MemoryRecord,memory_id)
    if not m: raise HTTPException(404,'Memory record not found')
    m.is_stale=True; await db.commit()
    return {'id':m.id,'stale':True,'message':'Historical memory retained and marked stale.'}

@app.post('/api/v1/memory/retain')
async def memory_retain(body:MemoryIn,db:AsyncSession=Depends(get_db)):
    record=MemoryRecord(memory_type=body.memory_type,content=body.content,confidence=body.confidence,provenance=body.metadata)
    db.add(record); await db.commit(); await db.refresh(record)
    if not mem.configured:
        return {'configured':False,'stored_locally':True,'memory_id':record.id,'message':'Hindsight is not configured; Memory Replay will not claim live Hindsight.'}
    try:
        result=await mem.retain(body.content,body.context,body.timestamp,body.memory_type,body.metadata)
        return {'configured':True,'stored_locally':True,'memory_id':record.id,'result':result}
    except HindsightUnavailable as e:
        return {'configured':False,'stored_locally':True,'memory_id':record.id,'message':str(e)}
@app.post('/api/v1/memory/recall')
async def memory_recall(body:dict):
    try: return {'configured':True,'result':await mem.recall(body.get('query',''),body.get('query_timestamp'))}
    except HindsightUnavailable as e: raise HTTPException(503,str(e))
@app.post('/api/v1/memory/reflect')
async def memory_reflect(body:dict):
    try: return {'configured':True,'result':await mem.reflect(body.get('query',''),body.get('context'))}
    except HindsightUnavailable as e: raise HTTPException(503,str(e))
@app.get('/api/v1/memory/status')
async def memory_status(): return {'configured':mem.configured,'bank_id':settings.hindsight_bank_id,'operations':['retain','recall','reflect'],'truthfulness':'Memory ON is unavailable unless Hindsight is configured.'}

@app.post('/api/v1/replay')
async def replay(body:ReplayIn,db:AsyncSession=Depends(get_db)):
    try: return await replay_service.run(db,body.scenario_id,body.query)
    except HindsightUnavailable as e: raise HTTPException(503,str(e))

@app.post('/api/v1/agent/ask')
async def agent(body:AgentIn):
    try:
        r=await mem.reflect(body.query,context='TRACE product intelligence. Distinguish facts, inferences and hypotheses. Do not make autonomous product decisions.')
        return {'configured':True,'text':r.get('text',''),'based_on':r.get('based_on',[]),'source':'hindsight'}
    except HindsightUnavailable: return {'configured':False,'text':'Hindsight is not configured. Connect Hindsight to enable live historical reasoning.','based_on':[],'source':'unavailable'}

@app.post('/api/v1/evaluation/run')
async def evaluation_run(body:EvaluationIn,db:AsyncSession=Depends(get_db)): return await evaluation_service.run(db,body.scenario_ids)
@app.get('/api/v1/evaluation/results')
async def evaluation_results(db:AsyncSession=Depends(get_db)): return [{'id':r.id,'scenario_id':r.scenario_id,'score':r.score,'results':r.results,'timestamp':r.timestamp} for r in await evaluation_service.latest(db)]
@app.get('/api/v1/evaluation/health')
async def evaluation_health(db:AsyncSession=Depends(get_db)): return {'checks':['identity','resurrection','intervention memory','outcomes','contradictions','evolution','evidence','stale memory','decision debt','replay'],'status':'ready'}

@app.post('/api/v1/demo/reset')
async def demo_reset(db:AsyncSession=Depends(get_db)): await seed(db,reset=True); return {'ok':True,'message':'Demo dataset reset and seeded.'}
@app.post('/api/v1/demo/seed')
async def demo_seed(db:AsyncSession=Depends(get_db)):
    await seed(db)
    hindsight_seeded=False
    if mem.configured:
        facts=['Mobile checkout reliability was first detected in January 2026.','The team chose checkout navigation simplification in February 2026.','Checkout navigation simplification shipped in March 2026.','The intervention partially succeeded: desktop complaints fell 61%, while mobile complaints persisted.','Mobile conversion improved only 2% after the later intervention, below the intended target.','New Android complaints in September 2026 indicate a possible recurrence or evolution; this is not a confirmed causal claim.']
        for fact in facts: await mem.retain(fact,context='TRACE synthetic longitudinal demo scenario')
        hindsight_seeded=True
    return {'ok':True,'message':'Demo dataset ready.','scenario':'mobile_checkout_resurrection','hindsight_seeded':hindsight_seeded}
@app.post('/api/v1/ingestion/upload')
async def ingestion_upload(file:UploadFile=File(...),db:AsyncSession=Depends(get_db)):
    if file.content_type not in {'text/csv','application/json','text/plain','application/vnd.ms-excel'}: raise HTTPException(415,'Only CSV or JSON uploads are supported.')
    data=await file.read()
    if len(data)>settings.request_max_bytes: raise HTTPException(413,'Upload exceeds configured size limit.')
    try:
        if (file.filename or '').lower().endswith('.json') or file.content_type=='application/json':
            payload=json.loads(data.decode('utf-8')); rows=payload if isinstance(payload,list) else payload.get('items',[])
        else:
            rows=list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))
        accepted=0; duplicates=0; errors=[]
        for idx,row in enumerate(rows,1):
            try:
                source=str(row.get('source') or 'manually_entered'); text=str(row.get('text') or '').strip(); timestamp=datetime.fromisoformat(str(row.get('timestamp') or '').replace('Z','+00:00')).replace(tzinfo=None)
                if not text: raise ValueError('text is required')
                item=FeedbackIn(source=source,text=text,timestamp=timestamp,source_external_id=row.get('source_external_id'),customer_id=row.get('customer_id'),product_id=row.get('product_id'),product_version=row.get('product_version'),rating=float(row['rating']) if row.get('rating') not in (None,'') else None,sentiment=row.get('sentiment'),language=row.get('language') or 'en',metadata={k:v for k,v in row.items() if k not in {'source','text','timestamp','source_external_id','customer_id','product_id','product_version','rating','sentiment','language'}})
                f,created=await feedback_service.ingest(db,item); duplicates += 0 if created else 1; accepted += 1 if created else 0
            except Exception as exc: errors.append({'row':idx,'error':str(exc)})
        await db.commit(); return {'accepted':True,'filename':file.filename,'rows_received':len(rows),'ingested':accepted,'duplicates':duplicates,'errors':errors[:50],'progress':1.0}
    except (UnicodeDecodeError,json.JSONDecodeError) as exc: raise HTTPException(400,f'Invalid dataset: {exc}')
