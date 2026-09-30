from app.models import Feedback, Problem, Decision, Intervention, Outcome, Evidence, Relationship, AnalysisAudit, MemoryRecord, EvaluationRun

def test_core_entities_exist():
    assert all([Feedback.__tablename__,Problem.__tablename__,Decision.__tablename__,Intervention.__tablename__,Outcome.__tablename__,Evidence.__tablename__,Relationship.__tablename__,AnalysisAudit.__tablename__,MemoryRecord.__tablename__,EvaluationRun.__tablename__])
