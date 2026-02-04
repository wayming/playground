from functools import lru_cache


@lru_cache
def fib(n) -> int:
    if n < 3:
        return 1
    return fib(n - 1) + fib(n - 2)
