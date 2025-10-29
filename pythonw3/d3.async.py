import asyncio
import datetime
import random
import os

async def producer(iterations: int, q: asyncio.Queue, sem: asyncio.Semaphore):
    async with sem:
        text = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S:%f")
        for _ in range(iterations):
            try:
                n = random.randint(0, 1000)
                print(f"producer: put {n}")
                await q.put((text, n))
            except Exception as e:
                print(f"producer: Failed to put into queue. {e}")


async def consumer(q: asyncio.Queue, stop: asyncio.Event, results: list, sem: asyncio.Semaphore):
    nums = []
    async with sem:
        while not stop.is_set() or not q.empty():
            try:
                text, num = await asyncio.wait_for(q.get(), 0.01)
                print("consumer:", text)
                nums.append(num)
                q.task_done()
                await asyncio.sleep(0.01)
            except asyncio.TimeoutError as e:
                continue
            except Exception as e:
                print(e)
        
        if nums:
            results.append(sum(nums)/len(nums))
        else:
            print("consumer: no data received")

async def main1():
    num_producers = 10
    num_consumers = 5
    data_queue = asyncio.Queue()
    stop = asyncio.Event()
    consumer_results = []
    sem = asyncio.Semaphore(5)
    
    begin = datetime.datetime.now()
    producers = [
        asyncio.create_task(producer(100, data_queue, sem))
            for _ in range(num_producers)
    ]
    
    consumers = [
        asyncio.create_task(consumer(data_queue, stop, consumer_results, sem))
            for _ in range(num_consumers)
    ]
    
    results = await asyncio.gather(*producers, return_exceptions=True)
    for r in results:
        if isinstance(r, Exception):
            print("producer exception ", r)
    stop.set()
    try:
        await asyncio.gather(*consumers)
    except Exception as e:
        print(e)
    
    for r in consumer_results:
        print(r)
    
    elapsed = datetime.datetime.now() - begin
    print("elapsed time ", elapsed.total_seconds(), " seconds, ")
# async def main():
#     num_producers = 10
#     num_consumers = 5
#     data_queue = asyncio.Queue()
#     stop = asyncio.Event
    

#     async with asyncio.taskgroups.TaskGroup() as group:
#         producers = [
#             group.create_task(asyncio.to_thread(producer(1000, data_queue)))
#                 for _ in range(num_producers)]
#         consumers = [
#             group.create_task(asyncio.to_thread(consumer(data_queue, stop)))
#                 for _ in range(num_consumers)]
#         asyncio.gather(*producers)
#         stop.set()
#         asyncio.gather(*consumers)

asyncio.run(main1())
        