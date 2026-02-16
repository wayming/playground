import collections
import functools
import types


class LRU:
    def __init__(self, cap):
        self.cache = collections.OrderedDict()
        self.capacity = cap
        self.cache_stats = types.SimpleNamespace(hits=0, misses=0)

        pass

    def __call__(self, func):

        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            key = (args, tuple(kwargs.items()))
            if key in self.cache:
                self.cache.move_to_end(key)
                self.cache_stats.hits += 1
                return self.cache[key]

            while len(self.cache) >= self.capacity:
                self.cache.popitem(last=False)

            self.cache_stats.misses += 1
            self.cache[key] = func(*args, **kwargs)
            return self.cache[key]

        func_wrapper.cache_stats = self.cache_stats
        return func_wrapper
