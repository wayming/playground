#include <gtest/gtest.h>
#include "../CPP11STL/d23.h"
#include <thread>
#include <filesystem>

TEST(RotateLoggerTest, SingleUser) {
	RotateLogger logger("d23.log", 10);
	for (int i = 0; i < 100; ++i) {
		logger.log({
			"this is the 1st message",
			"this is the 2nd message",
			"this is the 3rd message",
		});
	}

	std::vector<std::string> files;
	for (auto& file : std::filesystem::directory_iterator(".")) {
		if (file.path().filename().string().find("d23.log") != std::string::npos) {
			files.push_back(file.path().filename().string());
		}
	}
	for (auto& f: files) std::cout << f << std::endl;
	ASSERT_EQ(files.size(), 5);
}