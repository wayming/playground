#include <functional>
#include <vector>
#include <iostream>
#include <memory>
#include <map>
#include <type_traits>
#include <tuple>

class LogFormatter {
	template<typename T>
	constexpr char formatChar() {
		if constexpr (std::is_same_v<int, T>) {
			return 'd';
		}
		else if constexpr (std::is_same_v<long, T>) {
			return 'l';
		}
		else if constexpr (std::is_same_v<char, T>) {
			return 'c';
		}
		else if constexpr (std::is_convertible_v<std::string, T>) {
			return 's';
		}
		else if constexpr (std::is_same_v<float，T>) {
			return 'f';
		}
		else {
			return '\0';
		}
	}

public:
	template<typename T>
	void formatArg(std::ostream& os, char formatChar, T&& arg) {
		std::cout << "DEBUG: formatChar = " << formatChar
			<< ", typeid(T).name() = " << typeid(T).name()
			<< ", typeid(arg).name() = " << typeid(arg).name()
			<< std::endl;
		std::cout << "DEBUG: is_same_v<int, remove_reference_t<T>> = "
			<< std::is_same_v<int, std::remove_reference_t<T>> << std::endl;

		switch (formatChar) {
		case 'd':
			if constexpr (std::is_same_v<int, std::remove_reference_t<T>>) {
				os << static_cast<int>(arg);
			}
			else {
				throw std::invalid_argument("%d needs integer");
			}
			break;
		case 'f':
			if constexpr (std::is_same_v<float, std::remove_reference_t<T>>) {
				os << static_cast<float>(arg);
			}
			else {
				throw std::invalid_argument("%f needs float");
			}
			break;
		case 's':
			if constexpr (std::is_convertible_v<std::remove_reference_t<T>, std::string>) {
				os << arg;
			}
			else {
				throw std::invalid_argument("%s needs string");
			}
			break;
		default:
			throw std::invalid_argument("unknown format char");
		}

	}

	template<typename... Args>
	std::string format(const std::string& format, Args&&... args) {
		std::ostringstream ss;
		constexpr size_t argsCount = sizeof...(args);

		if constexpr (argsCount > 0) {
			std::tuple<Args&&...> argsTuple(std::forward<Args>(args)...);
			formatImp(ss, format, argsTuple, std::make_index_sequence<sizeof...(args)>{});
		}
		else {
			return format;
		}

		return ss.str();
	}

private:
	template<typename Tuple, size_t... Is>
	void formatImp(std::ostringstream& ss, const std::string& fmt, Tuple& args, std::index_sequence<Is...>) {
		size_t currPos = 0;
		size_t nextArgIdx = 0;
		constexpr size_t argsCount = std::tuple_size_v<std::remove_reference_t<Tuple>>;
		constexpr size_t indexCount = sizeof...(Is);
		if (argsCount != indexCount) {
			throw std::invalid_argument("unmatched number of format chars and parameters");
		}
		while (currPos < fmt.size()) {
			auto nextPercent = fmt.find('%', currPos);
			if (nextPercent == std::string::npos) {
				ss.write(fmt.data() + currPos, fmt.size() - currPos);
				break;
			}

			auto formatCharPos = nextPercent + 1;
			char formatChar = '\0';
			if (formatCharPos < fmt.size()) {
				formatChar = fmt.at(formatCharPos);
			}
			else {
				ss.write(fmt.data() + currPos, fmt.size() - currPos);
				break;
			}

			if (nextArgIdx >= argsCount) {
				throw std::invalid_argument("not enough number of parameters");
			}

			bool processed = false;
			((nextArgIdx == Is ? (formatArg(ss, formatChar, std::get<Is>(args)), processed = true) : false), ...);

			if (!processed) {
				throw std::invalid_argument("Invalid format char or argument");
			}

			nextArgIdx++;
			currPos = nextPercent + 2;
		}

		if (nextArgIdx != argsCount) {
			throw std::invalid_argument("too many parameters");
		}

	}
};

class Logger {
public:
	template<typename... Args>
	void log(const std::string& format, Args&&... args) {
		try {
			std::cout << formatter.format(format, std::forward<Args>(args)...);
			std::cout << std::endl;
		}
		catch (std::exception& e) {
			throw(e);
		}
	}
private:
	LogFormatter formatter;
};