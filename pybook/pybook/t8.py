import threading


def counter_mt(nthreads, niterations) -> int:
    data = {"count": 0}
    lock = threading.Lock()

    def compute(n):
        for _ in range(n):
            with lock:
                data["count"] += 1

    threads = []
    for _ in range(nthreads):
        threads.append(threading.Thread(target=compute, args=[niterations]))

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    return data["count"]
