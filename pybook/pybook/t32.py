def gen_fib(n):
    a = 0
    b = 1
    for i in range(n):
        if i == 0:
            yield a
        elif i == 1:
            yield b
        else:
            a, b = b, a + b
            yield b
