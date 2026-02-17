import collections
import functools
import threading
import types


class LRU:
    def __init__(self, cap):
        self.cache = collections.OrderedDict()
        self.lock = threading.Lock()
        self.capacity = cap
        self.cache_stats = types.SimpleNamespace(hits=0, misses=0)

        pass

    def __call__(self, func):

        @functools.wraps(func)
        def func_wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            with self.lock:
                if key in self.cache:
                    self.cache.move_to_end(key)
                    self.cache_stats.hits += 1
                    return self.cache[key]

            result = func(*args, **kwargs)

            with self.lock:
                if key not in self.cache:
                    while len(self.cache) >= self.capacity:
                        self.cache.popitem(last=False)

                    self.cache_stats.misses += 1
                    self.cache[key] = result
            return result

        func_wrapper.cache_stats = self.cache_stats
        return func_wrapper
