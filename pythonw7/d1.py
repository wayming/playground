from collections import abc
import asyncio
class MyRange:
    def __init__(self, n:int):
        self.n = n
    
    def __next__(self):
        if self.n > 0:
            r = self.n
            self.n -= 1
            return r
        else:
            raise StopIteration("iteration exhausted")
    
    def __iter__(self):
        return self
    

class MyRange2(abc.AsyncIterator):
    def __init__(self, n:int):
        self.n = n

    async def __anext__(self):
        if self.n > 0:
            r = self.n
            self.n -= 1
            return r
        else:
            raise StopAsyncIteration("iteration exhausted")

    def __iter__(self):
        return self
print(list(MyRange(10)))

async def run():
    res = [x async for x in MyRange2(10)]
    print(res)
asyncio.run(run())
