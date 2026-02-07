import functools
import random


def repeat(n):
    def dector(func):
        @functools.wraps(func)  # 用func的属性替换wrapfun的属性
        def wfunc(*args, **kwargs):
            results = []
            for _ in range(n):
                results.append(func(*args, **kwargs))
            return results

        return wfunc

    return dector


@repeat(10)
def myrand(text):
    return text + str(random.randrange(100))
