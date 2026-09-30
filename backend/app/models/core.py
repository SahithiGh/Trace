from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Text, Float, Integer, DateTime, JSON, ForeignKey, Boolean, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base

def uid(): return str(uuid4())

def now(): return datetime.utcnow()

class Feedback(Base):
    __tablename__='feedback'
    __table_args__=(UniqueConstraint('source','source_external_id',name='uq_feedback_source_external'), Index('ix_feedback_timestamp','timestamp'), Index('ix_feedback_product','product_id'), Index('ix_feedback_customer','customer_id'))
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid)
    source: Mapped[str]=mapped_column(String(40)); source_external_id: Mapped[str|None]=mapped_column(String(120),nullable=True)
    customer_id: Mapped[str|None]=mapped_column(String(120),nullable=True); product_id: Mapped[str|None]=mapped_column(String(120),nullable=True); product_version: Mapped[str|None]=mapped_column(String(80),nullable=True)
    timestamp: Mapped[datetime]=mapped_column(DateTime); text: Mapped[str]=mapped_column(Text); rating: Mapped[float|None]=mapped_column(Float,nullable=True)
    sentiment: Mapped[str|None]=mapped_column(String(30),nullable=True); language: Mapped[str]=mapped_column(String(12),default='en'); metadata_json: Mapped[dict]=mapped_column('metadata',JSON,default=dict); created_at: Mapped[datetime]=mapped_column(DateTime,default=now)

class Problem(Base):
    __tablename__='problems'; __table_args__=(Index('ix_problem_last_seen','last_seen_at'),Index('ix_problem_status','status'))
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); canonical_title: Mapped[str]=mapped_column(String(200)); canonical_description: Mapped[str]=mapped_column(Text)
    problem_type: Mapped[str]=mapped_column(String(80)); product_area: Mapped[str]=mapped_column(String(100)); severity: Mapped[str]=mapped_column(String(30)); status: Mapped[str]=mapped_column(String(30))
    first_seen_at: Mapped[datetime]=mapped_column(DateTime); last_seen_at: Mapped[datetime]=mapped_column(DateTime); occurrence_count: Mapped[int]=mapped_column(Integer,default=1)
    current_sentiment: Mapped[float]=mapped_column(Float,default=0); historical_sentiment_summary: Mapped[dict]=mapped_column(JSON,default=dict); customer_segments: Mapped[list]=mapped_column(JSON,default=list); current_state: Mapped[dict]=mapped_column(JSON,default=dict)
    created_at: Mapped[datetime]=mapped_column(DateTime,default=now); updated_at: Mapped[datetime]=mapped_column(DateTime,default=now,onupdate=now)

class Decision(Base):
    __tablename__='decisions'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); problem_id: Mapped[str]=mapped_column(String(36),ForeignKey('problems.id',ondelete='CASCADE')); decision: Mapped[str]=mapped_column(Text); rationale: Mapped[str]=mapped_column(Text); decision_maker: Mapped[str|None]=mapped_column(String(120),nullable=True); timestamp: Mapped[datetime]=mapped_column(DateTime)

class Intervention(Base):
    __tablename__='interventions'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); problem_id: Mapped[str]=mapped_column(String(36),ForeignKey('problems.id',ondelete='CASCADE')); name: Mapped[str]=mapped_column(String(200)); why: Mapped[str]=mapped_column(Text); target_segment: Mapped[str|None]=mapped_column(String(120),nullable=True); target_platform: Mapped[str|None]=mapped_column(String(80),nullable=True); expected_outcome: Mapped[str]=mapped_column(Text); timestamp: Mapped[datetime]=mapped_column(DateTime); decision_maker: Mapped[str|None]=mapped_column(String(120),nullable=True); status: Mapped[str]=mapped_column(String(40),default='TESTED')

class Outcome(Base):
    __tablename__='outcomes'; __table_args__=(Index('ix_outcome_intervention','intervention_id'),)
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); intervention_id: Mapped[str]=mapped_column(String(36),ForeignKey('interventions.id',ondelete='CASCADE')); outcome_type: Mapped[str]=mapped_column(String(40)); qualitative_evidence: Mapped[str]=mapped_column(Text); metric: Mapped[dict]=mapped_column(JSON,default=dict); measurement_window_days: Mapped[int|None]=mapped_column(Integer,nullable=True); timestamp: Mapped[datetime]=mapped_column(DateTime)

class Evidence(Base):
    __tablename__='evidence'; __table_args__=(Index('ix_evidence_source','source_id'),)
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); source_type: Mapped[str]=mapped_column(String(50)); source_id: Mapped[str]=mapped_column(String(120)); evidence_type: Mapped[str]=mapped_column(String(50)); content: Mapped[str]=mapped_column(Text); timestamp: Mapped[datetime]=mapped_column(DateTime); relevance: Mapped[float]=mapped_column(Float,default=.8); confidence: Mapped[float]=mapped_column(Float,default=.8); created_at: Mapped[datetime]=mapped_column(DateTime,default=now)

class Relationship(Base):
    __tablename__='relationships'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); from_problem_id: Mapped[str]=mapped_column(String(36),ForeignKey('problems.id',ondelete='CASCADE')); to_problem_id: Mapped[str]=mapped_column(String(36),ForeignKey('problems.id',ondelete='CASCADE')); relation_type: Mapped[str]=mapped_column(String(40)); confidence: Mapped[float]=mapped_column(Float); evidence: Mapped[list]=mapped_column(JSON,default=list)

class AnalysisAudit(Base):
    __tablename__='analysis_audits'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); operation: Mapped[str]=mapped_column(String(80)); input_text: Mapped[str]=mapped_column(Text); model: Mapped[str]=mapped_column(String(120),default='deterministic-fallback'); prompt_version: Mapped[str]=mapped_column(String(80),default='v1'); retrieved_memories: Mapped[list]=mapped_column(JSON,default=list); evidence_ids: Mapped[list]=mapped_column(JSON,default=list); output_json: Mapped[dict]=mapped_column(JSON,default=dict); confidence: Mapped[float]=mapped_column(Float,default=0); timestamp: Mapped[datetime]=mapped_column(DateTime,default=now); request_id: Mapped[str|None]=mapped_column(String(64),nullable=True)

class MemoryRecord(Base):
    __tablename__='memory_records'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); memory_type: Mapped[str]=mapped_column(String(40)); content: Mapped[str]=mapped_column(Text); confidence: Mapped[float]=mapped_column(Float,default=1); provenance: Mapped[dict]=mapped_column(JSON,default=dict); hindsight_id: Mapped[str|None]=mapped_column(String(160),nullable=True); is_stale: Mapped[bool]=mapped_column(Boolean,default=False); created_at: Mapped[datetime]=mapped_column(DateTime,default=now); updated_at: Mapped[datetime]=mapped_column(DateTime,default=now,onupdate=now)

class EvaluationRun(Base):
    __tablename__='evaluation_runs'
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=uid); scenario_id: Mapped[str]=mapped_column(String(120)); results: Mapped[dict]=mapped_column(JSON,default=dict); score: Mapped[float]=mapped_column(Float,default=0); timestamp: Mapped[datetime]=mapped_column(DateTime,default=now)
