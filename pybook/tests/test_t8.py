import sys
import time

import pybook.t8 as t

sys.setswitchinterval(0.000001)


def test_counter_mt():
    begin = time.perf_counter()
    print(t.counter_mt(20, 100000000))
    end = time.perf_counter()
    print(f"total elapsed {end - begin} seconds")
