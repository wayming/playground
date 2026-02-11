import pybook.t40 as t


def test_first_distinct():
    assert t.first_distinct("leetcode") == "l"
    assert t.first_distinct("leetlcode") == "t"
