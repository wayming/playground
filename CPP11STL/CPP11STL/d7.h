#include <future>
#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <chrono>

int run(std::vector<std::string>& files, const std::string& searchStr) {
	std::vector<std::future<int>> futs;
	auto begin = std::chrono::system_clock::now();
	for (auto& f : files) {
		futs.emplace_back(
			std::async([&f](const std::string& substr) {
			std::ifstream fs(f, std::ifstream::in);
			if (!fs.is_open()) {
				std::cout << "Failed to open file " << f << std::endl;
				throw std::runtime_error("file " + f + " not found.");
			}

			std::stringstream ss;
			ss << fs.rdbuf();
			std::string src = ss.str();
			size_t pos = src.find(substr);
			int count = 0;
			while (pos != std::string::npos) {
				count++;
				pos = src.find(substr, pos + substr.size());
			}
			return count;
		}, searchStr));
	}

	int totalMatch = 0;
	for (auto& fut : futs) {
		totalMatch += fut.get();
	}

	auto duration = std::chrono::system_clock::now() - begin;
	std::cout << "Find " << totalMatch << " occurence in " << std::chrono::duration_cast<std::chrono::milliseconds>(duration).count() << "ms" << std::endl;
	return totalMatch;
}