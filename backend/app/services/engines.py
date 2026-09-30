from datetime import datetime, timedelta
from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from ..models import Problem, Intervention, Outcome, Evidence, Relationship, Feedback, Decision, MemoryRecord

STOP={'the','a','an','is','are','on','in','to','of','and','for','with','from','this','that','still','again'}
def tokens(s): return {x.strip('.,!?()[]{}').lower() for x in s.replace('/',' ').replace('-',' ').split() if len(x)>2 and x.lower() not in STOP}

def dna(text, product_area=None, platform=None, segment=None):
    t=text.lower(); return {'product_area':product_area or ('checkout' if 'checkout' in t or 'payment' in t else 'unknown'),'user_goal':'complete purchase' if any(x in t for x in ['checkout','payment','purchase']) else 'complete task','failure_mode':'payment failure' if 'payment' in t and any(x in t for x in ['fail','error','declin']) else ('performance/reliability' if any(x in t for x in ['slow','freeze','crash','fail']) else 'usability friction'),'platform':platform or ('mobile' if any(x in t for x in ['mobile','android','ios','phone']) else 'web'),'segment':segment or ('android users' if 'android' in t else 'mobile shoppers')}

class ProblemIdentityEngine:
    async def classify(self,db:AsyncSession,text,product_area=None,platform=None,segment=None):
        d=dna(text,product_area,platform,segment); ts=tokens(text); problems=(await db.execute(select(Problem))).scalars().all(); candidates=[]
        for p in problems:
            pd=p.current_state or {}; ptext=f'{p.canonical_title} {p.canonical_description} {p.product_area} {" ".join(p.customer_segments)} {pd.get("failure_mode","")} {pd.get("platform","")}'
            overlap=len(ts & tokens(ptext))/max(1,len(ts)); attrs=sum([p.product_area.lower()==d['product_area'].lower(),str(pd.get('platform','')).lower()==d['platform'].lower(),str(pd.get('failure_mode','')).lower()==d['failure_mode'].lower(),any(d['segment'].lower() in s.lower() for s in p.customer_segments)])
            score=min(0.99,overlap+attrs*.12)
            if score>.12: candidates.append((score,p))
        candidates.sort(key=lambda x:x[0],reverse=True); best=candidates[0] if candidates else None
        if not best: return {'classification':'NEW_PROBLEM','problem_id':None,'confidence':.72,'reasoning':'No sufficiently supported historical problem match.','evidence':[],'problem_dna':d}
        score,p=best; historical_gap=(datetime.utcnow()-p.last_seen_at).days if p.last_seen_at else 0
        if score>=.38 and historical_gap>30 and p.occurrence_count>1: cls='RESURRECTED_PROBLEM'
        elif score>=.48: cls='SAME_PROBLEM'
        elif score>=.22 and (d['failure_mode']!=str((p.current_state or {}).get('failure_mode',''))): cls='EVOLVED_PROBLEM'
        else: cls='RELATED_PROBLEM'
        evidence=[{'source_type':'problem','source_id':p.id,'content':p.canonical_description,'confidence':round(score,2)}]
        return {'classification':cls,'problem_id':p.id,'confidence':round(min(.99,.55+score*.45),2),'reasoning':f'Historical match based on problem DNA, product area, platform, failure mode and segment; {historical_gap} days since last observed.','evidence':evidence,'problem_dna':d}

class ResurrectionEngine:
    async def detect(self,db,p):
        ints=(await db.execute(select(Intervention).where(Intervention.problem_id==p.id).order_by(Intervention.timestamp))).scalars().all(); outs=[]
        for i in ints: outs += (await db.execute(select(Outcome).where(Outcome.intervention_id==i.id).order_by(Outcome.timestamp))).scalars().all()
        recurrence=p.occurrence_count>1 or p.status in {'RECURRING','REGRESSING'}
        return {'resurrected':recurrence,'original_problem_id':p.id,'confidence':.91 if recurrence and outs else (.72 if recurrence else .18),'reason':'Possible recurrence after historical intervention.' if recurrence and ints else ('Repeated observations suggest recurrence.' if recurrence else 'No supported recurrence signal.'),'previous_interventions':[{'id':i.id,'name':i.name,'date':i.timestamp.isoformat()} for i in ints],'previous_outcomes':[{'type':o.outcome_type,'evidence':o.qualitative_evidence,'metric':o.metric} for o in outs]}

class InterventionMemoryEngine:
    async def check(self,db,problem_id,proposed):
        ints=(await db.execute(select(Intervention).where(Intervention.problem_id==problem_id))).scalars().all(); pt=tokens(proposed); matches=[]
        for i in ints:
            sim=len(pt & tokens(i.name+' '+i.why))/max(1,len(pt));
            if sim>=.15:
                outs=(await db.execute(select(Outcome).where(Outcome.intervention_id==i.id).order_by(Outcome.timestamp))).scalars().all(); matches.append({'intervention':i.name,'date':i.timestamp.isoformat(),'target_segment':i.target_segment,'target_platform':i.target_platform,'expected_outcome':i.expected_outcome,'outcomes':[{'type':o.outcome_type,'what_worked':o.qualitative_evidence,'metric':o.metric} for o in outs],'confidence':round(min(.99,.55+sim*.44),2)})
        return {'historical_matches':matches,'found':bool(matches)}

class ContradictionEngine:
    async def check(self,db,p):
        ints=(await db.execute(select(Intervention).where(Intervention.problem_id==p.id))).scalars().all(); outs=[]
        for i in ints: outs += (await db.execute(select(Outcome).where(Outcome.intervention_id==i.id))).scalars().all()
        solved=any(o.outcome_type=='SUCCESS' for o in outs); current=p.status in {'RECURRING','REGRESSING'}
        return {'contradiction_detected':bool(solved and current),'historical_claim':'Historical evidence suggested the problem was solved.' if solved else None,'current_evidence':[{'source_type':'problem','source_id':p.id,'content':f'Current status: {p.status}'}], 'possible_explanations':['problem returned','original fix addressed only one segment','product or platform changed','problem evolved','historical conclusion may have been premature'] if solved and current else [],'confidence':.84 if solved and current else .2}

class EvolutionEngine:
    async def graph(self,db,problem_id):
        rels=(await db.execute(select(Relationship).where(or_(Relationship.from_problem_id==problem_id,Relationship.to_problem_id==problem_id)))).scalars().all(); return [{'from':r.from_problem_id,'to':r.to_problem_id,'type':r.relation_type,'confidence':r.confidence,'evidence':r.evidence} for r in rels]

class SentimentEngine:
    async def trend(self,db,problem_id):
        p=await db.get(Problem,problem_id); ifalse=[]
        if not p:return []
        fb=(await db.execute(select(Feedback).where(Feedback.timestamp.between(p.first_seen_at,p.last_seen_at)).order_by(Feedback.timestamp))).scalars().all()
        buckets={}
        for f in fb:
            key=f.timestamp.strftime('%Y-%m'); val={'negative':-1,'neutral':0,'positive':1}.get((f.sentiment or '').lower(),0); buckets.setdefault(key,[]).append(val)
        return [{'month':k,'sentiment':round(sum(v)/len(v),2),'signals':len(v)} for k,v in sorted(buckets.items())]

class EmergingEngine:
    async def list(self,db):
        rows=(await db.execute(select(Problem).order_by(Problem.occurrence_count.desc()))).scalars().all(); return [{'problem_id':p.id,'emerging':p.status=='EMERGING','growth_rate':round(max(0,(p.occurrence_count-1)/max(1,(datetime.utcnow()-p.first_seen_at).days))*30,3),'evidence':[{'source_type':'problem','source_id':p.id,'content':f'{p.occurrence_count} observed occurrences'}]} for p in rows if p.status=='EMERGING']

class DecisionDebtEngine:
    async def list(self,db):
        probs=(await db.execute(select(Problem))).scalars().all(); out=[]
        for p in probs:
            dc=(await db.execute(select(func.count(Decision.id)).where(Decision.problem_id==p.id))).scalar_one(); ic=(await db.execute(select(func.count(Intervention.id)).where(Intervention.problem_id==p.id))).scalar_one()
            if p.occurrence_count>=3 and ic==0: out.append({'problem_id':p.id,'title':p.canonical_title,'occurrences':p.occurrence_count,'signal':'Repeatedly observed problem with no recorded intervention.'})
        return out

class StaleMemoryEngine:
    async def list(self,db):
        mems=(await db.execute(select(MemoryRecord).where(MemoryRecord.is_stale==True))).scalars().all(); return [{'id':m.id,'type':m.memory_type,'content':m.content,'confidence':m.confidence} for m in mems]
