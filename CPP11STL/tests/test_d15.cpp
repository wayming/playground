#include <gtest/gtest.h>
#include "../CPP11STL/d15.h"
#include <iostream>
#include <sstream>

TEST(ConfigReaderTest, Trim) {
	// ASSERT_EQ(trim("  abcd    "), "abcd");
	// ASSERT_EQ(trim("  ab cd    "), "ab cd");
	std::string str("  abcd    ");
	trim(str);
	ASSERT_EQ(str, "abcd");

	str = std::string("  ab cd    ");
	trim(str);
	ASSERT_EQ(str, "ab cd");
}

TEST(ConfigReaderTest, Parser) {

	std::ofstream fs("config1.txt");
	if (fs.is_open()) {
		fs << R"(
[network]
host = 127.0.0.1
port = 8080

[database]
user = root
password = secret
timeout = 30)" << std::endl;
	}

	ConfigReader r;
	r.parse("config1.txt");
	r.dump();

	ASSERT_EQ(r["network"].at("host"), "127.0.0.1");
	ASSERT_EQ(r["database"].at("password"), "secret");
}