import asyncio
import random
import signal
import datetime
from traceback import print_exc
async def producer(queue: asyncio.Queue, stop: asyncio.Event, rate_per_second: int):
    begin = datetime.datetime.now()
    count = 0
    batch_begin = datetime.datetime.now()
    batch_count = 0
    while not stop.is_set():
        try:
            await asyncio.wait_for(queue.put(random.randint(0, 1000)), 1)
            batch_count += 1
            if batch_count == rate_per_second:
                remain_time = datetime.timedelta(seconds=1) - (datetime.datetime.now() - batch_begin)
                if remain_time.seconds > 0 or remain_time.microseconds > 0:
                    await asyncio.sleep(remain_time.seconds + remain_time.microseconds/1000000)
                batch_count = 0
                batch_begin = datetime.datetime.now()

            count += 1
            if count == 100:
                delta = datetime.datetime.now() - begin
                if delta.seconds > 0:
                    print("producer rate ", count//delta.seconds, " message per second")
                    count = 0
                    begin = datetime.datetime.now()
        except asyncio.TimeoutError as e:
            print(f"queue put timeout, {e}")
        except Exception as e:
            print_exc()
            
async def consumer(queue: asyncio.Queue, stop: asyncio.Event, results: list):
    begin = datetime.datetime.now()
    count = 0
    while not stop.is_set():
        try:
            val = await asyncio.wait_for(queue.get(), 1)
            queue.task_done()
            results.append(val)
            await asyncio.sleep(0.01 * random.randint(1, 10))
            count += 1
            if count == 100:
                delta = datetime.datetime.now() - begin
                if delta.seconds > 0:
                    print("consumer rate ", 100//delta.seconds, " message per second")
                    count = 0
                    begin = datetime.datetime.now()
        except asyncio.TimeoutError as e:
            print(f"queue get timeout, {e}")
        except Exception as e:
            print(e)
    
    while not queue.empty():
        try:
            val = await asyncio.wait_for(queue.get(), 1)
            queue.task_done()
            results.append(val)
        except asyncio.TimeoutError as e:
            print(f"queue get timeout, {e}")
        except Exception as e:
            print(e)

async def main():
    results = []
    q = asyncio.Queue(100)
    stop = asyncio.Event()
    num_of_producers = 10
    num_of_consumers = 5
    rate_producers = 5
    def sig_handler():
        print("handling termination")
        stop.set()
    asyncio.get_running_loop().add_signal_handler(signal.SIGINT, sig_handler)


    # def sig_handler(signum, frame):
    #     print("handling termination")
    #     stop.set()
    # signal.signal(signal.SIGINT, sig_handler)
    async with asyncio.TaskGroup() as group:
        for _ in range(num_of_producers):
            group.create_task(producer(q, stop, 5)) 
        for _ in range(num_of_consumers):
            group.create_task(consumer(q, stop, results))
        while not stop.is_set():
            await asyncio.sleep(0.5)
            
    # producers = [asyncio.create_task(producer(q, stop)) for _ in range(num_of_producers)]
    # consumers = [asyncio.create_task(consumer(q, stop, results)) for _ in range(num_of_consumers)]
    # tasks = producers + consumers
    # await asyncio.gather(*tasks, return_exceptions=True)
    try:
        await asyncio.wait_for(q.join(), 1)
    except asyncio.TimeoutError:
        print("queue join timeout, force exit")

    for r in results:
        if isinstance(r, Exception):
            print("exception caught {r}")
        else:
            print(results)
    
asyncio.run(main())