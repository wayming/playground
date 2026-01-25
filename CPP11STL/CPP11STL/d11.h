#include <map>
#include <string>
#include <vector>
#include <variant>
#include <memory>
#include <iostream>
#include <algorithm>
#include <typeinfo>
#include <vector>
#include <functional>
#include <regex>

std::string trim(const std::string& input) {
	auto isSpace = [](unsigned char c) { return std::isspace(c); };
	auto begin = std::find_if_not(input.begin(), input.end(), isSpace);
	auto end = std::find_if_not(input.rbegin(), input.rend(), isSpace).base();
	if (begin >= end) {
		return std::string();
	} else {
		return std::string(begin, end);
	}
}

std::string toLower(const std::string& input) {
	std::string result;
	result.resize(input.size());
	std::transform(input.begin(), input.end(), result.begin(), [](unsigned char c) { return std::tolower(c); });
	return result;
}

std::string removePunct(const std::string& input) {
	auto notPunct = [](unsigned char c) { return !std::ispunct(c); };
	std::string result;
	// result.resize(input.size());
	// auto end = std::copy_if(input.begin(), input.end(), result.begin(), isPunct);
	// result.resize(std::distance(result.begin(), end));
	std::copy_if(input.begin(), input.end(), std::back_inserter(result), notPunct);
	return result;
}

std::string regexReplace(const std::string& input, const std::regex& r, const std::string& replace) {
	std::string result;
	std::regex_replace(std::back_inserter(result), input.begin(), input.end(), r, replace);
	return result;
}

class TextProcessPipeLine {
	std::vector<std::function<std::string(std::string)>> processors;

public:
	TextProcessPipeLine& addProcessor(const std::function<std::string(std::string)>& p) {
		processors.emplace_back(p);
		return *this;
	}
	std::string run(const std::string& input) {
		std::string result = input;
		for (auto& p : processors) {
			result = p(result);
		}
		return result;
	}
};