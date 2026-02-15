import time

import pybook.t81 as t


def test_t81_square_sum():
    begin = time.perf_counter()
    print(t.t81_square_sum_mp(10, 1000000))
    end = time.perf_counter()
    print("MP elapsed ", end - begin, " seconds")

    begin = time.perf_counter()
    print(t.t81_square_sum_mt(10, 1000000))
    end = time.perf_counter()
    print("MT elapsed ", end - begin, " seconds")

    begin = time.perf_counter()
    print(t.t81_square_sum_mtq(10, 1000000))
    end = time.perf_counter()
    print("MTQ elapsed ", end - begin, " seconds")

    begin = time.perf_counter()
    print(t.t81_square_sum_mpq(10, 1000000))
    end = time.perf_counter()
    print("MTQ elapsed ", end - begin, " seconds")
