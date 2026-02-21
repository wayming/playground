import threading

import pybook.t100 as t


def counter_thread_func(e: threading.Event, c: t.t100_Counter_MT, v: int):

    e.wait()
    c.increase(v)
    c.print_local()


def test_t100_Counter_MT():
    counter = t.t100_Counter_MT()
    threads: list[threading.Thread] = []
    start = threading.Event()
    for i in range(100):
        threads.append(
            threading.Thread(target=counter_thread_func, args=(start, counter, i))
        )

    for th in threads:
        th.start()

    start.set()

    for th in threads:
        th.join()

    counter.print()
