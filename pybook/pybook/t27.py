def distinct(a: set, b: set):
    return a ^ b


def a_only(a: set, b: set):
    return a - b


def common(a: set, b: set):
    return a & b
