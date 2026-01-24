#include <vector>
#include <functional>
#include <string>
#include <iostream>
#include <thread>
#include <chrono>
#include <map>
#include <algorithm>

class EventHub {
	using Listener = std::function<void(const std::string&)>;
	std::vector<Listener> listeners;

public:
	void subscribe(Listener&& listener) {
		std::cout << "rvalue reference" << std::endl;
		listeners.emplace_back(std::move(listener));
	}
	void subscribe(const Listener& listener) {
		std::cout << "lvalue reference" << std::endl;
		listeners.emplace_back(listener);
	}
	void publish(const std::string& message) {
		for(auto& listener : listeners) {
			listener(message);
		}
	}
};

enum class LOG_LEVEL {
	INFO,
	WARNING,
	DEBUG
};
std::map<LOG_LEVEL, std::string> LEVEL {
	{LOG_LEVEL::INFO, "INFO"},
	{LOG_LEVEL::WARNING, "WARNING"},
	{LOG_LEVEL::DEBUG, "DEBUG"},
};
class Logger {
	LOG_LEVEL level;
	public:
		void SetLevel(LOG_LEVEL l) { level = l; }

		std::string Now() {

			time_t tt;
			auto now = std::chrono::system_clock::now();
			tt = std::chrono::system_clock::to_time_t(now);
			std::string timeStr = std::string(ctime(&tt));
			timeStr.erase(std::remove(timeStr.begin(), timeStr.end(), '\n'), timeStr.end());
			return timeStr;
		}
		void Log(LOG_LEVEL l, const std::string& message) {
			if (l < level) return;

			std::cout << "[" << LEVEL.at(l) << "]" << "[" << Now() << "] " << message << std::endl;
		}
};