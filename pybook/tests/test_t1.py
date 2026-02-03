import pybook.t1 as t1


def test_two_sum():
    assert sorted(t1.two_sum([1, 3, 4, 6, 7], 9)) == [1, 3]
