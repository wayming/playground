#include <deque>
#include <queue>
#include <iostream>
#include <unordered_map>
#include <algorithm>
#include <list>

class LRU1
{
public:
    LRU1(size_t cap) : _cap(cap) {}
    ~LRU1() {
        while(!_keys.empty()) {
            _keys.pop();
        }
    }
    void put(std::string v) {
        while (_keys.size() >= _cap ) {
            std::cout << "pop " << _keys.front() << std::endl;
            _keys.pop();
        }
        _keys.push(v);
    }
    std::string pop() {
        auto v = _keys.front();
        std::cout << "pop " << v << std::endl;
        _keys.pop();
        return v;
    }

private:
    std::queue<std::string> _keys;
    size_t _cap;
};

template<class K, class V>
class LRU2
{
public:
    LRU2(size_t cap) : _cap(cap) {}
    ~LRU2() {

    }
    void put(const K& key, const V& v) {
        if (_cap == 0) { throw std::runtime_error("cap 0"); }
        auto iter = _index.find(key);
        if (iter != _index.end()) {
            _data.erase(iter->second);
            _index.erase(key);
        }
        while (_data.size() >= _cap) {
            auto elem = _data.front();
            _data.pop_front();
            _index.erase(elem.first);
            std::cout << "pop " << "[" << elem.first << "]" << "[" << elem.second << "]" << std::endl;
        }

        _data.push_back(std::pair<K,V>(key, v));
        _index[key] = std::prev(_data.end());
    }
    V pop(const K& key) {
        if (_data.size() == 0) {throw std::runtime_error("no element"); }

        auto iter = _index.find(key);
        if (iter != _index.end()) {
            auto val = iter->second->second;
            std::cout << "pop " << "[" << key << "]" << "[" << val << "]" << std::endl;

            _data.erase(iter->second);
            _index.erase(key);
            return val;
        } else {
            throw std::runtime_error("no key");
        }
    }
    V get(const K& key) {
        auto iter = _index.find(key);
        if (iter != _index.end()) {
            _data.splice(_data.end(), _data, iter->second);
            return iter->second->second;
        } else {
            throw std::runtime_error("no key");
        }
    }
private:
    using LRUElement = std::list<std::pair<K, V>>;
    LRUElement _data;
    std::unordered_map<K, typename LRUElement::iterator> _index;
    size_t _cap;
};

int main()
{
    LRU2<int, std::string> cache(5);
    cache.put(1, "aaa");
    cache.put(2, "bbb");
    cache.put(3, "ccc");
    cache.put(4, "ddd");
    cache.put(5, "eee");
    cache.put(6, "fff");
    cache.put(3, "ggg");
    cache.put(3, "hhh");
    cache.get(2);
    cache.put(7, "iii");
    cache.pop(3);
    return 0;
}