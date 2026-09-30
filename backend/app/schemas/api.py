from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict

class FeedbackIn(BaseModel):
    source:str; text:str=Field(min_length=3,max_length=10000); timestamp:datetime; source_external_id:str|None=None; customer_id:str|None=None; product_id:str|None=None; product_version:str|None=None; rating:float|None=None; sentiment:str|None=None; language:str='en'; metadata:dict[str,Any]=Field(default_factory=dict)
class FeedbackBatchIn(BaseModel): items:list[FeedbackIn]=Field(min_length=1,max_length=1000)
class AnalysisIn(BaseModel): text:str=Field(min_length=3); timestamp:datetime|None=None; product_area:str|None=None; platform:str|None=None; segment:str|None=None
class ProblemCreate(BaseModel): canonical_title:str; canonical_description:str; product_type:str='customer_pain'; product_area:str; severity:str='medium'; status:str='EMERGING'; first_seen_at:datetime; last_seen_at:datetime; customer_segments:list[str]=Field(default_factory=list); current_state:dict[str,Any]=Field(default_factory=dict)
class InterventionIn(BaseModel): problem_id:str; name:str; why:str; target_segment:str|None=None; target_platform:str|None=None; expected_outcome:str; timestamp:datetime; decision_maker:str|None=None; status:str='TESTED'
class InterventionCheckIn(BaseModel): problem_id:str; proposed_intervention:str=Field(min_length=3)
class OutcomeIn(BaseModel): intervention_id:str; outcome_type:Literal['SUCCESS','PARTIAL_SUCCESS','FAILURE','INCONCLUSIVE','REGRESSION','NO_MEASURABLE_CHANGE']; qualitative_evidence:str; metric:dict[str,Any]=Field(default_factory=dict); measurement_window_days:int|None=None; timestamp:datetime
class DecisionIn(BaseModel): problem_id:str; decision:str; rationale:str; decision_maker:str|None=None; timestamp:datetime
class AgentIn(BaseModel): query:str=Field(min_length=3)
class ReplayIn(BaseModel): scenario_id:str='mobile_checkout_resurrection'; query:str=Field(min_length=3)
class EvaluationIn(BaseModel): scenario_ids:list[str]|None=None
class MemoryIn(BaseModel): content:str; context:str='TRACE'; timestamp:datetime|None=None; metadata:dict[str,Any]=Field(default_factory=dict); memory_type:str='FACT'; confidence:float=Field(default=1,ge=0,le=1)
class ProblemIdentityOut(BaseModel): classification:str; problem_id:str|None=None; confidence:float; reasoning:str; evidence:list[dict[str,Any]]
class ErrorBody(BaseModel): code:str; message:str; request_id:str
