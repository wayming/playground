from collections import Counter
from collections import defaultdict
ip_count = Counter()
url_count = Counter()
try:
    with open("d4.log", "r", encoding="UTF-8") as f:
        for line in f:
            tokens = line.strip().split()
            if len(tokens) != 3:
                print("invalid data, ignore")
                continue
            timestamp, ip, url = tokens
            ip_count.update({ip: 1})
            url_count.update({url: 1})
except Exception as e:
    print(e)

for k, v in ip_count.items():
    print(f"{k}: {v}")

for k, v in url_count.items():
    print(f"{k}: {v}")

print(url_count.most_common(1))


def search(key: str):
    wordsMap = defaultdict(lambda: defaultdict(int))
    files = ['file1.txt', 'file2.txt', 'file3.txt']
    for file in files:
        try:
            with open(file, "r", encoding="UTF-8") as f:
                for line in f:
                    s = [c for c in line if c.isspace() or c.isalpha()]
                    words = "".join(s).split()
                    for word in words:
                        wordsMap[file][word.lower()] += 1
        except Exception as e:
            print(e)
    
    for k, v in wordsMap.items():
        if key in v:
            count = v[key]
            print(f"{k} {count}")


search("python")

def max_profit(prices: list):
    min_price = prices[0]
    max_profit = 0
    for p in prices:
        if p < min_price:
            min_price = p
        elif p - min_price > max_profit:
            max_profit = p - min_price
    return max_profit

print(max_profit([7, 1, 5, 3, 6, 4]))
