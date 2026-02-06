import asyncio
import multiprocessing
import threading


def counter_mt(nParallel, nIterations) -> int:
    data = {"count": 0}
    lock = threading.Lock()

    def compute(n):
        for _ in range(n):
            with lock:
                data["count"] += 1

    threads = []
    for _ in range(nParallel):
        threads.append(threading.Thread(target=compute, args=[nIterations]))

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    return data["count"]


def counter_mp(nParallel, nIterations) -> int:
    data = multiprocessing.Value("i", 0, lock=True)

    def compute(v: multiprocessing.Value, n: int):
        for _ in range(n):
            with v.get_lock():
                v.value += 1

    processes = []
    for _ in range(nParallel):
        processes.append(
            multiprocessing.Process(target=compute, args=[data, nIterations])
        )

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    return data.value


def counter_async(nParallel, nIteration) -> int:
    value = {"count": 0}

    async def acounter_async(p, i) -> int:
        async def acompute(n):
            for _ in range(n):
                value["count"] += 1
                if _ % 1000 == 0:
                    await asyncio.sleep(0)

        tasks = [acompute(i) for _ in range(p)]
        await asyncio.gather(*tasks)

    asyncio.run(acounter_async(nParallel, nIteration))
    return value["count"]
