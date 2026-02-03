from collections import OrderedDict
from typing import Any


class LRUCache:
    def __init__(self, cap):
        self.cache = OrderedDict()
        self.capacity = cap

    def get(self, key) -> Any:
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        else:
            return None

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            while len(self.cache) >= self.capacity:
                self.cache.popitem(False)

        self.cache[key] = value
