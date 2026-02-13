import time

import pybook.t80 as t


def test_t81_square_sum():
    begin = time.perf_counter()
    print(t.t81_square_sum_mp(20, 100000))
    end = time.perf_counter()
    print("elapsed ", end - begin, " seconds")
