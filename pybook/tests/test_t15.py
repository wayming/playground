import pybook.t15 as t


def test_inorder():
    nodes = [x for x in range(1, 10)]
    assert t.inorder(nodes) == [1, 2, 4, 8, 9, 5, 3, 6, 7]
