#include <gtest/gtest.h>
#include "../CPP11STL/d23.h"
#include <thread>
#include <filesystem>

using LogFuture = std::future<std::chrono::steady_clock::duration>;

class RotateLoggerTest : public ::testing::Test {
protected:
	void SetUp() override {
		std::error_code ec;
		std::cout << "RotateLoggerTest SetUp" << std::endl;
		for (auto& file : std::filesystem::directory_iterator(".")) {
			if (file.path().filename().string().find("d23SingleUser.log") != std::string::npos) {
				std::cout << "delete " << file.path().filename() << std::endl;
				std::filesystem::remove(file.path(), ec);
			}
		}
	}
};
TEST_F(RotateLoggerTest, SingleUser) {
	{
		RotateLogger logger("d23SingleUser.log", 100);
		std::vector<LogFuture> futures;
		for (int i = 0; i < 10; ++i) {
			auto thisFutures = logger.log({
				"this is the 1st message",
				"this is the 2nd message",
				"this is the 3rd message",
			});

			std::move(thisFutures.begin(), thisFutures.end(), std::back_inserter(futures));
		}

		for (auto& f : futures) {
			auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(f.get());
			std::cout << "log message in " << ms.count() << "ms" << std::endl;
		}
	}


	std::vector<std::string> files;
	for (auto& file : std::filesystem::directory_iterator(".")) {
		if (file.path().filename().string().find("d23SingleUser.log") != std::string::npos) {
			files.push_back(file.path().filename().string());
		}
	}
	for (auto& f: files) std::cout << f << std::endl;
	ASSERT_EQ(files.size(), 6);
}


TEST_F(RotateLoggerTest, MultipleUsers) {
	{
		RotateLogger logger("d23MultipleUsers.log", 100);
		std::vector<std::thread> threads;
		for (int i = 0; i < 10; ++i) {
			threads.emplace_back([&logger]() {
				for (int j = 0; j < 10; ++j) {
					auto futures = logger.log({
						"this is the 1st message",
						"this is the 2nd message",
						"this is the 3rd message",
					});
					for (auto& f : futures) {
						auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(f.get());
						std::cout << "log message in " << ms.count() << "ms" << std::endl;
					}
				}
			});
		}

		for (auto& t : threads) {
			t.join();
		}
	}

	std::vector<std::string> files;
	for (auto& file : std::filesystem::directory_iterator(".")) {
		if (file.path().filename().string().find("d23MultipleUsers.log") != std::string::npos) {
			files.push_back(file.path().filename().string());
		}
	}
	for (auto& f: files) std::cout << f << std::endl;
	ASSERT_EQ(files.size(), 6);
}