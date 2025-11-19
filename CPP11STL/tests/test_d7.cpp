#include <gtest/gtest.h>
#include "../CPP11STL/d7.h"
#include <fstream>

TEST(SearchString, Sanity) {
	std::vector<std::string> files = { "a1.txt", "a2.txt", "a3.txt", "a4.txt" };
	for (auto& f : files) {
		std::ofstream fs(f, std::iostream::out);
		if (fs.is_open()) {
			fs << "this is a test string for file " << f << std::endl;
		}
	}
	run(files, std::string("is"));
}