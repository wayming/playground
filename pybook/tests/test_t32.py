import pybook.t32 as t


def test_gen_fib():
    for i in t.gen_fib(10):
        print(i)
