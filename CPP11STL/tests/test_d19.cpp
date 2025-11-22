#include <gtest/gtest.h>
#include "../CPP11STL/d19.h"
#include <iostream>
#include <sstream>
#include <chrono>
#include <ctime>
#include <thread>
#include <vector>
#include "stdlib.h"


TEST(LRUTest, Sanity) {
	LRUCache<int, std::string> lru(3);

	lru.put(1, "A");
	lru.put(2, "B");
	lru.put(3, "C");

	lru.print();   // (3,C) (2,B) (1,A)

	ASSERT_EQ(lru.get(1), "A");     // 访问 1，使其变为 MRU
	lru.print();    // (1,A) (3,C) (2,B)

	lru.put(4, "D"); // 淘汰 key=2
	lru.print();     // (4,D) (1,A) (3,C)
}