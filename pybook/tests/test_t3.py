import pybook.t3 as t


def test_fib():
    assert t.fib(1) == 1
    assert t.fib(2) == 1
    assert t.fib(3) == 2
    assert t.fib(10) == 55
