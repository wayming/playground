import asyncio

class AsyncMyIterator:
    def __init__(self, n):
        self.n = n
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if not self.n:
            raise StopAsyncIteration
        
        res = self.n
        self.n -= 1
        return res
    

async def run1():
    it = AsyncMyIterator(10)
    async for i in it:
        print(i)

asyncio.run(run1())