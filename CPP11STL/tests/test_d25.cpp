#include <gtest/gtest.h>
#include "../CPP11STL/d25.h"

TEST(CVSToJsonConverterTest, Sanity) {
	std::vector<std::string> tokens = split("aa, bb,cc,");
	std::vector<std::string> expected = {"aa", " bb", "cc", ""};
	ASSERT_EQ(tokens.size(), 4);
	ASSERT_EQ(tokens, expected);
}