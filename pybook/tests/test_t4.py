import pybook.t4 as t


def test_valid_expression():
    assert t.validate_exp("{abc}") is True
    assert t.validate_exp("{abc)") is False
    assert t.validate_exp("{(abc)}") is True
    assert t.validate_exp("{(abc}") is False
    assert t.validate_exp("{abc") is False
    assert t.validate_exp("{(abc)([efg])}") is True
