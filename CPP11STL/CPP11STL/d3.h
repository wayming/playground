#include <array>
#include <unordered_map>
#include <memory>
#include <iostream>
#include <exception>
class IDGen {
public:
	static IDGen& Instance() {
		static IDGen gen;
		return gen;
	}
	size_t Next() {
		return next++;
	}
private:
	IDGen() = default;
	~IDGen() = default;
	IDGen(const IDGen&) = delete;
	IDGen(IDGen&&) = delete;
	IDGen& operator=(const IDGen&) = delete;
	IDGen& operator=(IDGen&&) = delete;
	size_t next = {0};
};

class Resource {
public:
	Resource(size_t n) {
		id = n;
		std::cout << "Resource " << id << " created." << std::endl;
	}
	~Resource() {
		data.fill('\0');
		std::cout << "Resource " << id << " cleared." << std::endl;
	}
	size_t Id() const { return id; }
	void Set(const std::string& str) {
		if (str.size() > 1024) {
			throw std::runtime_error("Input string is too large");
		}
		size_t idx = 0;
		for (auto& c : str) data[idx++] = c;
	}
	std::string Get() {
		return std::string(data.begin(), std::find(data.begin(), data.end(), '\0'));
	}
private:
	size_t id;
	std::array<char, 1024> data = {};
};

class ResourcePool {
public:
	ResourcePool(size_t len) {
		for (int i = 0; i < len; ++i) {
			dataMap.emplace(i, std::make_shared<Resource>(i));
		}
	}
	void Destroy() {
		dataMap.clear();
	}
	std::shared_ptr<Resource>& AcquireResource(size_t id) {
		try {
			return dataMap.at(id);
		}
		catch (std::exception&) {
			std::cerr << "No element for id " << id << std::endl;
			throw;
		}
	}

private:
	std::unordered_map<size_t, std::shared_ptr<Resource>> dataMap;
};