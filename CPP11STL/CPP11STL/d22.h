#include <future>
#include <deque>
#include <utility>
#include <unordered_map>
#include <mutex>
#include <tuple>
#include <chrono>
#include <algorithm>

class LRUSafe {
public:
    using DATA_ENTRY = std::tuple<std::string, std::string, std::chrono::time_point<std::chrono::system_clock>>;
    using DEQ = std::deque<DATA_ENTRY>;
    LRUSafe(size_t n, int ttl) :cap(n),ttl(ttl) {} 
    void put(const std::string& key, const std::string& val) {
        {
            std::lock_guard<std::mutex> lock(mtx);
            if (indexes.find(key) != indexes.end()) {
                lru.emplace_front(*(indexes.at(key)));
                lru.erase(indexes.at(key));
            } else {
                lru.emplace_front(
                    std::make_tuple(std::move(key), std::move(val),
                        std::chrono::system_clock::now() + std::chrono::milliseconds(ttl)));
                indexes[key] = lru.begin();
            }
        }
        (void)std::async(std::launch::async, &LRUSafe::houseKeeping, this);
    }

    std::string get(const std::string& key) {
        {
            std::lock_guard<std::mutex> lock(mtx);
            if (std::chrono::system_clock::now() - lastCheck > std::chrono::milliseconds(ttl)) {
                houseKeeping();
            }
        }
        if (indexes.find(key) != indexes.end()) {
            std::string ret;
            {
                std::lock_guard<std::mutex> lock(mtx);
                ret = std::get<1>(*(indexes.at(key)));
                lru.emplace_front(*(indexes.at(key)));
                lru.erase(indexes.at(key));
            }

            (void)std::async(std::launch::async, &LRUSafe::houseKeeping, this);
            return ret;
        }
        
        throw std::runtime_error("no key " + key);
    }

    void houseKeepingSafe() {
        std::lock_guard<std::mutex> lock(mtx);
        houseKeeping();
    }
    void houseKeeping() {
        auto now = std::chrono::system_clock::now();
        auto end = std::remove_if(lru.begin(), lru.end(), [&now](auto& elem){
            return (std::get<2>(elem) < now);
        });

        std::for_each(end, lru.end(), [this](auto& elem) { indexes.erase(std::get<0>(elem)); });
        lru.erase(end, lru.end());

        while(lru.size() > cap) {
            indexes.erase(std::get<0>(lru.back()));
            lru.pop_back();
        }

        lastCheck = now;
    }

    void dump() {
        std::cout << "keys: ";
        for(auto& [k, _] : indexes) {
            std::cout << k << " ";
        }
        std::cout << std::endl;
    }
private:
    std::deque<DATA_ENTRY> lru;
    std::unordered_map<std::string, DEQ::const_iterator> indexes;
    std::mutex mtx;
    size_t cap;
    int ttl;
    std::chrono::time_point<std::chrono::system_clock> lastCheck = std::chrono::system_clock::now();
};