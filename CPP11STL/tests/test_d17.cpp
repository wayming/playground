#include <gtest/gtest.h>
#include "../CPP11STL/d17.h"
#include <iostream>
#include <sstream>
#include <chrono>
#include <ctime>
#include <thread>
#include <vector>
#include "stdlib.h"


TEST(MatrixTest, Construct) {
	Matrix<3, 5, int> m = {
		{1},
		{2, 3, 4, 5, 6},
		{1, 1, 1, 1, 1, 1, 1}
	};
	m.print();
}

TEST(MatrixTest, Plus) {
	Matrix<3, 5, int> m = {
		{1},
		{2, 3, 4, 5, 6},
		{1, 1, 1, 1, 1, 1, 1}
	};

	Matrix<3, 5, int> m2 = m + m; // Direct construct result at m2 directly, no move or copy

	m2.print();
}

TEST(MatrixTest, multiply) {
	Matrix<3, 5, int> m = {
		{1},
		{2, 3, 4, 5, 6},
		{1, 1, 1, 1, 1, 1, 1}
	};

	auto m2 = m * 5;
	m2.print();
}