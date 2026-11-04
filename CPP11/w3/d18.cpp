#include <thread>
#include <functional>
#include <vector>
#include <stdexcept>
#include <utility>
#include <memory>
#include <mutex>
#include <atomic>
#include <algorithm>
#include <future>
#include <iostream>

using Callback = std::move_only_function<void(const std::string &)>;
class Downloader
{
private:
    std::vector<Callback> callbacks_;
    std::string url_;
    std::mutex mtx_;
    std::atomic<bool> started_ = false;

public:
    explicit Downloader(const std::string &url) : url_(url) {};
    ~Downloader() {};

    void add(Callback c)
    {
        std::scoped_lock<std::mutex> lk(mtx_);
        callbacks_.emplace_back(std::move(c));
    }

    void start(std::promise<bool> done_pm)
    {
        std::vector<Callback> callbacks;
        {
            std::scoped_lock<std::mutex> lk(mtx_);
            if (std::atomic_exchange(&started_, true))
                return;

            callbacks = std::move(callbacks_);
            callbacks_.clear();
        }

        std::jthread([url = url_, done_pm = std::move(done_pm), cbs = std::move(callbacks)]() mutable
                     {
                        const std::string content = Downloader::fetch(url);
                        for (auto &c : cbs)
                        {
                            try
                            {
                                c(content);
                            }
                            catch(const std::exception& e)
                            {
                                done_pm.set_exception(std::current_exception());
                            }
                         }
                    done_pm.set_value(true); });
    }
    static std::string fetch(const std::string &url)
    {
        auto result = url;
        std::reverse(result.begin(), result.end());
        return result;
    }
};
struct Buffer
{
    std::vector<std::string> data_;
    void add(const std::string &s) { data_.emplace_back(s); }
};
int main()
{
    Downloader d("www.thissite.com");
    auto counter = std::make_shared<int>(0);
    auto buf = std::make_unique<Buffer>();

    auto buffer_pm = std::promise<std::unique_ptr<Buffer>>();
    auto buffer_fu = buffer_pm.get_future();
    auto done_pm = std::promise<bool>();
    auto done_fu = done_pm.get_future();

    d.add([&buffer_pm, buf = std::move(buf)](const std::string &s) mutable
          { buf->add(s); 
        buffer_pm.set_value(std::move(buf)); });
    d.add([counter](const std::string &s)
          { (*counter)++; });

    d.start(std::move(done_pm));
    done_fu.wait();
    std::cout << *counter << std::endl;

    buffer_fu.wait();
    auto still_buf = buffer_fu.get();
    for (auto &s : still_buf->data_)
    {
        std::cout << s << std::endl;
    }
    return 0;
}