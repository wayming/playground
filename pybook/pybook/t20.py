class Countdown:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return self

    def __next__(self):
        v = self.n
        if v < 0:
            raise StopIteration
        self.n -= 1
        return v
