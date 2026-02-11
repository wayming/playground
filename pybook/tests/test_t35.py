import pybook.t35 as t


def test_revert():
    assert t.revert("abc") == "cba"
