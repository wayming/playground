#include <gtest/gtest.h>
#include "../CPP11STL/d18.h"
#include <iostream>
#include <sstream>
#include <chrono>
#include <ctime>
#include <thread>
#include <vector>
#include "stdlib.h"


TEST(SubjectObserverTest, Sanity) {
	Subject s;
	auto ob1 = std::make_shared<ReversePrinterObserver>();
	auto ob2 = std::make_shared<TimeObserver>();
	{
		auto ob3 = std::make_shared<ReversePrinterObserver>();
		auto ob4 = std::make_shared<TimeObserver>();
		s.add(ob1);
		s.add(ob2);
		s.add(ob3);
		s.add(ob4);

		s.notify("in scope");
	}

	s.notify("out scope");
}