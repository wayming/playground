import pybook.t19 as t


def test_find_duplicate():
    assert t.find_duplicte([5, 8, 7, 6, 8, 2, 4, 3, 9, 1]) == 8
