#include <list>
#include <unordered_map>

template <typename K, typename V>
class LRUCache {
public:
    LRUCache(size_t capacity) : cap(capacity) {}

    void put(const K& k, const V& v) {
        auto it = lookup.find(k);
        if (it != lookup.end()) {
            cache.splice(cache.begin(), cache, it->second);
            // lookup[k] = std::prev(cache.end()); // iterator of the element is not changed
            return;
        }

        cache.emplace_front(k, v);
        lookup[k] = cache.begin();
        if (cache.size() > cap) {
            lookup.erase(cache.back().first);
            cache.pop_back();
        }
    }

    V& get(const K& k) {
        auto it = lookup.find(k);
        if (it != lookup.end()) {
            cache.splice(cache.begin(), cache, it->second);
            return cache.front().second;
        } else {
            throw std::runtime_error("no value found");
        }
    }

    void print() {
        for (auto& e : cache) {
            std::cout << "(" << e.first << "," << e.second << ") ";
        }
        std::cout << std::endl;
    }
private:
    std::list<std::pair<K, V>> cache;
    std::unordered_map<K, typename std::list<std::pair<K,V>>::iterator> lookup;
    size_t cap = 0;
};