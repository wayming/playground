#include <gtest/gtest.h>
#include "../CPP11STL/d8.h"

TEST(EventHub, Sanity) {
	EventHub hub;
	Worker w1("worker1");
	Worker w2("worker2");
	Worker w3("worker3");
	Worker w4("worker4");

	hub.subscribe(&Worker::fire, &w1);
	hub.subscribe(&Worker::fire, &w2);
	hub.subscribe(&Worker::fire, &w3);
	hub.subscribe(&Worker::fire, &w4);

	hub.publish("start");
	hub.publish("stop");

}