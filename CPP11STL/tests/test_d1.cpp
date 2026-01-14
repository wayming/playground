#include <gtest/gtest.h>
#include "../CPP11STL/d1.h"

TEST(SeqGeneratorTest, Sanity) {
	SeqGenerator gen(5, 10);
	auto seq = gen.genIntegerSeq();
	ASSERT_EQ(seq.size(), 10);

	for (auto& x : gen.genIntegerSeq()) {
		std::cerr << x << ",";
	}
	std::cerr << std::endl;

	for (auto& x : gen.genSquareSeq()) {
		std::cerr << x << ",";
	}
	std::cerr << std::endl;

	for (auto& x : gen.genStringSeq("item")) {
		std::cerr << x << ",";
	}
	std::cerr << std::endl;

}