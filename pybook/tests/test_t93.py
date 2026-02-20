import pybook.t95 as t


def test_t95_myiter():
    iter = t.MyIter(10)
    assert len([x for x in iter]) == 10
