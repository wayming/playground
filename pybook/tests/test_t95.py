import pybook.t93 as t


def test_t93_ways():
    assert t.t93_ways(5) == 8


def test_t93_steps():
    assert len(t.t93_steps(5)) == 8
