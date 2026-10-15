#include <string>
#include <unordered_map>
#include <list>
#include <chrono>
#include <optional>
#include <sstream>
#include <iostream>
struct Response
{
    std::string message;
    uint32_t code;
};

template <class T>
class LRU
{
    using Key = uint32_t;
    struct Node
    {
        T t;
        std::chrono::steady_clock::time_point time;
        Key k;
    };

private:
    std::list<Node> message_cache;
    std::unordered_map<Key, typename std::list<Node>::iterator> search;
    const size_t cap = 1000;
    size_t ttl;
    uint64_t key = 0;

public:
    LRU(size_t n) : ttl(n) {}
    void house_keeping()
    {
        auto it = message_cache.begin();
        while (std::chrono::steady_clock::now() - it->time >= std::chrono::seconds(ttl))
        {
            it++;
        }

        std::list<Node> node_to_remove;
        node_to_remove.splice(node_to_remove.begin(), message_cache, message_cache.begin(), it);
        for (auto n : node_to_remove)
        {
            search.erase(n.k);
        }
    }
    template <class U>
    Key push(U &&u)
    {
        house_keeping();
        if (message_cache.size() >= cap)
        {
            message_cache.erase(message_cache.begin(), std::next(message_cache.begin(), message_cache.size() - cap + 1));
        }
        message_cache.emplace_back(
            std::forward<U>(u),
            std::chrono::steady_clock::now(),
            ++key);
        search[key] = std::prev(message_cache.end());
        return key;
    }

    std::optional<T> get(Key k)
    {
        auto it = search.find(k);
        if (it != search.end())
        {
            message_cache.splice(message_cache.end(), message_cache, it->second);
            it->second->time = std::chrono::steady_clock::now();
            return it->second->t;
        }
        return std::nullopt;
    }
    std::string view()
    {
        std::stringstream ss;
        for (auto n : message_cache)
        {
            ss << "= " << n.t << " " << n.k << "\n";
        }
        return ss.str();
    }
};

int main()
{
    LRU<int> cache(10);
    auto key1 = cache.push(10);
    auto key2 = cache.push(20);
    auto key3 = cache.push(30);
    std::cout << cache.view() << std::endl;
    std::cout << cache.get(key1).value() << std::endl;
    std::cout << cache.view() << std::endl;
    std::cout << cache.get(key2).value() << std::endl;
    std::cout << cache.view() << std::endl;

    return 0;
}