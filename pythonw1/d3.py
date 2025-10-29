import csv
import re
from collections import defaultdict
csvfile = "data.csv"
outfile = "out.txt"
prog = re.compile(r"(?i)ERROR")
errors = []
scores = defaultdict(list)
try:
    with open(csvfile, newline='') as f:
        rows = csv.reader(f, delimiter=',')
        total = 0
        empty = 0
        next(rows)
        for row in rows:
            if not row:
                empty += 1
            else:
                total += 1
                if prog.search(",".join(row)):
                    errors.append(",".join(row))
                else:
                    scores[row[1]].append(int(row[2]))
        print(f"total {total}, empty {empty}")
        
except Exception as e:
    print(f"Failed to process file {csvfile}: {e}")


try:
    with open(outfile, "w", newline='') as f:
        for line in errors:
            f.write(line + "\n")
except Exception as e:
    print(f"Failed to write to file {outfile}: {e}")

for k, v in scores.items():
    avg = sum(v)/len(v) if len(v) > 0 else 0
    print(k, " avg=", avg)
    

def fib(n : int) :
    x, y = 0, 1
    for _ in range(n):
        yield x
        x, y = y, x+y

for n in fib(100) :
    print(n)
        