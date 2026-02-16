import pybook.t85 as t


def test_t85_decorator():
    @t.LRU(cap=5)
    def calc(n):
        return n * n

    # Cache None
    for x in [1, 3, 5, 3, 1]:
        print(calc(x))
    assert calc.cache_stats.hits == 2
    assert calc.cache_stats.misses == 3

    # Cache 5, 3, 1
    for x in [7, 9, 11, 5]:
        print(calc(x))
    assert calc.cache_stats.hits == 2
    assert calc.cache_stats.misses == 7

    # Cache 1, 7, 9, 11, 5
    for x in [1, 7, 9, 11, 5]:
        print(calc(x))
    assert calc.cache_stats.hits == 7
    assert calc.cache_stats.misses == 7
