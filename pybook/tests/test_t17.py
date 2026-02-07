import time

import pybook.t17 as t


def test_process():
    nums = range(10**8)
    begin = time.perf_counter()
    t.process(nums)
    end = time.perf_counter()
    print(f"elapsed {(end - begin):.2f}seconds")


def test_process_mt():
    nums = range(10**6)
    begin = time.perf_counter()
    t.processMt(nums)
    end = time.perf_counter()
    print(f"elapsed {(end - begin):.2f}seconds")
