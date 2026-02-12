import pybook.t50 as t


def test_t71_top_k():
    assert t.t71_top_k([4, 1, 1, 1, 2, 2, 3, 1, 4], 3) == [1, 4, 2]


def test_t72_factorial():
    assert t.t72_factorial(5) == 120


def test_t73_islands():
    g = [[1, 1, 0, 0], [1, 0, 0, 1], [0, 0, 1, 1], [1, 0, 0, 0]]
    assert t.t73_islands(g) == 3


def test_t74_shortest_path():
    g = [[1, 1, 0, 0], [1, 0, 0, 1], [0, 0, 1, 1], [1, 0, 0, 0]]
    assert t.t74_shortest_path(g) == -1
    g = [[0, 1, 0, 0], [1, 0, 0, 1], [0, 0, 1, 1], [1, 0, 0, 0]]
    assert t.t74_shortest_path(g) == -1
    g = [[0, 1, 0, 0], [0, 0, 1, 1], [0, 1, 0, 0], [0, 0, 0, 0]]
    assert t.t74_shortest_path(g) == 7


def test_t74_shortest_path2():
    g = [[1, 1, 0, 0], [1, 0, 0, 1], [0, 0, 1, 1], [1, 0, 0, 0]]
    assert t.t74_shortest_path2(g) == -1
    g = [[0, 1, 0, 0], [1, 0, 0, 1], [0, 0, 1, 1], [1, 0, 0, 0]]
    assert t.t74_shortest_path2(g) == -1
    g = [[0, 1, 0, 0], [0, 0, 1, 1], [0, 1, 0, 0], [0, 0, 0, 0]]
    assert t.t74_shortest_path2(g) == 7
    g = [[0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1], [1, 0, 0, 0]]
    assert t.t74_shortest_path2(g) == 7


def test_t76_max_profit():
    assert t.t76_max_profit([7, 1, 5, 8, 3, 2, 6, 4]) == [
        (7, 1),
        (1, 8),
        (8, 2),
        (2, 6),
        (6, 4),
    ]


def test_t77_bubble_sort():
    nums = [7, 1, 5, 8, 3, 2, 6, 4]
    t.t77_bubble_sort(nums)
    assert nums == [1, 2, 3, 4, 5, 6, 7, 8]


def test_t78_producers_consumers():
    processer = t.T78(5, 10, 1000)
    processer.fire()
