import sys
import time

import pybook.t8 as t

sys.setswitchinterval(0.000001)


def test_counter_parallel():
    begin = time.perf_counter()
    print(t.counter_mt(20, 100000))
    end = time.perf_counter()
    print(f"mt total elapsed {end - begin} seconds")

    begin = time.perf_counter()
    print(t.counter_mp(20, 100000))
    end = time.perf_counter()
    print(f"mp total elapsed {end - begin} seconds")

    begin = time.perf_counter()
    print(t.counter_async(20, 100000))
    end = time.perf_counter()
    print(f"async total elapsed {end - begin} seconds")
