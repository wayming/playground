import copy


def test_copy():
    orig = [[1, 2], [3, 4]]
    assign = orig
    assert id(assign) == id(orig)

    shallow = copy.copy(orig)
    deep = copy.deepcopy(orig)
    orig.append([5, 6])
    assert id(shallow) != id(orig)
    assert shallow == [[1, 2], [3, 4]]
    assert deep == [[1, 2], [3, 4]]

    orig[0][0] = "X"
    assert shallow == [["X", 2], [3, 4]]
    assert deep == [[1, 2], [3, 4]]
