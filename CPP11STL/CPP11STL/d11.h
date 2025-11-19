#include <map>
#include <string>
#include <vector>
#include <variant>
#include <memory>
#include <iostream>
#include <algorithm>
#include <typeinfo>

struct JsonValue;
struct JsonArray;
class JsonObject;
class JsonFormater;

constexpr char SPACE = ' ';

using JsonValueType = std::variant<
	std::monostate,
	int,
	std::string,
	JsonArray,
	JsonObject>;

class JsonObject :public std::map<std::string, JsonValue> {
public:
	JsonObject() = default;
	JsonObject(std::initializer_list<std::pair<const std::string, JsonValue>> init) : std::map<std::string, JsonValue>(init) {}
};

//struct JsonArray {
//	std::vector<JsonValue> elements;
//
//	JsonArray(std::initializer_list<JsonValue> init) : elements(init) {}
//};

struct JsonArray : std::vector<JsonValue>{
	using std::vector<JsonValue>::vector;

	// JsonArray(std::initializer_list<JsonValue> init) : std::vector<JsonValue>(init) {}
};

struct JsonValue {
	JsonValueType value;
	JsonValue() = default;
	~JsonValue() = default;
	JsonValue(const JsonValue& other) : value(other.value) {}
	JsonValue(JsonValue&& other) noexcept : value(std::move(other.value)) {}
	JsonValue& operator=(const JsonValue& other) {
		if (&other != this) {
			value = other.value;
		}
		return *this;
	}
	JsonValue& operator=(JsonValue&& other) {
		if (&other != this) {
			value = std::move(other.value);
		}
		return *this;
	}

	//JsonValue(std::initializer_list<JsonValue> v) : value(JsonArray(v)) {}

	JsonValue(const int v) : value(v) {}
	JsonValue(const char* v) : value(std::string(v)) {}
	JsonValue(const std::string& v) : value(v) {}
	JsonValue(JsonArray&& v) : value(std::move(v)) {}
	JsonValue(JsonObject&& v) : value(std::move(v)) {}


};

class JsonFormater {
public:
	JsonFormater(int indent = 2):indentSize(indent) {}
	void printIndent(int level) {
		ss << std::string(level * indentSize, SPACE);
	}
	std::string prettyJson(const JsonObject& json, int level = 0) {
		printIndent(level);
		ss << "{\n";
		for (auto it = json.begin(); it != json.end();) {
			printIndent(level+1);
			ss << '"' << it->first << '"' << ":";
			printJsonValue(it->second, level + 1);
			if (++it != json.end()) ss << ',' << '\n';
		}
		printIndent(level);
		ss << '}';
		return ss.str();
	}

	void printJsonValue(const JsonValue& val, int level) {


		if (std::holds_alternative<std::monostate>(val.value)) {
			ss << "NULL";
		}
		else if (std::holds_alternative<int>(val.value)) {
			ss << std::get<int>(val.value);
		}
		else if (std::holds_alternative<std::string>(val.value)) {
			ss << '"' << std::get<std::string>(val.value) << '"';
		}
		else if (std::holds_alternative<JsonArray>(val.value)) {
			auto& value = std::get<JsonArray>(val.value);
			ss << "[\n";
			for (size_t idx = 0; idx < value.size(); ++idx) {
				//std::visit([this, level](const auto& value) {
				//	using T2 = std::decay_t<decltype(value)>;
				//	if constexpr (!std::is_same_v < T2, JsonObject) printIndent(level+1);
				//}, value.elements[idx]);
				const JsonValue& elem = value[idx];
				if (!std::holds_alternative<JsonObject>(elem.value)) {
					printIndent(level + 1);
				}
				printJsonValue(value[idx], level + 1);
				if (idx < value.size() - 1) {
					ss << ',';
				}
				ss << '\n';
			}
			printIndent(level);
			ss << ']';
			ss << '\n';
		}
		else if (std::holds_alternative<JsonObject>(val.value)) {
			auto& value = std::get<JsonObject>(val.value);
			prettyJson(value, level);
		}

	}

	//void printJsonValue(const JsonValue& val, int level) {
	//	std::visit([this, level](const auto& value) {
	//		using T = std::decay_t<decltype(value)>;

	//		if constexpr (std::is_same_v<T, std::monostate>) {
	//			ss << "NULL";
	//		}
	//		else if constexpr (std::is_same_v<T, int>) {
	//			ss << value;
	//		}
	//		else if constexpr (std::is_same_v<T, std::string>) {
	//			ss << '"' << value << '"';
	//		}
	//		else if constexpr (std::is_same_v<T, JsonArray>) {
	//			ss << "[\n";
	//			for (size_t idx = 0; idx < value.elements.size(); ++idx) {
	//				//std::visit([this, level](const auto& value) {
	//				//	using T2 = std::decay_t<decltype(value)>;
	//				//	if constexpr (!std::is_same_v < T2, JsonObject) printIndent(level+1);
	//				//}, value.elements[idx]);
	//				const JsonValue& elem = value.elements[idx];
	//				if (!std::holds_alternative<JsonObject>(elem.value)) {
	//					printIndent(level + 1);
	//				}
	//				printJsonValue(value.elements[idx], level + 1);
	//				if (idx < value.elements.size() - 1) {
	//					ss << ',';
	//				}
	//				ss << '\n';
	//			}
	//			printIndent(level);
	//			ss << ']';
	//			ss << '\n';
	//		}
	//		else if constexpr (std::is_same_v < T, JsonObject>) {
	//			prettyJson(value, level);
	//		}
	//		}, val.value);
	//}

private:
	std::stringstream ss;
	int indentSize = 2;
};
