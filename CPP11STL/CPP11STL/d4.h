#include <string>
#include <vector>
#include <algorithm>
class LogBuffer {
public:
	LogBuffer() = default;
	~LogBuffer() = default;
	LogBuffer(const LogBuffer& other) {
		std::cout << "Copy Construct" << std::endl;
		logLines = other.logLines;
	}
	LogBuffer(LogBuffer&& other) noexcept {
		std::cout << "Move Construct" << std::endl;
		logLines = std::move(other.logLines);
	}
	LogBuffer& operator=(const LogBuffer& other) {
		std::cout << "Copy Assign" << std::endl;
		if (this != &other) {
			logLines = other.logLines;
		}
		return *this;
	}
	LogBuffer& operator=(LogBuffer&& other) noexcept {
		std::cout << "Move Assign" << std::endl;
		if (this != &other) {
			logLines = std::move(other.logLines);
		}
		return *this;
	}
	const std::vector<std::string>& buffer() const { return logLines; }
	void add(const std::string& log) { logLines.emplace_back(log); }
	void merge(LogBuffer&& other) noexcept {
		std::cout << "Merge" << std::endl;
		logLines.insert(logLines.end(), std::make_move_iterator(other.buffer().begin()), std::make_move_iterator(other.buffer().end()));
	}
	void show() {
		for (auto& l : logLines) {
			std::cout << l << std::endl;
		}
	}
private:
	std::vector<std::string> logLines;
};