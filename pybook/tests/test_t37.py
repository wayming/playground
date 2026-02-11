import pybook.t37 as t


def test_two_sum():
    assert t.two_sum([2, 6, 7, 11, 3, 15], 9) == [(2, 0), (4, 1)]
