import asyncio
import dataclasses
import datetime


@dataclasses.dataclass
class TokenBucketStats:
    allocated: int
    remaining: int


class TokenBucket:
    def __init__(self, capacity, rate):
        self.cap = capacity
        self.rate = rate
        self.lock = asyncio.Lock()
        self.allocate_time = datetime.datetime.now()
        self.remaining = capacity
        self.stats = TokenBucketStats(0, self.remaining)

    async def wait_for_token(self, require):
        async with self.lock:
            if self.remaining >= require:
                self.remaining -= require
                self.stats.allocated += require
                self.stats.remaining = self.remaining
                return
            while True:
                now = datetime.datetime.now()
                new_tokens = int((now - self.allocate_time).total_seconds() * self.rate)

                if self.remaining + new_tokens >= require:
                    self.remaining += new_tokens
                    self.remaining -= require
                    self.stats.allocated += require
                    self.stats.remaining = self.remaining
                    return

                await asyncio.sleep(min(0.1, 1 / self.rate))

    async def get_stats(self):
        async with self.lock:
            return self.stats
