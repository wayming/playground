import datetime
import asyncio
import hashlib
import random
import traceback



class TokenBucket():
    def __init__(self, capacity, rate):
        self.rate = rate
        self.allocated_time = datetime.datetime.now()
        self.capacity = capacity
        self.tokens = capacity
        self.lock = asyncio.Lock()
        
    async def wait_for_token(self, require: int = 1):
        while True:
            try:
                async with self.lock:
                    now = datetime.datetime.now()
                    elapsed = now - self.allocated_time
                    allocate_new = int(elapsed.total_seconds() * self.rate)
                    if  allocate_new >= 1:
                        self.tokens = min(self.capacity, self.tokens + allocate_new)
                        self.allocated_time += datetime.timedelta(seconds=allocate_new/self.rate)
                        
                    if self.tokens >= require:
                        self.tokens -= require
                        return

                await asyncio.sleep(max(0.1, 1.0/self.rate))
            except Exception as e:
                traceback.print_exc()


def to_key(input):
    filtered = "".join([x for x in input.lower() if x.isalnum()])
    return hashlib.sha256(filtered.encode()).hexdigest()[:8]
    
class InFlightDeduper:
    def __init__(self):
        self.call_map = {}
        self.lock = asyncio.Lock()
        pass

    async def remove_key(self, key):
        async with self.lock:
            if key in self.call_map:
                self.call_map.pop(key)
    async def call_and_wait(self, fn, params):
        key = to_key(params[0])
        async with self.lock:
            if key not in self.call_map:
                self.call_map[key] = asyncio.create_task(fn(*params))
                self.call_map[key].add_done_callback(lambda fut: asyncio.create_task(self.remove_key(key)))
        try:
            return await self.call_map[key]
        except Exception as e:
            traceback.print_exc()
            raise

async def asr_worker(audio: bytes):
    await asyncio.sleep(0.1)
    return "prompt template. " +  hashlib.sha256(audio).hexdigest()[:2]


class LLM:
    def __init__(self, ttl=10):
        self.cache = {}
        self.ttl = ttl
    
    def house_keeping(self):
        now = datetime.datetime.now()
        to_remove = [k for k, v in self.cache.items() if now - v[1] > datetime.timedelta(seconds=self.ttl)]
        for key in to_remove:
            self.cache.pop(key)

    def put_to_cache(self, key, val):
        now = datetime.datetime.now()
        self.cache[key] = (val, now)
        self.house_keeping()
    
    def fetch_from_cache(self, key):
        if key in self.cache:
            return self.cache[key][0]
        else:
            return None

    async def call(sefl, prompt: str):
        await asyncio.sleep(0.2)
        if random.randint(1, 10) % 5 == 0:
            raise asyncio.TimeoutError("llm does not respond")
        print("llm responds")
        return f"llm response {hash(prompt)}"

    async def call_with_retry(self, prompt: str, token: TokenBucket, retries: int = 5):
        key = to_key(prompt)
        if cached := self.fetch_from_cache(key):
            return cached
        print("llm cache miss, call llm")
        
        base = 1
        for attempt in range(retries + 1):
            try:
                await token.wait_for_token()
                resp = await self.call(prompt)
                self.put_to_cache(key, resp)
                return resp
            except asyncio.TimeoutError as e:
                print(f"llm processing error: {e}")
                await asyncio.sleep(min(base, 30) * (0.8 + 0.2 * random.random()))
                base = base * 2
                if attempt == retries:
                    raise
                
        raise asyncio.TimeoutError(f"llm failed to process after max retries")

async def tts_worker(text: str):
    await asyncio.sleep(0.1)
    return hashlib.sha256(text.encode()).digest()

async def asr_llm_pipeline(
                    llm: LLM,
                    asr_queue: asyncio.Queue,
                    llm_response_queue: asyncio.Queue,
                    error_queue: asyncio.Queue,
                    token: TokenBucket,
                    dedpuer: InFlightDeduper):
    task_name = asyncio.current_task().get_name()
    while True:
        try:
            aid, audio = await asyncio.wait_for(asr_queue.get(), 1)
            asr_queue.task_done()
            if not aid and not audio:
                print(f"{task_name} complete")
                return
        except asyncio.TimeoutError as e:
            print("no asr request")
            continue

        try:
            prompt = await asr_worker(audio)
        except Exception as e:
            print(f"asr_worker processing error: {e} for {aid}")
            await error_queue.put((aid, str(e)))
            print("send to error queue")
            continue
        
        try:
            resp = await dedpuer.call_and_wait(llm.call_with_retry, [prompt, token])
            await llm_response_queue.put((aid, resp))
        except Exception as e:
            print(f"llm processing error {e}")
            await error_queue.put((aid, str(e)))
            print("send to error queue")
            continue

async def tts_pipeline(llm_response_queue: asyncio.Queue, audio_response_queue: asyncio.Queue, error_queue: asyncio.Queue):
    task_name = asyncio.current_task().get_name()

    while True:
        try:
            aid, llm_response = await asyncio.wait_for(llm_response_queue.get(), 1)
            llm_response_queue.task_done()
            if not aid and not llm_response:
                print(f"{task_name} complete")
                return
        except asyncio.TimeoutError as e:
            print("no llm response")
            continue
        
        try:
            await audio_response_queue.put((aid, await tts_worker(llm_response)))
        except Exception as e:
            print(f"tts_worker processing error: {e} for audio {aid}")
            await error_queue.put((aid, str(e)))
            print("send to error queue")
            continue

async def audio_generator(asr_queue, total):
    task_name = asyncio.current_task().get_name()
    try:
        for i in range(total):
            print(f"Generate asr request {task_name}-{i}")
            await asr_queue.put((f"{task_name}-{i}", f'this is the message {i}'.encode()))
    except Exception as e:
        print(f"failed to generate audio {e}")

async def main():
    '''
    Asynchronous pipeline (ASR → LLM → TTS)
    TokenBucket rate limiter (rate limit)
    In-flight deduplication (same prompt calls LLM only once)
    Caching (Cache + TTL) (with expiration time)
    Prompt normalization (Normalization + Hash key)
    LLM call retry (Exponential backoff retry)
    Support for batch task processing (Batch pipeline)
    Robust exception handling
    Print final output (including cache hit and retry information)
    '''
    token = TokenBucket(10, 10)
    duper = InFlightDeduper()
    asr_queue = asyncio.Queue()
    llm_response_queue = asyncio.Queue()
    audio_response_queue = asyncio.Queue()
    error_queue = asyncio.Queue()
    asr_llm_task_num = 10
    tts_task_num = 5
    asr_llm_pipeline_tasks = []
    llm = LLM()
    for i in range(asr_llm_task_num):
        asr_llm_pipeline_tasks.append(asyncio.create_task(asr_llm_pipeline(llm, asr_queue, llm_response_queue, error_queue, token, duper), name=f"llm-{i}"))

    tts_pipeline_tasks = []
    for i in range(tts_task_num):
        tts_pipeline_tasks.append(asyncio.create_task(tts_pipeline(llm_response_queue, audio_response_queue, error_queue), name=f"tts-{i}"))

    audio_gen_tasks = []
    for i in range(5):
        audio_gen_tasks.append(asyncio.create_task(audio_generator(asr_queue, 10), name=f"audio-{i}"))

    await asyncio.gather(*audio_gen_tasks)

  
    # Notify asr_llm_pipeline_tasks to complete
    for i in range(asr_llm_task_num):
        await asr_queue.put((None, None))
    await asr_queue.join()
    await asyncio.gather(*asr_llm_pipeline_tasks)

    # Notify tts_pipeline_tasks to complete
    for i in range(tts_task_num):
        await llm_response_queue.put((None, None))
    await llm_response_queue.join()
    await asyncio.gather(*tts_pipeline_tasks)
    
    while not audio_response_queue.empty():
        aid, audio_response = await audio_response_queue.get()
        audio_response_queue.task_done()
        print(f"{aid} response: {audio_response}")

    while not error_queue.empty():
        aid, error = await error_queue.get()
        error_queue.task_done()
        print(f"{aid} error: {error}")
        
asyncio.run(main())
    
