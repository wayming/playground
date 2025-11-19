#include <map>
#include <regex>
#include <functional>
#include <vector>
#include <sstream>
#include <deque>
#include <tuple>
struct CommandParser {
	using Func = std::function<std::any(const std::vector<std::any>&)>;

	CommandParser() {
		regFunc("ADD", [](const std::vector<std::any>& v) {
			if (v.size() != 2) {
				throw std::runtime_error("Expecting two parameters for ADD operation");
			}
			const auto& param1Type = v[0].type();
			const auto& param2Type = v[1].type();
			if (param1Type != typeid(std::string) || param2Type != typeid(std::string)) {
				throw std::runtime_error("Invalid parameter type.");
			}
			try {
				auto op1 = std::stol(std::any_cast<std::string>(v[0]));
				auto op2 = std::stol(std::any_cast<std::string>(v[1]));
				return op1 + op2;
			} catch (std::exception& e) {
				std::cerr << "Failed to cast any value to its type " << param1Type.name() << std::endl;
				throw e;
			}
		});

		regFunc("MULT", [](const std::vector<std::any>& v) {
			if (v.size() != 2) {
				throw std::runtime_error("Expecting two parameters for ADD operation");
			}
			const auto& param1Type = v[0].type();
			const auto& param2Type = v[1].type();
			if (param1Type != typeid(std::string) || param2Type != typeid(std::string)) {
				throw std::runtime_error("Invalid parameter type.");
			}
			try {
				auto op1 = std::stol(std::any_cast<std::string>(v[0]));
				auto op2 = std::stol(std::any_cast<std::string>(v[1]));
				return op1 * op2;
			}
			catch (std::exception& e) {
				std::cerr << "Failed to cast any value to its type " << param1Type.name() << std::endl;
				throw e;
			}
		});
		regFunc("ECHO", [](const std::vector<std::any>& v) {
			if (v.size() != 1) {
				throw std::runtime_error("Expecting two parameters for ADD operation");
			}
			const auto& param1Type = v[0].type();
			if (param1Type != typeid(std::string)) {
				throw std::runtime_error("Invalid parameter type.");
			}
			try {
				return std::any_cast<std::string>(v[0]);
			}
			catch (std::exception& e) {
				std::cerr << "Failed to cast any value to its type " << param1Type.name() << std::endl;
				throw e;
			}
		});
	}
	void addCommand(const std::string& cmd) {
		std::regex pattern(R"(\s*(\w+))");
		auto patternIter = std::sregex_iterator(cmd.begin(), cmd.end(), pattern);
		std::sregex_iterator patternEnd;
		std::vector<std::string> tokens;
		while(patternIter != patternEnd) {
			tokens.push_back(patternIter->str());
			++patternIter;
		}

		if (tokens.empty()) {
			throw std::runtime_error("Failed to parse command string " + cmd);
		}
		const std::string& key = tokens[0];
		std::vector<std::string> params;
		params.reserve(tokens.size() - 1);
		std::move(tokens.begin() + 1, tokens.end(), std::back_inserter(params));
		commandsQueue.emplace_back(key, std::move(params));
	}

	void dump() {
		for (auto& cmd : commandsQueue) {
			std::cout << '"' << std::get<0>(cmd) << '"' << ": [";
			auto& v = std::get<1>(cmd);
			if (!v.empty()) {
				auto iter = v.begin();
				std::cout << *iter;
				++iter;
				while (iter != v.end()) {
					std::cout << ", " << *iter;
					++iter;
				}
			}

			std::cout << "]" << std::endl;
		}

	}

	void eval() {

		for (auto& cmd : commandsQueue) {
			std::string op;
			std::vector<std::string> params;
			std::tie(op, params) = cmd;
			if (op.empty()) {
				throw std::runtime_error("No handler for operation " + op);
			}
			std::vector<std::any> anyParams;
			std::copy(params.begin(), params.end(), std::back_inserter(anyParams));
			std::cout << anyToString(funcsMap[op](anyParams)) << std::endl;
		}
	}

	std::string anyToString(const std::any& val) {
		if (!val.has_value()) {
			throw std::runtime_error("No value found.");
		}

		const auto& valType = val.type();
		try {
			if (valType == typeid(int)) return std::to_string(std::any_cast<int>(val));
			if (valType == typeid(long)) return std::to_string(std::any_cast<long>(val));
			if (valType == typeid(std::string)) return std::any_cast<std::string>(val);
		}
		catch (std::exception& e) {
			std::cerr << "Failed to cast any value to its type " << valType.name() << std::endl;
			throw e;
		}
		return "NULL";

	}
	void regFunc(const std::string& op, Func f) {
		funcsMap[op] = f;
	}

	std::unordered_map<std::string, Func> funcsMap;

	std::deque<std::tuple<std::string, std::vector<std::string>>> commandsQueue; // OP => Params

};

