#include <deque>
#include <list>
#include <unordered_map>
#include <tuple>
template <typename K, typename V>
class LRUCache {
    std::list<K> keysList;
    std::unordered_map<K, V> values;
    std::unordered_map<K, typename std::list<K>::iterator> iters;
    size_t capacity;
public:
    LRUCache(size_t n) : capacity(n) {}
    void put(const K& k, const V& v) {
        // auto& [k, v] = kv;
        auto iter = iters.find(k);
        if (iter ==iters.end()) {
            // new key
            while(keysList.size() >= capacity) {
                iters.erase(keysList.front());
                values.erase(keysList.front());
                keysList.pop_front();
            }
            keysList.emplace_back(k);
            values.emplace(k, v);
            iters.emplace(k, std::prev(keysList.end()));
        } else {
            // existing key
            keysList.splice(keysList.end(), keysList, iter->second);
            values[k] = v;
        }
    }

    V get(const K& k) {
        auto iter = iters.find(k);
        if(iter == iters.end()) {
            throw std::range_error("invalid key");
        }
        
        keysList.splice(keysList.end(), keysList, iter->second);
        return values.at(k);
    }

    void print() {
        std::cout << "order(new-old)" << std::endl;
        for(auto rit = keysList.crbegin(); rit != keysList.crend(); ++rit) {
            std::cout << "[" << *rit << "] => [" << values.at(*rit) << "]" << std::endl; 
        }
    }
};