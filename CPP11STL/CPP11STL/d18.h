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
        auto tm = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());
        auto tmStr = std::string(std::ctime(&tm));
        tmStr.erase(std::remove(tmStr.begin(), tmStr.end(), '\n'), tmStr.end());
        std::cout << tmStr << " " << message << std::endl;
    }
};
class ReversePrinterObserver : public Observer {
public:
    void onNotify(const std::string& message) override {
        auto msg = message;
        std::reverse(msg.begin(), msg.end());
        std::cout << msg << std::endl;
    }
};


class Subject {
    std::vector<std::weak_ptr<Observer>> obs;
public:
    void add(std::weak_ptr<Observer> ob) {
        obs.emplace_back(std::move(ob));
    }
    void notify(const std::string& message) {
        auto iter = obs.begin();
        while(iter != obs.end()) {
            auto ob = iter->lock();
            if (ob) {
                ob->onNotify(message);
                ++iter;
            } else {
                iter = obs.erase(iter);
            }
        }
    }
};