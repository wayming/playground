import concurrent.futures


def t81_squre(x):
    return x * x


def t81_square_sum_mp(np: int, r: int):
    with concurrent.futures.ProcessPoolExecutor(np) as exectuor:
        return sum(exectuor.map(t81_squre, range(r)))
