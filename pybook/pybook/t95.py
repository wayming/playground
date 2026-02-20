import random


class MyIter:
    def __init__(self, n):
        self.data = [random.Random().randint(100, 1000) for _ in range(n)]
        self.pos = 0
        pass

    def __iter__(self):
        return self

    def __next__(self):
        if self.pos == len(self.data):
            raise StopIteration

        v = self.data[self.pos]
        self.pos += 1
        return v
