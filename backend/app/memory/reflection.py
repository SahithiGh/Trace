class MemoryReflector:
    def __init__(self,memory_service): self.memory=memory_service
    async def learn(self,query,context='TRACE product intelligence'):
        return await self.memory.reflect(query,context=context)
