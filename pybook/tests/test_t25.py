import pybook.t25 as t


def test_order_by():
    text = "a a b c a b d e"
    print(t.top_words(text, 5))
    assert t.top_words(text, 5)[0] == "a"
