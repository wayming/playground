import pybook.t96 as t


def test_t96_reverse():
    t1 = t.t96_Node(1, None)
    t2 = t.t96_Node(2, t1)
    t3 = t.t96_Node(3, t2)
    t4 = t.t96_Node(4, t3)
    t5 = t.t96_Node(5, t4)

    assert t5.values() == [5, 4, 3, 2, 1]
    root = t5.reverse()
    assert root.values() == [1, 2, 3, 4, 5]
