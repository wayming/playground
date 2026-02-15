import collections
import datetime
import heapq


class StockAgg:
    def __init__(self, window):
        self.data = collections.deque()
        self.window = window
        self.minh = []
        self.maxh = []
        self.curr_sum = 0
        self.minq = collections.deque()
        self.maxq = collections.deque()

    def push(self, t: datetime.datetime, p: int):
        self.data.append((p, t))
        self.curr_sum += p
        heapq.heappush(self.minh, (p, t))
        heapq.heappush(self.maxh, (p * -1, t))

        while self.minq and self.minq[-1][0] >= p:
            self.minq.pop()
        self.minq.append((p, t))

        while self.maxq and self.maxq[-1][0] <= p:
            self.maxq.pop()
        self.maxq.append((p, t))

        self.house_keeping()

    def house_keeping(self):
        cutoff = datetime.datetime.now() - datetime.timedelta(seconds=self.window)
        self.pop_till(self.data, cutoff, True)
        self.pop_till(self.minq, cutoff)
        self.pop_till(self.maxq, cutoff)

    def pop_till(
        self, q: collections.deque, cutoff: datetime.datetime, sum: bool = False
    ):
        while q:
            if q[0][1] < cutoff:
                p, t = q.popleft()
                print("pop", p, "at", t)
                if sum:
                    self.curr_sum -= p
            else:
                break

    def avg(self):
        self.house_keeping()
        if len(self.data) == 0:
            return None

        return self.curr_sum / len(self.data)

    def high(self):
        cutoff = datetime.datetime.now() - datetime.timedelta(seconds=self.window)
        while self.maxh:
            p, t = self.maxh[0]
            if t >= cutoff:
                return p * -1
            else:
                heapq.heappop(self.maxh)
        return None

    def low(self):
        cutoff = datetime.datetime.now() - datetime.timedelta(seconds=self.window)
        print("low cutoff", cutoff)
        while self.minh:
            p, t = self.minh[0]
            if t >= cutoff:
                return p
            else:
                heapq.heappop(self.minh)
        return None

    def high_O1(self):
        cutoff = datetime.datetime.now() - datetime.timedelta(seconds=self.window)
        self.pop_till(self.maxq, cutoff)

        return self.maxq[0][0] if self.maxq else None

    def low_O1(self):
        cutoff = datetime.datetime.now() - datetime.timedelta(seconds=self.window)
        self.pop_till(self.minq, cutoff)

        return self.minq[0][0] if self.minq else None
