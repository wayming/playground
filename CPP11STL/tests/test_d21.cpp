#include <gtest/gtest.h>
#include "../CPP11STL/d21.h"

TEST(StockDataParserTest, Sanity) {
	std::ofstream os("StockDataParserTest.csv", std::ofstream::trunc);
	os << "symbol,date,price,exchange" << std::endl;
	os << "AAPL,20200101,100,nasdaq" << std::endl;
	os << "AAPL,20200102,110,nasdaq" << std::endl;
	os << "AAPL,20200103,120,nasdaq" << std::endl;
	os << "AAPL,20200104,111,nasdaq" << std::endl;
	os << "AAPL,20200105,188,nasdaq" << std::endl;
	os.close();
	StockDataParser p;
	p.parse("StockDataParserTest.csv", "price");
	p.parse("StockDataParserTest.csv", "date");
}