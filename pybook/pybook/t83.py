import asyncio
import datetime
import random
import traceback


async def producer(q: asyncio.Queue, run: asyncio.Event, rates: int):
    await run.wait()

    totalMessages = 0
    beginAt = datetime.datetime.now()
    print("producer begin at", beginAt)
    while run.is_set():
        try:
            q.put_nowait(random.randint(1, 100))
            totalMessages += 1
            advanced = (
                beginAt
                + datetime.timedelta(seconds=totalMessages / rates)
                - datetime.datetime.now()
            )
            if advanced.total_seconds() > 0:
                await asyncio.sleep(advanced.total_seconds())
        except Exception as e:
            traceback.print_exception(e)
    print("producer complete with ", totalMessages, "total messages")
    return totalMessages


async def consumer(
    input: asyncio.Queue,
    output: asyncio.Queue,
    run: asyncio.Event,
):
    await run.wait()

    total_sum = 0
    count = 0
    while True:
        if not run.is_set() and input.empty():
            break

        try:
            v = await asyncio.wait_for(input.get(), timeout=0.1)
            input.task_done()
            total_sum += v
            count += 1
        except TimeoutError:
            # traceback.print_exception(e)
            continue
        except Exception as e:
            traceback.print_exception(e)
            raise e
    await output.put((count, total_sum))
    return f"consumer complete with total message {count}"


async def runner(
    producer_rates: int, producer_elapsed: int, nproducers: int, nconsumers: int
):
    producers = []
    consumers = []
    in_queue = asyncio.Queue()
    out_queue = asyncio.Queue()
    run = asyncio.Event()
    async with asyncio.TaskGroup() as tg:
        producers = [
            tg.create_task(producer(in_queue, run, producer_rates))
            for _ in range(nproducers)
        ]
        consumers = [
            tg.create_task(consumer(in_queue, out_queue, run))
            for _ in range(nconsumers)
        ]

        run.set()

        print("Fire at", datetime.datetime.now())

        await asyncio.sleep(producer_elapsed)

        # Complete producing
        run.clear()

    # await in_queue.join()

    total_produced = 0
    for p in producers:
        if p.exception():
            print(p.exception())
        else:
            total_produced += p.result()

    for c in consumers:
        if c.exception():
            print(c.exception())
        else:
            print(c.result())

    consumed_count = 0
    consumed_sum = 0
    while not out_queue.empty():
        count, sum = await out_queue.get()
        consumed_count += count
        consumed_sum += sum

    assert total_produced == consumed_count
    print(
        "produced",
        total_produced,
        "consumed",
        consumed_count,
        "average value",
        consumed_sum / consumed_count,
    )
