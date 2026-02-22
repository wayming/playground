import asyncio
import base64
import collections
import dataclasses
import datetime
import hashlib
import logging
import random
import time
import traceback


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


class KeyGenerator:
    def __init__(self):
        pass

    def __call__(self, input: str):
        cleaned_input = str([x for x in input if x.isalnum()])
        hashed_key = hashlib.sha256(cleaned_input.encode("utf-8")).digest()[:24]
        return base64.b64encode(hashed_key).decode("utf-8")


class InFlightDeduper:
    def __init__(self):
        self.call_map: dict[str, asyncio.Task] = {}
        self.key_gen = KeyGenerator()
        self.lock = asyncio.Lock()
        pass

    async def __call__(self, fn, *args):
        key = self.key_gen(args[0])
        task: asyncio.Task
        async with self.lock:
            if key not in self.call_map:
                task = asyncio.create_task(fn(*args))
                # task.add_done_callback(lambda fut, k=key: self.call_map.pop(k, None))
                self.call_map[key] = task
            else:
                task = self.call_map[key]
        try:
            return await task
        except Exception:
            traceback.print_exc()
            raise
        finally:
            async with self.lock:
                if self.call_map.get(key) is task:
                    self.call_map.pop(key, None)


class LLMCache:
    def __init__(self, capacity, ttl):
        self.cap = capacity
        self.ttl_delta = datetime.timedelta(seconds=ttl)
        self.stats = LLMCacheStats(0, 0, 0)
        self.cache = collections.OrderedDict()
        self.lock = asyncio.Lock()
        self.key_gen = KeyGenerator()

    def gen_key(self, input: str):
        return self.key_gen(input)

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
        key = self.gen_key(input)
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
        key = self.gen_key(input)
        async with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                self.cache.setdefault(key, ())
            self.cache[key] = (datetime.datetime.now() + self.ttl_delta, output)
        await self.house_keeping()

    async def get_stats(self):
        return self.stats


class LLM:
    def __init__(self, cache):
        self.cache: LLMCache = cache

    async def call(self, input):

        # Simulate maximum 1 second delay
        await asyncio.sleep(random.randint(1, 100) / 100)

        # 1% chances of timeout
        if random.randint(1, 100) % 10 == 0:
            raise TimeoutError

        return hash(input)

    async def call_retry(self, input, timeout):
        delay = 1
        begin = time.monotonic()
        while True:
            try:
                output = await self.cache.get(input)
                if output is not None:
                    return output

                output = await self.call(input)
                await self.cache.put(input, output)
                return output
            except TimeoutError:
                elasped = time.monotonic() - begin
                if elasped > float(timeout):
                    traceback.print_exc()
                    raise
                remaining = float(timeout) - elasped
                if remaining <= 0:
                    raise
                await asyncio.sleep(min(delay, remaining))
                delay *= 2 * (0.9 + 0.1 * random.random())
            except Exception:
                traceback.print_exc()
                raise


@dataclasses.dataclass
class ASR_LLM_Pipeline_Config:
    input_queue_cap: int = 1000
    token_bucket_cap: int = 50
    token_bucket_rate: int = 5
    llm_cache_cap: int = 100
    llm_cache_ttl: int = 10
    llm_retry_timeout: int = 5


@dataclasses.dataclass
class ASR_LLM_Pipeline_Stats:
    submits: int
    succeeds: int
    error: int
    retries: int


class ASR_LLM_Pipeline:
    def __init__(self, config: ASR_LLM_Pipeline_Config):
        self.input = asyncio.Queue(config.input_queue_cap)
        self.output = asyncio.Queue()
        self.error = asyncio.Queue()

        self.token_bucket = TokenBucket(
            config.token_bucket_cap, config.token_bucket_rate
        )
        self.deduper = InFlightDeduper()
        self.llm_cache = LLMCache(config.llm_cache_cap, config.llm_cache_ttl)
        self.llm = LLM(self.llm_cache)
        self.llm_retry_timeout = config.llm_retry_timeout
        self.closing = asyncio.Event()
        self.stats = ASR_LLM_Pipeline_Stats()
        self.lock = asyncio.Lock()

    async def submit(self, input_message):
        if self.closing.is_set():
            raise Exception("pipeline closing down")
        try:
            await self.input.put(input_message)
            with self.lock:
                self.stats.submits += 1
        except asyncio.QueueFull:
            traceback.print_exc()
            return
        except Exception:
            traceback.print_exc()
            raise

    async def run(self):
        while True:
            if self.input.empty() and self.closing.is_set():
                logging.Info("stop monitoring input queue")
                break

            id, input_bytes = await self.input.get()
            self.input.task_done()
            await self.token_bucket.wait_for_token(1)
            try:
                output = await self.deduper(
                    self.llm.call_retry, input_bytes, self.llm_retry_timeout
                )
                await self.output.put((id, output))
                with self.lock:
                    self.stats.succeeds += 1
            except Exception as e:
                self.error.put((id, input_bytes, e))
                with self.lock:
                    self.stats.error += 1

    async def error_router(self, retry=False):
        while not self.closing.is_set():
            id, input, e = await self.error.get()
            retry_message = "Retry." if retry else "Not Retry."
            logging.warning(
                "Error while processing message id ",
                id,
                ", error: ",
                e,
                " ",
                retry_message,
            )
            if retry and e is TimeoutError:
                await self.input.put((id, input))  # reprocessing
                with self.lock:
                    self.stats.retries += 1

    def shutdown(self):
        self.closing.set()
        logging.Info("asr-llm pipeline closing")
