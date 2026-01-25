#include <deque>
#include <tuple>
#include <chrono>
#include <numeric>
#include <algorithm>
#include <optional>
class SlidingWindowPricingStats {
	std::chrono::system_clock::duration secondsToLive;
	std::deque<std::tuple<std::chrono::time_point<std::chrono::system_clock>, int>> prices;
public:
	SlidingWindowPricingStats(size_t ttl) : secondsToLive(std::chrono::seconds(ttl)) {}
	void add(int price) {
		prices.emplace_back(std::chrono::system_clock::now() + secondsToLive, price);
	}

	void houseKeeping() {
		auto now = std::chrono::system_clock::now();
		while(!prices.empty()) {
			auto& [ttl, price] = prices.front();
			if (ttl > now) {
				break;
			}
			std::cout << "pop " << price << std::endl;
			prices.pop_front();
		}
	}

	std::optional<int> max() {
		houseKeeping();
		if (prices.empty()) return std::nullopt;
		int highestPrice = std::get<1>(prices.front());
		for(auto& t : prices) {
			auto& [ttl, price] = t;
			if (price > highestPrice) highestPrice = price;
		}
		return highestPrice;
	}

	std::optional<int> min() {
		houseKeeping();
		if (prices.empty()) return std::nullopt;
		int lowestPrice = std::get<1>(prices.front());
		for(auto& t : prices) {
			auto& [ttl, price] = t;
			if (price < lowestPrice) lowestPrice = price;
		}
		return lowestPrice;
	}

	size_t count() { houseKeeping(); return prices.size(); }

	std::optional<double> avg() {
		houseKeeping();
		if (prices.empty()) return std::nullopt;
		int count = 0;
		int all = 0;
		for(auto& t : prices) {
			auto& [ttl, price] = t;
			all += price;
			count++;
		}
		return all/count;
	}
};