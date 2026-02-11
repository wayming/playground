import pybook.t38 as t


def test_parentheses_match():
    assert t.parentheses_match("{}[(())]")
    assert t.parentheses_match("{xx}[ww((mm))oo]")
    assert not t.parentheses_match("{}[(()]")
