#include <gtest/gtest.h>
#include "../CPP11STL/d12.h"

TEST(CommandRunnerTest, Split) {
	auto v1 = split("ADD a b");
	ASSERT_EQ(v1.size(), 3);
	ASSERT_STREQ(v1.at(0).c_str(), "ADD");
	ASSERT_STREQ(v1.at(1).c_str(), "a");
	ASSERT_STREQ(v1.at(2).c_str(), "b");

	v1 = split("  ADD  a ");
	ASSERT_EQ(v1.size(), 2);
	ASSERT_STREQ(v1.at(0).c_str(), "ADD");
	ASSERT_STREQ(v1.at(1).c_str(), "a");

	v1 = splitRe("ADD a b");
	ASSERT_EQ(v1.size(), 3);
	ASSERT_STREQ(v1.at(0).c_str(), "ADD");
	ASSERT_STREQ(v1.at(1).c_str(), "a");
	ASSERT_STREQ(v1.at(2).c_str(), "b");

	v1 = splitRe("  ADD  a ");
	ASSERT_EQ(v1.size(), 2);
	ASSERT_STREQ(v1.at(0).c_str(), "ADD");
	ASSERT_STREQ(v1.at(1).c_str(), "a");
}
TEST(CommandRunnerTest, Sanity) {
	CommandParser parser;
	parser.addCommand("ADD 3 5");
	parser.addCommand("MULT 3 5");
	parser.addCommand("ECHO TESTSTRING");
	parser.dump();
	parser.eval();
}