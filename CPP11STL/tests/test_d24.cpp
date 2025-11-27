#include <gtest/gtest.h>
#include "../CPP11STL/d24.h"

TEST(TempalteRenderTest, Sanity) {
	std::string tpl("this ${param1} is a ${param2} with $$ in side.");
	ASSERT_EQ(std::string("this item is a test with $ in side."),
		renderTemplate(tpl, {{"param1", "item"}, {"param2", "test"}}));
}