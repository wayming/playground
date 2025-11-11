import asyncio
import logging
import traceback
logging.basicConfig(
    level=logging.DEBUG
)
async def worker(data: list, lock: asyncio.Lock, fire: asyncio.Event):
    async with lock:
        await fire.wait()
        logging.info(f"worker {asyncio.current_task().get_name()}")        
        data.append(asyncio.current_task().get_name())

async def unlock(lock:asyncio.Lock):
    await asyncio.sleep(1)
    logging.info(f"unlocker {asyncio.current_task().get_name()}")        
    if lock.locked():
        lock.release()

async def begin(e: asyncio.Event):
    await asyncio.sleep(2)
    logging.info(f"begin {asyncio.current_task().get_name()}")        
    e.set()
    
async def main():
    lock = asyncio.Lock()
    await lock.acquire()
    data = []
    tasks = []
    fire = asyncio.Event()
    for i in range(10):
        tasks.append(asyncio.create_task(worker(data, lock, fire)))

    tasks.append(asyncio.create_task(unlock(lock)))
    tasks.append(asyncio.create_task(begin(fire)))
    await asyncio.gather(*tasks)

    logging.info(data)

asyncio.run(main())

for i in range(1, 3):
    logging.info(i)