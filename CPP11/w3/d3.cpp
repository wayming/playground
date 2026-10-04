#include <unordered_map>
#include <typeindex>
#include <functional>
#include <iostream>
#include <memory>
#include <chrono>
#include <format>
#include <utility>
#include <atomic>
#include <mutex>
#include <thread>
#include <sstream>

template <class E>
class Handler
{
    struct Concept
    {
        virtual ~Concept() = default;
        virtual void call(const E &) = 0;
    };

    template <class F>
    struct Model final : public Concept
    {
        F f;
        template <class G>
        explicit Model(G &&g) : f(std::forward<G>(g)) {};
        void call(const E &e) override
        {
            f(e);
        }
    };
    std::unique_ptr<Concept> ptr_;

public:
    template <class F>
        requires(!std::same_as<std::remove_cvref_t<F>, Handler>)
    explicit Handler(F &&f) : ptr_(std::make_unique<Model<std::decay_t<F>>>(std::forward<F>(f)))
    {
    }
    void operator()(const E &e) { ptr_->call(e); }
};

class EventBus;
class Subscription;
namespace detail
{
    class BusState;
}

class [[nodiscard]] Subscription
{
private:
    std::type_index typeidx_ = std::type_index(typeid(void));
    std::size_t subid_ = 0;
    std::weak_ptr<detail::BusState> bus_state_;

public:
    Subscription() = default;
    Subscription(std::type_index tid, std::size_t sid, std::weak_ptr<detail::BusState> state) noexcept
        : typeidx_(tid), subid_(sid), bus_state_(state) {}
    ~Subscription() noexcept { unsubscribe(); };
    Subscription(const Subscription &) = delete;
    Subscription(Subscription &&that) noexcept
        : typeidx_(std::exchange(that.typeidx_, std::type_index(typeid(void)))),
          subid_(std::exchange(that.subid_, 0)), bus_state_(std::exchange(that.bus_state_, {}))
    {
    }
    Subscription &operator=(const Subscription &) = delete;
    Subscription &operator=(Subscription &&that) noexcept
    {
        if (this == &that)
        {
            return *this;
        }
        unsubscribe();
        typeidx_ = std::exchange(that.typeidx_, std::type_index(typeid(void)));
        subid_ = std::exchange(that.subid_, 0);
        bus_state_ = std::exchange(that.bus_state_, {});
        return *this;
    }

    void unsubscribe();
};

class ChannelBase
{
public:
    virtual ~ChannelBase() = default;
    virtual std::shared_ptr<void> remove(size_t) = 0;
};

template <class E>
class Channel : public ChannelBase
{
public:
    struct Sub
    {
        size_t subid_ = 0;
        std::function<void(const E &)> fn_;
        // Handler<E> handler_;
        std::atomic<bool> active_ = true;

    public:
        Sub(size_t s, std::function<void(const E &)> fn) : subid_(s), fn_(std::move(fn)) {}
        // Sub(size_t s, std::function<void(const E &)> &&fn) : subid_(s), fn_(std::forward<std::function<void(const E &)>>(fn)) {}
        ~Sub() = default;
        Sub(const Sub &) = delete;
        Sub(Sub &&) = delete;
        Sub &operator=(const Sub &) = delete;
        Sub &operator=(Sub &&) = delete;
    };

private:
    std::vector<std::shared_ptr<Sub>> subs_;
    size_t next_id = 0;
    std::string channel_type = std::string(std::type_index(typeid(E)).name());

public:
    ~Channel() = default;

    static size_t publish_snapshot(const std::vector<std::shared_ptr<Sub>> &snapshot, const E &event)
    {
        size_t count = 0;
        for (auto &sub : snapshot)
        {
            if (sub->active_.load())
            {
                sub->fn_(event);
                ++count;
            }
        }
        return count;
    }

    std::vector<std::shared_ptr<Sub>> snapshot()
    {
        return subs_;
    }

    size_t add(std::function<void(const E &)> sub)
    {
        subs_.emplace_back(std::make_shared<Sub>(++next_id, std::move(sub)));
        std::cout << channel_type << ":" << next_id << " subscribed." << std::endl;
        return next_id;
    }
    std::shared_ptr<void> remove(size_t id) override
    {
        auto iter = std::find_if(subs_.begin(), subs_.end(),
                                 [id](const std::shared_ptr<Sub> &s)
                                 { return s->subid_ == id; });
        if (iter != subs_.end())
        {
            auto dead = *iter;
            (*iter)->active_.store(false);
            subs_.erase(iter);
            std::cout << channel_type << ":" << id << " unsubscribed." << std::endl;
            return dead;
        }
        else
        {
            return nullptr;
        }
    }
};

namespace detail
{
    class BusState;
    class BusStateScopeLock;

    class BusState
    {
        friend class ::EventBus;

    private:
        std::unordered_map<std::type_index, std::shared_ptr<ChannelBase>> channels_;

        std::mutex mtx_;

    public:
        void unsubscribe(std::type_index typeidx, size_t subid)
        {
            std::shared_ptr<void> dead;
            {

                std::scoped_lock<std::mutex> lock(mtx_);

                auto channel_iter = channels_.find(typeidx);
                if (channel_iter == channels_.end())
                {
                    return;
                }
                dead = channel_iter->second->remove(subid);
            }
        }
        void lock()
        {
            mtx_.lock();
        }
        void unlock()
        {
            mtx_.unlock();
        }
    };
};
class EventBus
{
private:
    std::shared_ptr<detail::BusState> state_;

public:
    EventBus() { state_ = std::make_shared<detail::BusState>(); }
    ~EventBus() { state_.reset(); }
    template <class E, class E2 = std::remove_cv_t<E>>
    Subscription subscribe(std::function<void(const E &)> handle_fn)
    {
        auto tid = std::type_index(typeid(E2));
        size_t subid = 0;
        {
            std::scoped_lock<detail::BusState> lock(*state_);
            auto iter = state_->channels_.find(tid);
            if (iter == state_->channels_.end())
            {
                state_->channels_.emplace(tid, std::make_shared<Channel<E2>>());
            }
            auto channel = std::static_pointer_cast<Channel<E2>>(state_->channels_.at(tid));
            subid = channel->add(std::move(handle_fn));
        }
        return Subscription(tid, subid, std::weak_ptr<detail::BusState>(state_));
    }
    template <class E, class E2 = std::remove_cv_t<E>>
    size_t publish(const E &event)
    {
        auto tid = std::type_index(typeid(E2));
        std::vector<std::shared_ptr<typename Channel<E2>::Sub>> subs_snapshot;
        {
            std::scoped_lock<detail::BusState> lock(*state_);

            auto iter = state_->channels_.find(tid);
            if (iter == state_->channels_.end())
            {
                std::cout << "no subscription for type id " << tid.name() << std::endl;
                return 0;
            }
            auto c = std::static_pointer_cast<Channel<E2>>(iter->second);
            subs_snapshot = c->snapshot();
        }
        return Channel<E2>::publish_snapshot(subs_snapshot, event);
    };
};
void Subscription::unsubscribe()
{
    if (auto state = bus_state_.lock())
    {
        state->unsubscribe(typeidx_, subid_);
    }
    typeidx_ = std::type_index(typeid(void));
    subid_ = 0;
    bus_state_.reset();
}

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

void session_function(EventBus &bus, size_t count)
{
    auto tid = std::this_thread::get_id();
    for (size_t i = 0; i < count; i++)
    {
        std::stringstream ss;
        ss << tid << ":" << i;
        bus.publish<EventLogin>(EventLogin{i, ss.str(), "admin", std::chrono::system_clock::now()});
        bus.publish<EventLogout>(EventLogout{i, ss.str(), std::chrono::system_clock::now()});
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
}
int main()
{
    EventBus bus;
    auto sub1 = bus.subscribe<EventLogin>([](const EventLogin &e)
                                          { std::cout << "User login, "
                                                      << "uid=" << e.uid << ", uname=" << e.uname
                                                      << ", client_type=" << e.client_type
                                                      << ", login_time="
                                                      << std::format("{:%Y-%m-%d %H:%M:%S}", e.login_time)
                                                      << std::endl; });
    auto sub2 = bus.subscribe<EventLogout>([](const EventLogout &e)
                                           { std::cout << "User logout, "
                                                       << "uid=" << e.uid << ", uname=" << e.uname
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

    std::vector<std::thread> sessions;
    for (size_t i = 0; i < 10; i++)
    {
        sessions.emplace_back(session_function, std::ref(bus), 100);
    }

    for (auto &ss : sessions)
    {
        ss.join();
    }
    return 0;
}