#include <unordered_map>
#include <typeindex>
#include <functional>
#include <iostream>
#include <memory>
#include <chrono>
#include <format>

struct Subscription
{
    std::type_index typeid_;
    std::size_t subid_;
};

struct ChannelBase
{
};

template <class E>
class Channel : public ChannelBase
{
private:
    std::unordered_map<size_t, std::function<void(const E &)>> subs_;
    size_t next_id = 0;

public:
    size_t add(std::function<void(const E &)> sub)
    {
        subs_.emplace(++next_id, std::move(sub));
        return next_id;
    }
    size_t publish(const E &event)
    {
        for (auto &[id, sub] : subs_)
        {
            sub(event);
        }
        return subs_.size();
    }
};

class EventBus
{
private:
    std::unordered_map<std::type_index, std::shared_ptr<ChannelBase>> channels_;

public:
    template <class E>
    Subscription subscribe(std::function<void(const E &)> handle_fn)
    {
        auto tid = std::type_index(typeid(std::remove_cv_t<E>));
        auto iter = channels_.find(tid);
        if (iter == channels_.end())
        {
            channels_.emplace(tid, std::make_shared<Channel<E>>());
        }
        auto c = std::static_pointer_cast<Channel<E>>(channels_.at(tid));
        return Subscription{tid, c->add(std::move(handle_fn))};
    }
    template <class E>
    size_t publish(const E &event)
    {
        auto tid = std::type_index(typeid(std::remove_cv_t<E>));
        auto iter = channels_.find(tid);
        if (iter == channels_.end())
        {
            std::cout << "no subscription for type id " << tid.name() << std::endl;
            return 0;
        }
        auto c = std::static_pointer_cast<Channel<E>>(iter->second);
        return c->publish(event);
    }
};

struct EventLogin
{
    size_t uid;
    std::string uname;
    std::string client_type;
    std::chrono::system_clock::time_point login_time;
};

struct EventLogout
{
    size_t uid;
    std::string uname;
    std::chrono::system_clock::time_point login_time;
};

int main()
{
    EventBus bus;
    auto sub1 = bus.subscribe<EventLogin>([](const EventLogin &e)
                                          { std::cout << "User login, "
                                                      << "uid=" << e.uid << ", uname" << e.uname
                                                      << ", client_type=" << e.client_type
                                                      << ", login_time="
                                                      << std::format("{:%Y-%m-%d %H:%M:%S}", e.login_time)
                                                      << std::endl; });
    auto sub2 = bus.subscribe<EventLogout>([](const EventLogout &e)
                                           { std::cout << "User logout, "
                                                       << "uid=" << e.uid << ", uname" << e.uname
                                                       << ", login_time="
                                                       << std::format("{:%Y-%m-%d %H:%M:%S}", e.login_time)
                                                       << std::endl; });
    auto sub3 = bus.subscribe<EventLogin>([](const EventLogin &e)
                                          { std::cout << "User " << e.uname << " login" << std::endl; });

    auto sub4 = bus.subscribe<EventLogout>([](const EventLogout &e)
                                           { std::cout << "User " << e.uname
                                                       << " logout, live time "
                                                       << std::chrono::duration_cast<std::chrono::nanoseconds>(std::chrono::system_clock::now() - e.login_time)
                                                       << std::endl; });

    bus.publish<EventLogin>(EventLogin{100, "user 01", "operator", std::chrono::system_clock::now()});
    bus.publish<EventLogin>(EventLogin{102, "user 02", "admin", std::chrono::system_clock::now()});

    bus.publish<EventLogout>(EventLogout{100, "user 01", std::chrono::system_clock::now()});
    bus.publish<EventLogout>(EventLogout{102, "user 02", std::chrono::system_clock::now()});

    return 0;
}