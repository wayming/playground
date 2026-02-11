import collections


def first_distinct(s: str):
    count = collections.Counter(s)
    for k, v in count.items():
        if v == 1:
            return k
