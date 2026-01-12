#include <functional>
#include <vector>
#include <iostream>


struct OP {
	enum class OPTYPE { FILTER, TRANSFORM, TAKE } opType;
	std::function<bool(int&)> filter;
	std::function<int(int&)> transform;
	size_t take;

	static OP makeFilter(std::function<bool(int&)> f) { return OP{ OPTYPE::FILTER, std::move(f), {}, SIZE_MAX }; }
	static OP makeTranform(std::function<int(int&)> f) { return OP{ OPTYPE::TRANSFORM, {}, std::move(f), SIZE_MAX }; }
	static OP makeTake(size_t s) { return OP{ OPTYPE::TAKE, {}, {}, s }; }
};

template <typename T>
OP filter(T&& f) { return OP::makeFilter(std::forward<T>(f)); }
template <typename T>
OP transform(T&& f) { return OP::makeTranform(std::forward<T>(f)); }
OP take(size_t t) { return OP::makeTake(t); }

class Pipe {
public:
	Pipe() = default;
	Pipe(OP&& operation) {
		ops.emplace_back(std::move(operation));
	}

	Pipe& operator|(OP&& operation) {
		ops.emplace_back(std::move(operation));
		return *this;
	}

	std::vector<int> operator()(std::vector<int>&& src) {
		std::vector<int> results = std::move(src);
		for (auto& op : ops) {
			std::cout << "perform op " << static_cast<int>(op.opType) << std::endl;
		}
		return results;
	}
private:
	std::vector<OP> ops;
};


