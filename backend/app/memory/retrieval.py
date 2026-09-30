class HistoricalRetriever:
    def __init__(self,memory_service): self.memory=memory_service
    async def for_problem(self,problem,query=None):
        q=query or problem.canonical_title
        return await self.memory.recall(q,context=f"product area: {problem.product_area}; status: {problem.status}",limit=10)
