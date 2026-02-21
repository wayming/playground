import asyncio
import base64
import dataclasses
import datetime
import hashlib


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


@dataclasses.dataclass
class LLMCacheStats:
    size: int
    hits: int
    misses: int


class LLMCache:
    def __init__(self, capacity, ttl):
        self.cap = capacity
        self.ttl = ttl
        self.stats = LLMCacheStats(0, 0, 0)

    async def gen_key(self, input: str):
        cleaned_input = str([x for x in input if x.isalnum()])
        hashed_key = hashlib.sha256(cleaned_input.encode("utf-8")).digest()[:24]
        return base64.b64encode(hashed_key).decode("utf-8")

    async def house_keeping(self):
        pass

    async def get(self, input):
        pass

    async def put(self, input):
        pass

    async def get_stats(self):
        return self.stats
