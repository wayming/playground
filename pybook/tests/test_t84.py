import pybook.t84 as t


def test_t84_short_url():
    print(t.short_url("http://www.sohu.com", 8))
    print(t.short_url("http://www.sohu.com", 1))
    print(t.short_url("http://www.sohu.com", 16))
    print(t.short_url("http://www.sohu.com", 160))
    assert len(t.short_url("http://www.sohu.com", 8)) == 8
