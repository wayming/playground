
#include <gtest/gtest.h>
#include "../CPP11STL/d26.h"

TEST(FunctionPipeTest, Sanity) {
	Pipe p;
	p | filter([](int x) { return x % 2 == 0; })
		| transform([](int x) { return x * x; })
		| take(3);
	p({ 1,2,3,4,5,6 });
	std::cout << "hello" << std::endl;

	// 使用 GTEST_LOG_
	GTEST_LOG_(INFO) << "hello";

	// 或者使用 SCOPED_TRACE
	SCOPED_TRACE("Test message: hello");
}

TEST(FunctionPipeTest, MultipleFilters) {
	Pipe p;
	p | filter([](int x) { return x < 5; })
		| filter([](int x) { return x > 3; })
		| transform([](int x) { return x * x; });
	p({ 1,2,3,4,5,6 });

}
