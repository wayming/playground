#include <array>
#include <unordered_map>
#include <memory>
#include <iostream>
#include <exception>
#include <algorithm>

class Resource {
	std::array<char, 1024> data;
	size_t len = 0;
	int id = 0;

public:
	Resource(int id): id(id) { std::cerr << "Resource " << id << " Allocated" << std::endl; }
	~Resource() { std::cerr << "Resource " << id << " Destoried" << std::endl; }
	void fill(const std::string& text) {
		if (len + text.size() > 1024) {
			throw std::runtime_error("Not enough space");
		}
		std::copy(text.begin(), text.end(), data.begin() + len);
		len += text.length();
	}
	std::string asString() { return std::string(data.data(), len); }
};


class ResourcePool {
	std::unordered_map<int, std::shared_ptr<Resource>> resources;
public:
	std::shared_ptr<Resource> acquireResource(int id) {
		auto res = resources.find(id);
		if (res == resources.end()) {
			// Add new resoure
			resources.emplace(id, std::make_shared<Resource>(id));
			return resources.at(id);
		} else {
			return resources.at(id);
		}
	}

	void destroy(){
		resources.clear();
	}
};