from pydantic import BaseModel, Field
class IdentityOutput(BaseModel):
    classification:str; problem_id:str|None=None; confidence:float=Field(ge=0,le=1); reasoning:str; evidence:list[dict]=Field(default_factory=list)
class FeedbackAnalysisOutput(BaseModel):
    sentiment:str; product_area:str; urgency:str; severity:str; platform:str; segment:str; intent:str; problem_title:str
