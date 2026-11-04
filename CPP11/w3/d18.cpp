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
#include <string>

using Callback = std::move_only_function<void(const std::string &)>;
class Downloader
{
private:
    std::vector<Callback> callbacks_;
    std::string url_;
    std::mutex mtx_;
    bool started_ = false;
    std::jthread worker_;

public:
    explicit Downloader(const std::string &url) : url_(url) {};
    ~Downloader() = default;

    void add(Callback c)
    {
        std::scoped_lock<std::mutex> lk(mtx_);
        if (started_)
            throw std::runtime_error("thread already started, no more callbacks");
        callbacks_.emplace_back(std::move(c));
    }

    void start(std::promise<bool> done_pm)
    {
        std::vector<Callback> callbacks;
        {
            std::scoped_lock<std::mutex> lk(mtx_);
            if (std::exchange(started_, true))
            {
                throw std::logic_error("already started");
            }

            callbacks = std::move(callbacks_);
        }

        std::jthread([url = url_, done_pm = std::move(done_pm), cbs = std::move(callbacks)]() mutable
                     {
                       
                        std::string content; try
                        {
                            content = Downloader::fetch(url);
                        }
                        catch(...)
                        {
                           throw std::logic_error("already started");
                        }
                        
                        
                        std::exception_ptr first_cb_exception;
                        for (auto &c : cbs)
                        {
                            try
                            {
                                c(content);
                            }
                            catch(...)
                            {
                                if (!first_cb_exception) first_cb_exception = std::current_exception();
                            }
                         }
                         if (first_cb_exception) {
                            done_pm.set_exception(first_cb_exception);
                            return;
                         } 
                    done_pm.set_value(true); })
            .detach();
    }

    void start2()
    {
        {
            std::scoped_lock<std::mutex> lk(mtx_);
            if (std::exchange(started_, true))
            {
                throw std::logic_error("already started");
            }
        }

        worker_ = std::jthread([this]() mutable
                               {
                       
                        std::string content; try
                        {
                            content = Downloader::fetch(url_);
                        }
                        catch(...)
                        {
                            throw std::logic_error("already started");
                        }
                        
                        
                        std::exception_ptr first_cb_exception;
                        for (auto &c : callbacks_)
                        {
                            try
                            {
                                c(content);
                            }
                            catch(...)
                            {
                                if (!first_cb_exception) first_cb_exception = std::current_exception();
                            }
                         }
                         if (first_cb_exception) {
                            throw first_cb_exception;
                         } });
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
    auto counter = std::make_shared<std::atomic<int>>(0);
    auto buf = std::make_unique<Buffer>();

    auto buffer_pm = std::promise<std::unique_ptr<Buffer>>();
    auto buffer_fu = buffer_pm.get_future();
    auto done_pm = std::promise<bool>();
    auto done_fu = done_pm.get_future();

    d.add([pm = std::move(buffer_pm), buf = std::move(buf)](const std::string &s) mutable
          { buf->add(s); 
        pm.set_value(std::move(buf)); });
    d.add([counter](const std::string &s)
          { (*counter)++; });

    // d.start(std::move(done_pm));
    // done_fu.get();
    d.start2();
    std::cout << *counter << std::endl;

    auto still_buf = buffer_fu.get();
    for (auto &s : still_buf->data_)
    {
        std::cout << s << std::endl;
    }
    return 0;
}