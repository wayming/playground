
#include <gtest/gtest.h>
#include "../CPP11STL/d29.h"
#include <sstream>

TEST(LogFormatterTest, Sanity) {
	std::stringstream ss;
	LogFormatter formater;
	formater.formatArg(ss, 'd', 5);
	ASSERT_STREQ("5", ss.str().c_str());
}

TEST(LogFormatterTest, String) {
	std::stringstream ss;
	LogFormatter formater;
	formater.formatArg(ss, 's', "user1");
	ASSERT_STREQ("user1", ss.str().c_str());
}


TEST(LogFormatterTest, InvalidType) {
	std::stringstream ss;
	LogFormatter formater;
	ASSERT_THROW(formater.formatArg(ss, 'd', "abc"), std::invalid_argument);
}

TEST(LoggerTest, Sanity) {
	Logger logger;
	logger.log("Hello %s, number %d, credit %f", "user1", 101, 100.5f);
}