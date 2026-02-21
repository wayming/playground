import asyncio
import base64
import collections
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
        self.ttl_delta = datetime.timedelta(seconds=ttl)
        self.stats = LLMCacheStats(0, 0, 0)
        self.cache = collections.OrderedDict()
        self.lock = asyncio.Lock()

    async def gen_key(self, input: str):
        cleaned_input = str([x for x in input if x.isalnum()])
        hashed_key = hashlib.sha256(cleaned_input.encode("utf-8")).digest()[:24]
        return base64.b64encode(hashed_key).decode("utf-8")

    async def house_keeping(self):
        now = datetime.datetime.now()
        async with self.lock:
            pops = []
            for k, v in self.cache.items():
                if v[0] < now:
                    pops.append(k)
                else:
                    break
            for k in pops:
                self.cache.pop(k)
            self.stats.size = len(self.cache)

    async def get(self, input):
        key = await self.gen_key(input)
        now = datetime.datetime.now()
        await self.house_keeping()
        async with self.lock:
            if key in self.cache and self.cache[key][0] > now:
                self.cache.move_to_end(key)
                self.cache[key] = (now + self.ttl_delta, self.cache[key][1])
                self.stats.hits += 1
                return self.cache[key][1]
            else:
                self.stats.misses += 1
                return None

    async def put(self, input, output):
        key = await self.gen_key(input)
        async with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
                self.stats.hits += 1
            else:
                self.cache.setdefault(key, ())
                self.stats.misses += 1
            self.cache[key] = (datetime.datetime.now() + self.ttl_delta, output)
        await self.house_keeping()

    async def get_stats(self):
        return self.stats
