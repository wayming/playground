#include <gtest/gtest.h>
#include "../CPP11STL/d8.h"

TEST(EventHub, Sanity) {
	EventHub hub;

	Logger l;
	l.SetLevel(LOG_LEVEL::DEBUG);
	hub.subscribe([&l](const std::string& message) {
		l.Log(LOG_LEVEL::DEBUG, message);
	});

	hub.subscribe([](const std::string& message){
		std::cout << message << std::endl;
	});

	hub.publish("this is a test string");
}