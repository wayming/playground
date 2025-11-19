#include <gtest/gtest.h>
#include "../CPP11STL/d12.h"

TEST(CommandRunnerTest, Sanity) {
	CommandParser parser;
	parser.addCommand("ADD 3 5");
	parser.addCommand("MULT 3 5");
	parser.addCommand("ECHO TESTSTRING");
	parser.dump();
	parser.eval();
}