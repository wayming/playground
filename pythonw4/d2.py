import datetime
import random
from collections import deque
import heapq
class StockPriceAggregator:
    def __init__(self):
        self.data = {}    
    
    def update(self, symbol, price, timestamp, window=60):
        if symbol not in self.data:
            self.data[symbol] = deque()
        
        self.data[symbol].append((timestamp, price))
        cut_off_time = datetime.datetime.now() - datetime.timedelta(seconds=window)
        while self.data[symbol] and self.data[symbol][0][0] < cut_off_time:
            print("pop old")
            self.data[symbol].popleft()
                
    def get_avg(self, symbol, window=60):
        prices_in_window = self._prices_in_window(symbol, window)
        return sum(prices_in_window) / len(prices_in_window)
    
    def get_high(self, symbol, window=60):
        neg_prices_in_window = [-x for x in self._prices_in_window(symbol, window)]
        heapq.heapify(neg_prices_in_window)
        return -1 * heapq.heappop(neg_prices_in_window)
    
    def get_low(self, symbol, window=60):
        prices_in_window = self._prices_in_window(symbol, window)
        heapq.heapify(prices_in_window)
        return heapq.heappop(prices_in_window)
     
    def _prices_in_window(self, symbol, window=60):
        if symbol not in self.data or not self.data[symbol]:
            raise ValueError(f"price for {symbol} not found")
        
        now = datetime.datetime.now()
        prices_in_window = [p for t, p in self.data[symbol] if t <= now and now - t <= datetime.timedelta(seconds=window)]
        if not prices_in_window:
            raise ValueError(f"price in {window} seconds for {symbol} not found")
        return prices_in_window
    
    def dump(self):
        for k, v in self.data.items():
            print("stock", k, v)
            
            
agg = StockPriceAggregator()

for stock in ["AAPL", "MSFT", "GOOG", "FB", "AMZN"]:
    num_of_prices_points = 100
    n = datetime.datetime.now()
    for i in range(num_of_prices_points):
        t = n - datetime.timedelta(seconds=(num_of_prices_points - i))
        agg.update(stock, random.randint(0, 1000), t)
agg.dump()

print("60 seconds avg for AAPL is ", agg.get_avg("AAPL"))
print("60 seconds AAPL high is ", agg.get_high("AAPL"))
print("60 seconds AAPL high is ", agg.get_low("AAPL"))