import pybook.t34 as t


def test_remove_duplicate():
    assert t.remove_duplicate_from_ordered_list([1, 3, 4, 4, 7, 8, 8, 9]) == 6
