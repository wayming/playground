#include <gtest/gtest.h>
#include "../CPP11STL/d11.h"

TEST(JsonBuilderTest, Sanity) {
	JsonFormater f;

	JsonObject a;
	a["name"] = "alice";
	a["age"] = 20;
	a["skills"] = JsonArray({ "c++", "python" });
	//a.print();

	JsonObject b;
	b["name"] = "john";
	b["age"] = 30;
	b["skills"] = JsonArray({ "Java", "JS" });
	//b.print();

	JsonObject c;
	c["department"] = "R&D";
	c["skillsregister"] = JsonArray({ std::move(a), std::move(b) });
	
	std::cout << f.prettyJson(c) << std::endl;

}