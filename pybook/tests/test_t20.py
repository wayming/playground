import pybook.t20 as t


def test_iterator():
    assert [x for x in t.Countdown(10)] == [x for x in reversed(range(11))]
