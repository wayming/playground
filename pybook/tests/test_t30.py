import pybook.t30 as t


def test_sort_grades():
    assert t.sort_grades({"Alice": 90, "Bob": 85, "Tom": 90})[0] == ("Alice", 90)
