from collections import OrderedDict
class LRUCache:
    def __init__(self, max_size):
        self.data = OrderedDict()
        self.max_size = max_size
    
    def get(self, key):
        if key not in self.data:
            return -1
        
        self.data.move_to_end(key)
        return self.data[key]
    
    def put(self, key, val):
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = val
        if len(self.data) > self.max_size:
            self.data.popitem(last = False)

if __name__ == "__main__":
    cache = LRUCache(max_size=2)
    cache.put(1, 1)
    cache.put(2, 2)
    print(cache.get(1))       # 返回 1
    cache.put(3, 3)    # 淘汰 key=2
    print(cache.get(2))       # 返回 -1
    cache.put(4, 4)    # 淘汰 key=1
    print(cache.get(1))       # 返回 -1
    print(cache.get(3))       # 返回 3
    print(cache.get(4))       # 返回 4