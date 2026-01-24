#include <deque>
#include <tuple>
#include <chrono>
#include <numeric>
#include <algorithm>
class PricingStats {
public:
	PricingStats(size_t timeToLive) : ttl(timeToLive) {}
	void add(int price) {
		auto exprireTime = std::chrono::system_clock::now() + std::chrono::seconds(ttl);
		pricesQueue.emplace_back(std::make_tuple(price, exprireTime));
		houseKeeping();
	}
	
	size_t count() {
		houseKeeping();
		return pricesQueue.size();
	}

	int min() {
		int min = -1;
		houseKeeping();

		if (pricesQueue.size() == 0) { return min; }
		min = std::get<0>(pricesQueue.front());
		std::for_each(pricesQueue.begin(), pricesQueue.end(), [&min](const auto& tup) {min = std::min(std::get<0>(tup), min); });
		return min;
	}

	int max() {
		int max = -1;
		houseKeeping();

		if (pricesQueue.size() == 0) { return max; }
		max = std::get<0>(pricesQueue.front());
		std::for_each(pricesQueue.begin(), pricesQueue.end(), [&max](const auto& tup) {max = std::max(std::get<0>(tup), max); });
		return max;
	}

	void houseKeeping() {
		auto now = std::chrono::system_clock::now();
		while (!pricesQueue.empty()) {
			std::chrono::system_clock::time_point exprireTime;
			std::tie(std::ignore, exprireTime) = pricesQueue.front();

			if (exprireTime < now) {
				pricesQueue.pop_front();
			}
			else {
				break;
			}
		}
	}
private:
	std::deque<std::tuple<int, std::chrono::system_clock::time_point>> pricesQueue;
	size_t ttl;
};