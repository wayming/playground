#include <map>
#include <regex>
#include <functional>
#include <vector>
#include <sstream>
#include <deque>
#include <tuple>
#include <variant>
#include <regex>
#include <queue>

std::vector<std::string> split(const std::string& src) {
	std::vector<std::string> tokens;
	size_t start = 0;
	while(start != std::string::npos) {
		auto tokenBegin = src.find_first_not_of(' ', start);
		if (tokenBegin == std::string::npos ) break; // end of string
		auto tokenEnd = src.find_first_of(' ', tokenBegin);
		tokens.emplace_back(src.substr(tokenBegin, tokenEnd-tokenBegin));
		start = tokenEnd;
	}
	return tokens;
}

std::vector<std::string> splitRe(const std::string& src) {
	std::regex e("\\w+");
	std::sregex_token_iterator begin(src.begin(), src.end(), e);
	std::sregex_token_iterator end;
	return std::vector<std::string>(begin, end);
}

class CommandParser {
	using ValueType = std::variant<long, double, std::string>;
	using OpFuncType = std::function<ValueType(const std::vector<ValueType>&)>;
	using ValueVecType = std::vector<ValueType>;
	std::unordered_map<std::string, OpFuncType> commandReg;
	std::queue<std::function<ValueType()>> commandQueue;
public:
	CommandParser() {
		regFunc("ADD", [](const ValueVecType& params) -> ValueType {
			if(params.size() != 2) throw std::runtime_error("Invalid number of parameters for ADD op");
			// if (std::holds_alternative<std::string>(params[0]) &&
			// 	std::holds_alternative<std::string>(params[1])) {
			// 		return std::get<std::string>(params[0]) + std::get<std::string>(params[1]);
			// }
			// else if (std::holds_alternative<long>(params[0]) &&
			// 	std::holds_alternative<long>(params[1])) {
			// 		return std::get<long>(params[0]) + std::get<long>(params[1]);
			// }
			// else if (std::holds_alternative<double>(params[0]) &&
			// 	std::holds_alternative<double>(params[1])) {
			// 		return std::get<double>(params[0]) + std::get<double>(params[1]);
			// } else {
			// 	throw std::runtime_error("Invalid types of operands.");
			// }

			// if (auto a = std::get_if<double>(&params[0])) {
			// 	if (auto b = std::get_if<double>(&params[1])) return *a + *b;

			// 	if (auto b = std::get_if<long>(&params[1])) return *a + *b;
			// }

			// if (auto a = std::get_if<long>(&params[0])) {
			// 	if (auto b = std::get_if<long>(&params[1])) return *a + *b;
			// 	if (auto b = std::get_if<double>(&params[1])) return *a + *b;
			// }

			// if (auto a = std::get_if<std::string>(&params[0])) {
			// 	if (auto b = std::get_if<std::string>(&params[1])) return *a + *b;
			// }
			// throw std::runtime_error("Invalid types of operands.");


			return std::visit([](auto&& a, auto&& b) -> ValueType {
				using T1 = std::decay_t<decltype(a)>;
				using T2 = std::decay_t<decltype(b)>;

				if constexpr (std::is_same_v<T1, std::string> && std::is_same_v<T2, std::string>) {
					return a + b;
				} else if constexpr (!std::is_same_v<T1, std::string> && !std::is_same_v<T2, std::string>) {
					return a + b;
				} else {
					throw std::runtime_error("Invalid types of operands.");
				}
			}, params[0], params[1]);
		});

		regFunc("MULT", [](const ValueVecType& params) -> ValueType {
			if(params.size() != 2) throw std::runtime_error("Invalid number of parameters for MULT op");
			return std::visit([](auto&& a, auto&& b) -> ValueType {
				using T1 = std::decay_t<decltype(a)>;
				using T2 = std::decay_t<decltype(b)>;

				if constexpr (!std::is_same_v<T1, std::string> && !std::is_same_v<T2, std::string>) {
					return a * b;
				} else {
					throw std::runtime_error("Invalid types of operands.");
				}
			}, params[0], params[1]);
		});

		regFunc("ECHO", [](const ValueVecType& params) -> ValueType {
			if(params.size() != 1) throw std::runtime_error("Invalid number of parameters for ECHO op");
			return std::visit([](auto&& a) -> ValueType {
				return a;
			}, params[0]);
		});
	}
	void addCommand(const std::string& cmd) {
		auto tokens = split(cmd);
		if (tokens.empty()) { throw std::runtime_error(std::string("invalid command - ") + cmd); };
		auto cmdIter = commandReg.find(tokens.at(0));
		if (cmdIter == commandReg.end()) { throw std::runtime_error(std::string("invalid command - ") + cmd); };
		ValueVecType params;
		std::transform(tokens.begin()+1, tokens.end(), std::back_inserter(params), [this](const std::string& s){
			return value(s);
		});
		commandQueue.emplace([params, func = cmdIter->second](){
			return func(params);
		});
	}

	ValueVecType eval() {
		ValueVecType results;
		while(!commandQueue.empty()) {
			results.emplace_back(commandQueue.front()());
			commandQueue.pop();
		}
		return results;
	}
	

	void regFunc(const std::string& op, OpFuncType f) {
		commandReg[op] = f;
	}

	ValueType value(const std::string& token) {

		try {
			size_t pos = 0;
			auto v = stol(token, &pos);
			if (pos == token.length()) return v; // Full convertion
		} catch (std::exception&) {} // try next type
		try {
			size_t pos = 0;
			auto v = stod(token, &pos);
			if (pos == token.length()) return v; // Full convertion
		} catch (std::exception&) {} // try next type

		return token;
	}
};

