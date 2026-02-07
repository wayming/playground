import pybook.t13 as t


def test_count():
    m = [
        [1, 1, 0, 0, 0],
        [1, 1, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 1, 1],
    ]
    assert t.count(m) == 3
