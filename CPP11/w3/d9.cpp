#include <string>
#include <unordered_map>
#include <list>
#include <chrono>
#include <optional>
#include <sstream>
#include <iostream>
#include <memory>
#include <thread>
#include <mutex>
#include <shared_mutex>
#include <vector>
#include <string_view>
struct Response
{
    std::string message;
    uint64_t code;
};

struct StringHash
{
    using is_transparent = void;
    size_t operator()(std::string_view s) const noexcept
    {
        return std::hash<std::string_view>{}(s);
    }
};
template <class T>
class LRU
{
    using Key = std::string;
    struct Node
    {
        std::shared_ptr<T> t;
        std::chrono::steady_clock::time_point time;
        Key k;
    };
    std::shared_mutex mtx;

private:
    std::list<Node> message_cache;
    std::unordered_map<Key, typename std::list<Node>::iterator, StringHash, std::equal_to<>> search;
    const size_t cap = 1000;
    size_t ttl;
    uint64_t message_seq = 0;

public:
    LRU(size_t n) : ttl(n) {}
    void house_keeping_unsafe()
    {
        std::list<Node> node_to_remove;

        auto it = message_cache.begin();
        while (it != message_cache.end() && std::chrono::steady_clock::now() - it->time >= std::chrono::seconds(ttl))
        {
            it++;
        }

        node_to_remove.splice(node_to_remove.begin(), message_cache, message_cache.begin(), it);

        if (message_cache.size() > cap)
        {
            node_to_remove.splice(
                node_to_remove.end(),
                message_cache,
                message_cache.begin(),
                std::next(message_cache.begin(), message_cache.size() - cap));
        }

        for (auto &n : node_to_remove)
        {
            search.erase(n.k);
        }
    }

    template <class U>
    Key push(U &&u)
    {
        std::string ret;
        {
            std::scoped_lock<std::shared_mutex> lock(mtx);
            Key this_key = std::to_string(message_seq);
            message_cache.emplace_back(
                std::make_shared<T>(std::forward<U>(u)),
                std::chrono::steady_clock::now(),
                this_key);
            message_seq++;
            search[this_key] = std::prev(message_cache.end());
            ret = this_key;
            house_keeping_unsafe();
        }
        return ret;
    }

    std::shared_ptr<T> get(std::string_view k)
    {

        std::scoped_lock<std::shared_mutex> lock(mtx);
        house_keeping_unsafe();

        auto it = search.find(k);
        if (it != search.end())
        {
            message_cache.splice(message_cache.end(), message_cache, it->second);
            it->second->time = std::chrono::steady_clock::now();
            return it->second->t;
        }
        return nullptr;
    }

    std::string view()
    {
        std::stringstream ss;
        auto now_time = std::chrono::steady_clock::now();
        {
            std::shared_lock<std::shared_mutex> lock(mtx);
            for (auto &n : message_cache)
            {
                if (now_time - n.time >= std::chrono::seconds(ttl))
                {
                    continue;
                }
                ss << "= " << n.t->message << " " << n.t->code << " " << n.k << "\n";
            }
        }

        return ss.str();
    }
};

int main()
{
    LRU<Response> cache(2);
    std::vector<std::thread> threads;
    for (size_t i = 0; i < 10; i++)
    {
        threads.emplace_back([i, &cache]()
                             {
            auto key1 = cache.push(Response{"message1", 100+i});
            auto key2 = cache.push(Response{"message2", 200+i});
            auto key3 = cache.push(Response{"message3", 300+i});
            auto key4 = cache.push(Response{"message4", 400+i});
            std::cout << cache.view() << std::endl;
            if (auto p = cache.get(key1); p) {
                std::cout <<p->message << std::endl;
            }
            std::cout << cache.view() << std::endl;
            if (auto p = cache.get(key2); p) {
                std::cout <<p->message << std::endl;
            }
            std::cout << cache.view() << std::endl; });
    }

    for (auto &t : threads)
    {
        t.join();
    }
    std::this_thread::sleep_for(std::chrono::seconds(3));
    std::cout << "expired: " << cache.view() << std::endl;

    return 0;
}