import pybook.t27 as t


def test_set():
    assert t.a_only({1, 2, 3, 4, 5}, {4, 5, 6, 7, 8}) == {1, 2, 3}
    assert t.distinct({1, 2, 3, 4, 5}, {4, 5, 6, 7, 8}) == {1, 2, 3, 6, 7, 8}
    assert t.common({1, 2, 3, 4, 5}, {4, 5, 6, 7, 8}) == {4, 5}
