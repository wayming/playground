#include <map>
#include <regex>
#include <functional>
#include <vector>
#include <sstream>
#include <deque>
#include <tuple>
#include <variant>
#include <regex>

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
	using OpFuncType = std::function<void(const std::vector<ValueType>&)>;
	std::unordered_map<std::string, OpFuncType> commandReg;
public:
	CommandParser() {
		regFunc("ADD", [](const std::vector<ValueType>& params) -> ValueType {
			if(params.size() != 2) throw std::runtime_error("Invalid number of parameters for ADD op");
			if (std::holds_alternative<std::string>(params[0]) &&
				std::holds_alternative<std::string>(params[1])) {
					return std::get<std::string>(params[0]) + std::get<std::string>(params[1]);
			}
			else if (std::holds_alternative<long>(params[0]) &&
				std::holds_alternative<long>(params[1])) {
					return std::get<long>(params[0]) + std::get<long>(params[1]);
			}
			else if (std::holds_alternative<double>(params[0]) &&
				std::holds_alternative<double>(params[1])) {
					return std::get<double>(params[0]) + std::get<double>(params[1]);
			} else {
				throw std::runtime_error("Invalid types of operands.");
			}
		});
	}

	void addCommand(const std::string& cmd) {

	}

	void dump() {
	}

	void eval() {
	}

	void regFunc(const std::string& op, OpFuncType f) {
		commandReg[op] = f;
	}
};

