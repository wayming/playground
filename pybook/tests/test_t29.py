import pybook.t29 as t


def test_sort_words():
    assert t.sort_words(["hello", "world", "is", "py"])[0] == "is"
