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
	auto ob1 = std::make_shared<SimplePrinterObserver>();
	auto ob2 = std::make_shared<TimeObserver>();
	{
		auto ob3 = std::make_shared<SimplePrinterObserver>();
		auto ob4 = std::make_shared<TimeObserver>();
		s.registObserver(ob1);
		s.registObserver(ob2);
		s.registObserver(ob3);
		s.registObserver(ob4);

		s.notify("in scope");
	}

	s.notify("out scope");
}