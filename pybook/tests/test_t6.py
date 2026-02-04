import pybook.t6 as t


def test_flat_dict():
    nested = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
    print(t.flat_dict(nested))
