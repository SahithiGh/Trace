from sqlalchemy.ext.asyncio import AsyncSession
from .engines import ProblemIdentityEngine
from ..ai.classifiers import FeedbackClassifier

class AnalysisService:
    def __init__(self): self.identity=ProblemIdentityEngine(); self.classifier=FeedbackClassifier()
    async def analyze(self,db:AsyncSession,text,product_area=None,platform=None,segment=None):
        cls=await self.classifier.classify(text); ident=await self.identity.classify(db,text,product_area or cls.product_area,platform or cls.platform,segment or cls.segment)
        return {'analysis':cls.model_dump(),'identity':ident}
