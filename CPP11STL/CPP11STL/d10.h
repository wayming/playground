#include <deque>
#include <tuple>
#include <chrono>
#include <numeric>
#include <algorithm>
#include <optional>

template<typename T, std::size_t... Is>
void tuple_print_imp(T&& tup, std::index_sequence<Is...>) {
	std::cout << "(";
	((std::cout << (Is == 0 ? "" : ", ") << std::get<Is>(tup)), ...);
	std::cout << ")" << std::endl;
}
template<typename... Args>
void tuple_print_left_ref(std::tuple<Args...>& tup) {
	tuple_print_imp(tup, std::make_index_sequence<sizeof...(Args)>{});
}

template<typename... Args>
void tuple_print_right_ref(std::tuple<Args...>&& tup) {
	tuple_print_imp(std::forward<std::tuple<Args...>>(tup),
	std::make_index_sequence<sizeof...(Args)>{});
}

template<typename T>
void tuple_print(T&& tup) {
	using TupleType = std::remove_reference_t<T>;
	constexpr auto size = std::tuple_size_v<T>;
	tuple_print_imp(std::forward<TupleType>(tup),
	std::make_index_sequence<size>{});
}