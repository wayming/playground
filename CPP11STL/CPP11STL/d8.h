#include <vector>
#include <functional>
#include <string>
#include <iostream>
#include <thread>
#include <chrono>
class Worker {
public:
	Worker(const std::string& name) : n(name) {}
	void fire(const std::string& message) {
		std::cout << n << " begin." << std::endl;
		std::this_thread::sleep_for(std::chrono::milliseconds(100));
		std::cout << message << std::endl;
		std::cout << n << " done." << std::endl;
	}
private:
	std::string n;
};

class EventHub {
public:
	void subscribe(std::function<void(Worker*, const std::string&)> fun, Worker* thisWorker) {
		handlers.emplace_back([fun, thisWorker](const std::string& message) {
				fun(thisWorker, message);
			});
	}

	void publish(const std::string& message) {
		for (auto& h : handlers) {
			try {
				h(message);
			} catch (std::exception& e) {
				std::cerr << "Failed to invoke a handler, continue. Error" << e.what() << std::endl;
			}
		}
	}
private:
	std::vector<std::function<void(const std::string&)>> handlers;
};