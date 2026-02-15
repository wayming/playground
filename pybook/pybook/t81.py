import concurrent
import concurrent.futures
import multiprocessing
import multiprocessing.synchronize
import queue
import threading
import time


def t81_squre(x):
    return x * x


def t81_square_sum_mp(np: int, r: int):
    with concurrent.futures.ProcessPoolExecutor(np) as exectuor:
        return sum(exectuor.map(t81_squre, range(r)))


def t81_square_sum_mt(np: int, r: int):
    with concurrent.futures.ThreadPoolExecutor(np) as exectuor:
        return sum(exectuor.map(t81_squre, range(r)))


def t81_mt_worker(q: queue.Queue, stop: threading.Event):
    sum = 0
    while True:
        try:
            v = q.get_nowait()
            q.task_done()
            sum += v
        except queue.Empty:
            if stop.is_set():
                break
            time.sleep(0.01)
        except Exception as e:
            print("Exception ", e)
            break
    return sum


def t81_square_sum_mtq(np: int, r: int):
    futures: list[concurrent.futures.Future] = []
    q = queue.Queue()
    stop = threading.Event()
    with concurrent.futures.ThreadPoolExecutor(np) as exectuor:
        futures = [exectuor.submit(t81_mt_worker, q, stop) for x in range(np)]

        for i in range(r):
            q.put(i)

        # Wait until work done
        q.join()
        stop.set()

        sum = 0
        for f in concurrent.futures.as_completed(futures):
            try:
                sum += f.result()
            except Exception as e:
                print("Woker error: ", e)
        return sum


class t81_mp_worker:
    queue: multiprocessing.Queue = None
    stop: multiprocessing.synchronize.Event | None = None

    @staticmethod
    def init_sync(q: multiprocessing.Queue, e: multiprocessing.synchronize.Event):
        t81_mp_worker.queue = q
        t81_mp_worker.stop = e

    @staticmethod
    def worker():
        sum = 0
        while True:
            try:
                v = t81_mp_worker.queue.get_nowait()
                sum += v
            except queue.Empty:
                if t81_mp_worker.stop.is_set():
                    break
                time.sleep(0.01)
            except Exception as e:
                print("Exception ", e)
                break
        return sum


def t81_square_sum_mpq(np: int, r: int):
    futures: list[concurrent.futures.Future] = []
    q = multiprocessing.Queue()
    stop = multiprocessing.Event()

    # All tasks are in queue
    for i in range(r):
        q.put(i)

    # Return when all consumers are done
    with concurrent.futures.ProcessPoolExecutor(
        np, initializer=t81_mp_worker.init_sync, initargs=(q, stop)
    ) as exectuor:
        futures = [exectuor.submit(t81_mp_worker.worker) for x in range(np)]

        # Consumer returns when queue is empty and stop is set
        stop.set()

        sum = 0
        for f in concurrent.futures.as_completed(futures):
            try:
                sum += f.result()
            except Exception as e:
                print("Woker error: ", e)
        return sum
