#include <gtest/gtest.h>
#include "../CPP11STL/d11.h"

TEST(TextProcessPipeLine, Sanity) {
	TextProcessPipeLine pipeline;
	pipeline.addProcessor(trim).addProcessor(removePunct).addProcessor(toLower);
	pipeline.addProcessor([](const std::string& input) {
		std::regex r("\\b(test)\\b");
		return regexReplace(input, r, "production");
	});

	ASSERT_STREQ(pipeline.run("  THIS ,is a test %%program%%   ").c_str(), "this is a production program");
}