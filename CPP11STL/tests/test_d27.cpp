
#include <gtest/gtest.h>
#include "../CPP11STL/d27.h"
#include <sstream>

TEST(SerializeFramework, UtilInteger) {
	std::stringstream ss;
	int n = 100;
	SerializeFramework::SerializeUtil::write<int>(ss, n);
	int m = SerializeFramework::SerializeUtil::read<int>(ss);
	ASSERT_EQ(n, m);
}

TEST(SerializeFramework, UtilString) {
	std::stringstream ss;
	std::string inStr("this is a test string");
	SerializeFramework::SerializeUtil::write<std::string>(ss, inStr);
	std::string ouStr = SerializeFramework::SerializeUtil::read<std::string>(ss);
	ASSERT_EQ(inStr, ouStr);
}

TEST(SerializeFramework, SerializeInOut) {
	SerializeFramework::Serializer s;
	SerializeFramework::LoginMessage inMsg("user1", "pass1");
	std::stringstream ss;

	s.in(inMsg, ss);
	auto ouMsg = s.out(ss);
	auto loginMsgPtr = dynamic_cast<SerializeFramework::LoginMessage*>(ouMsg.get());
	ASSERT_STREQ(inMsg.User().c_str(), loginMsgPtr->User().c_str());
	ASSERT_STREQ(inMsg.Pass().c_str(), loginMsgPtr->Pass().c_str());

}