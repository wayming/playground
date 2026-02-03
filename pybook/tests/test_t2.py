import pybook.t2 as t


def test_lru():
    cache = t.LRUCache(2)
    cache.put("first", "aaa")
    cache.put("second", "bbb")
    cache.put("third", "ccc")
    cache.put("second", "ddd")
    cache.put("forth", "eee")
    assert cache.get("first") is None
    assert cache.get("third") is None
    assert cache.get("second") == "ddd"
    assert cache.get("forth") == "eee"
