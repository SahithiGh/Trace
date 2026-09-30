from .llm_client import LLMClient
from .structured_output import FeedbackAnalysisOutput
from .prompts import IDENTITY_SYSTEM

class FeedbackClassifier:
    def __init__(self): self.llm=LLMClient()
    async def classify(self,text):
        if self.llm.configured:
            schema={'type':'object','properties':{'sentiment':{'type':'string'},'product_area':{'type':'string'},'urgency':{'type':'string'},'severity':{'type':'string'},'platform':{'type':'string'},'segment':{'type':'string'},'intent':{'type':'string'},'problem_title':{'type':'string'}},'required':['sentiment','product_area','urgency','severity','platform','segment','intent','problem_title'],'additionalProperties':False}
            try:
                data=await self.llm.structured(IDENTITY_SYSTEM,text,schema)
                if data:return FeedbackAnalysisOutput.model_validate(data)
            except Exception:
                pass
        t=text.lower(); sentiment='negative' if any(x in t for x in ['bad','slow','fail','broken','confusing','freeze','error','hate']) else ('positive' if any(x in t for x in ['love','great','easy','fast']) else 'neutral')
        platform='mobile' if any(x in t for x in ['mobile','android','ios','phone']) else 'web'; severity='high' if any(x in t for x in ['cannot',"can't",'fail','broken','crash']) else 'medium'; urgency='high' if severity=='high' else 'medium'; product_area='checkout' if any(x in t for x in ['checkout','payment','purchase']) else 'unknown'; intent='report_problem' if sentiment=='negative' else 'feedback'; segment='android users' if 'android' in t else ('mobile shoppers' if platform=='mobile' else 'web users'); title='Mobile checkout reliability' if product_area=='checkout' and platform=='mobile' else 'Emerging product issue'
        return FeedbackAnalysisOutput(sentiment=sentiment,product_area=product_area,urgency=urgency,severity=severity,platform=platform,segment=segment,intent=intent,problem_title=title)
