from functools import wraps
import random
from collections import OrderedDict
class LRU:
    def __init__(self, capacity = 10):
        self.cap = capacity
        self.cache = OrderedDict()
        pass
    
    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        else:
            raise KeyError("Key not found")
    
    def put(self, key, val):
        self.cache[key] = val
        self.cache.move_to_end(key)
        if len(self.cache) > self.cap:
            self.cache.popitem(last=False)

    def print(self):
        for k, v in self.cache.items():
            print(f"{k}=>{v}")
    def has(self, key):
        return key in self.cache

def LRUDecorator(func):
    lru = LRU(3)
    count = 0
    @wraps(func)
    def wrapper(*args, **kwargs):
        if count % 10 == 0:
            print("-------------------------")
            lru.print()
        key = (args, tuple(sorted(kwargs.items())))
        
        if lru.has(key):
            return lru.get(key)
        
        result = func(*args, **kwargs)
        
        lru.put(key, result)
        return result
    
    return wrapper


@LRUDecorator
def func1(s):
    return s + " - " + str(random.randint(100, 200))

for i in range(100):
    func1(str(i))
