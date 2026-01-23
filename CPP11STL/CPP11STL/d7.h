#include <future>
#include <vector>
#include <iostream>
#include <fstream>
#include <sstream>
#include <algorithm>
#include <chrono>

void run(std::vector<std::string>& files, const std::string& searchStr) {
	std::vector<std::future<int>> results;
	auto begin = std::chrono::steady_clock::now();
	for(auto& file: files) {
		results.emplace_back(
			std::async([&file, &searchStr](){
				std::ifstream inStream(file);
				if (! inStream.good()) {
					throw std::runtime_error(std::string("Failed to open file " + file));
				}
				std::stringstream ss;
				ss << inStream.rdbuf();
				std::string contents = ss.str();
				int matches = 0;
				auto found = contents.find(searchStr);
				while(found != std::string::npos) {
					matches++;
					found = contents.find(searchStr, found+1);
				}

				inStream.close();
				return matches;
			}));
	}

	int totalMatches = 0;
	for (auto& r : results) {
		totalMatches += r.get();
	}
	auto duration = std::chrono::steady_clock::now() - begin;
	std::cout << "Total found " << totalMatches << ", duration " 
			  << std::chrono::duration_cast<std::chrono::milliseconds>(duration).count() << "ms" << std::endl;
}