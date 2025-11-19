#include <string>
#include <vector>
#include <algorithm>
class LogBuffer {
public:
	LogBuffer() = default;
	LogBuffer(const LogBuffer&) = delete;
	LogBuffer& operator=(LogBuffer& other) = delete;
	LogBuffer(LogBuffer&& other) {
		if (this != &other) {
			this->buffer = std::move(other.buffer);
		}
	}
	LogBuffer& operator=(LogBuffer&& other) {
		if (this != &other) {
			this->buffer = std::move(other.buffer);
		}
		return *this;
	}

	void addLog(const std::string& log) {
		buffer.emplace_back(std::move(log));
	}
	std::vector<std::string>& getBuffer() { return buffer; }
	void merge(LogBuffer&& other) {
		buffer.reserve(buffer.size() + other.getBuffer().size());
		for (auto&& x : other.getBuffer()) buffer.emplace_back(std::move(x));

		// More effecient
		// std::move(other.getBuffer().begin(), other.getBuffer().end(), buffer.end());
	}

	void show() {
		for (auto& x : buffer) std::cout << x << std::endl;
	}
private:
	std::vector<std::string> buffer;
};