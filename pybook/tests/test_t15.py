import pybook.t15 as t


def test_preorder():
    nodes = [x for x in range(1, 10)]
    assert t.preorder(nodes) == [1, 2, 4, 8, 9, 5, 3, 6, 7]


def test_inorder():
    nodes = [x for x in range(1, 10)]
    assert t.inorder(nodes) == [8, 4, 9, 2, 5, 1, 6, 3, 7]
