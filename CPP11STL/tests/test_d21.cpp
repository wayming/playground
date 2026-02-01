#include <gtest/gtest.h>
#include "../CPP11STL/d21.h"

TEST(StockDataParserTest, Tokens) {
	StockDataParser parser;
	auto tokens = parser.split("AAPL,20200101,100,nasdaq");
	for(auto& t : tokens) {
		std::cout << t << std::endl;
	}
	ASSERT_EQ(parser.split("AAPL,20200101,100,nasdaq").size(), 4);
	ASSERT_EQ(parser.split("AAPL,20200101,100,").size(), 4);
	ASSERT_EQ(parser.split(",").size(), 2);
	ASSERT_EQ(parser.split("AAPL").size(), 1);
}

TEST(StockDataParserTest, Sanity) {
	std::ofstream os("StockDataParserTest.csv", std::ofstream::trunc);
	os << "symbol,date,price,exchange" << std::endl;
	os << "AAPL,20200101,100,nasdaq" << std::endl;
	os << "AAPL,20200102,110,nasdaq" << std::endl;
	os << "AAPL,,120,nasdaq" << std::endl;
	os << "AAPL,20200104,111,nasdaq" << std::endl;
	os << "AAPL,20200105,188,nasdaq" << std::endl;
	os.close();
	StockDataParser p;
	p.parse("StockDataParserTest.csv");
	auto values = p.get("price");
	ASSERT_EQ(values.size(), 5);
	std::cout << "[ ";
	bool first = true;
	for (auto& v : values) {
		if (!first) {
			std::cout <<", ";
		} 

		first = false;
		std::cout << v;
	}
	std::cout << " ]";
	std::cout << std::endl;
}