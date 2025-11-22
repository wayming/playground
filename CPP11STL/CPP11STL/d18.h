#include <iostream>
#include <vector>
#include <memory>
#include <algorithm>
#include <chrono>
#include <ctime>

class Observer {
public:
    virtual void onNotify(const std::string& message) = 0;
};

class TimeObserver : public Observer {
public:
    void onNotify(const std::string& message) override {
        auto now = std::chrono::system_clock::now();
        time_t ts = std::chrono::system_clock::to_time_t(now);
        std::cout << ctime(&ts) << " " << message << std::endl;
    }
};

class SimplePrinterObserver : public Observer {
public:
    void onNotify(const std::string& message) override {
        std::cout << "simple " << message << std::endl;
    }
};


class Subject {
public:
    void registObserver(std::shared_ptr<Observer> ob) {
        obs.emplace_back(ob);
    }

    void notify(const std::string& message) {
        obs.erase(
            std::remove_if(obs.begin(), obs.end(), [](auto& ob) { return ob.expired(); }),
            obs.end());
        for (auto& ob : obs) {
            auto obShared = ob.lock();
            if(obShared) {
                obShared->onNotify(message);
            }
        }
    }
private:
    std::vector<std::weak_ptr<Observer>> obs;
};