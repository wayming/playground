import pybook.t39 as t


def test_min_stack():
    s = t.MinStack()
    s.push(5)
    s.push(3)
    s.push(7)
    s.push(2)
    s.push(8)

    assert s.min() == 2
    assert s.pop() == 8
    assert s.min() == 2
    assert s.pop() == 2
    assert s.min() == 3
    assert s.pop() == 7
    assert s.min() == 3
    assert s.pop() == 3
    assert s.min() == 5
    assert s.pop() == 5
    assert not s.min()
