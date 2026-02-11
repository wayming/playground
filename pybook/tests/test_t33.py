import pybook.t33 as t


def test_count_words():
    assert t.count_words("a a b c\nb a") == 6
