#include <gtest/gtest.h>
#include "../CPP11STL/d25.h"

TEST(CSVToJsonConverterTest, SplitWithTrailingDelimiter) {
	std::vector<std::string> tokens = split("aa, bb,cc,");
	std::vector<std::string> expected = {"aa", " bb", "cc", ""};
	ASSERT_EQ(tokens.size(), 4);
	ASSERT_EQ(tokens, expected);
}

TEST(CSVToJsonConverterTest, SplitWithoutTrailingDelimiter) {
	std::vector<std::string> tokens = split("aa, bb,cc");
	std::vector<std::string> expected = {"aa", " bb", "cc"};
	ASSERT_EQ(tokens.size(), 3);
	ASSERT_EQ(tokens, expected);
}

TEST(CSVToJsonConverterTest, CSVInput) {
	const std::string csvText =
		"aa,bb,cc\n"
		"dd,ee,ff\n";
	std::stringstream ss(csvText);
	CSVInputIterator iter(ss);
	std::vector<std::string> expectedLine1 = {"aa", "bb", "cc"};
	std::vector<std::string> expectedLine2 = {"dd", "ee", "ff"};
	ASSERT_EQ(*iter, expectedLine1);
	ASSERT_EQ(*(++iter), expectedLine2);
}

TEST(CSVToJsonConverterTest, JSONOutput) {
	std::stringstream ss;
	JSONOutputIterator iter(ss, {"field1", "field2", "field3"});
	iter = {"aa", "bb", "cc"};
	std::cout << ss.str() << std::endl;
	ASSERT_EQ(ss.str(), R"RAW({"field1":"aa", "field2":"bb", "field3":"cc"})RAW");
	iter = {"dd", "ee", "ff"};
	std::cout << ss.str() << std::endl;
	ASSERT_EQ(ss.str(), R"RAW({"field1":"aa", "field2":"bb", "field3":"cc"}, {"field1":"dd", "field2":"ee", "field3":"ff"})RAW");
}