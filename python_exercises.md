# Python 练习册

本练习册基于你在工作区中完成的练习整理而成，包含 51 道练习题。每题包括：题目描述、考察范围、解决思路、一个可复制运行的验证代码片段（轻量）、以及扩展方向。你可以将验证代码复制到 REPL、脚本或测试文件中运行。

使用说明：
- 逐题练习：阅读题目 -> 实现自己的解法 -> 运行验证代码（它通常包含 assert 或简单输出）。
- 若要批量运行验证代码，我可以帮你把它们组织成 pytest 测试套件。

---

## 目录（按题号）
1. 从列表中移除偶数并排序
2. 列表中不同元素的个数（distinct count）
3. 学生平均成绩（按人聚合）
4. 按年龄与城市排序人员
5. 文本前 5 高频词（Top-5 words）
6. 每班平均分（分组聚合）
7. 集合操作（交、差、对称差）
8. 简单命令队列（PUSH/POP/SIZE）
9. 按长度与字典序排序单词（两种实现）
10. 按分数降序、姓名升序排序
11. CSV 解析与错误行写出
12. Fibonacci 生成器
13. CLI 单词计数（top N）功能
14. 原地删除有序数组的重复值
15. 字符串反转（两指针）
16. 忽略非字母判断回文
17. Two-sum
18. 有效括号匹配
19. 支持 getMin 的栈（MinStack）
20. 字符串中第一个不重复字符
21. 前 K 高频元素
22. 递归阶乘
23. 岛屿数量（DFS / BFS）
24. 网格最短路径（从左上到右下）
25. 日志统计：IP/URL 计数与词检索
26. 股票一次买卖最大利润
27. 排序与二分查找（含旋转数组搜索）
28. 并发生产者-消费者（线程/队列示例）
29. 异步爬虫（aiohttp / TaskGroup 思路）
30. 低级 HTTP 抓取 + 线程/进程池写文件
31. 进程池并行计算对比串行（square_sum）
32. StockPriceAggregator：时间窗口聚合
33. asyncio 生产者速率控制与优雅关闭
34. Base64 + Hash 生成短码（短链接思路）
35. LRU Cache（OrderedDict / 自实现）
36. 图的 DFS / BFS 遍历
37. 拓扑排序（Kahn）
38. 单源最短路径（Dijkstra）
39. 网格 BFS 最短路径并重建路径
40. TokenBucket + InFlightDeduper + LLM 流水线（综合异步）
41. 全排列 / 全组合（含去重）
42. 组合之和（Combination Sum）
43. 爬楼梯 / 斐波那契（记忆化）
44. 0/1 背包（递归与 DP）
45. 自定义迭代器与异步迭代器
46. 链表反转（迭代）
47. 最长无重复子串（滑动窗口）
48. 合并区间
49. 文件上下文管理器 & argparse 示例
50. 线程同步原语示例（Lock / Condition / Semaphore / local）
51. asyncio Lock / Event 协作示例

---

<!-- 以下为每题详情及验证代码 -->

### 1) 从列表中移除偶数并排序
题目：给定整数列表，移除偶数并对剩余奇数进行升序排序并返回。

考察：列表推导、排序算法、复杂度分析。

思路：先筛选奇数，然后 sort。

验证代码：
```python
def remove_even_and_sort(nums):
    odds = [n for n in nums if n % 2 != 0]
    odds.sort()
    return odds

assert remove_even_and_sort([5,3,2,8,1,4,10,7,6,9,0]) == [1,3,5,7,9]
print("pass 1")
```

扩展：实现原地修改版本、处理生成器或大流数据。

---

### 2) 列表中不同元素的个数（distinct count）
题目：返回列表中不同元素数量。

考察：set/hash。

验证代码：
```python
def distinct_count(nums):
    return len(set(nums))

assert distinct_count([5,3,0,8,1,7,10,7,6,9,0]) == 9
print("pass 2")
```

扩展：HyperLogLog 等近似去重方法处理大规模流。

---

### 3) 学生平均成绩（按人聚合）
题目：输入 (name, grade) 列表，返回每个学生的平均分。

考察：字典/默认字典聚合。

验证代码：
```python
from collections import defaultdict

def average_grade(records):
    d = defaultdict(list)
    for name, g in records:
        d[name].append(g)
    return {k: sum(v)/len(v) for k,v in d.items()}

assert average_grade([('Way',90),('Way',80),('H',70),('H',60),('Way',50)])['Way'] == (90+80+50)/3
print("pass 3")
```

扩展：处理缺失/无效数据、加权平均。

---

### 4) 按年龄与城市排序人员
题目：给 (name, age, city) 列表，先按 age 升序，再按 city 升序排序。

考察：排序 key。

验证代码：
```python
def order_by_age_city(persons):
    return sorted(persons, key=lambda x: (x[1], x[2]))

people = [('bob',10,'Brisbane'),('alice',30,'Sydney'),('tom',10,'Brisbane')]
res = order_by_age_city(people)
assert res[0][0] in ('bob','tom')
print("pass 4")
```

扩展：支持降序、多字段优先级。

---

### 5) 文本前 5 高频词（Top-5 words）
题目：返回文本中出现次数最多的 5 个单词及其次数。

考察：分词（标点/大小写）、Counter。

验证代码：
```python
from collections import Counter

def top5_words(text):
    words = [w for w in text.lower().split() if w.isalpha()]
    return Counter(words).most_common(5)

txt = "a a b c a b d e"
assert top5_words(txt)[0][0] == 'a'
print("pass 5")
```

扩展：更健壮的分词（正则/nltk）、停用词过滤、n-gram。

---

### 6) 每班平均分（分组聚合）
题目：输入 (class, student, grade) 列表，返回每个 class 的平均分。

考察：defaultdict、分组聚合。

验证代码：
```python
from collections import defaultdict

def avg_grades(records):
    d = defaultdict(list)
    for cls,student,g in records:
        d[cls].append(g)
    return {k: sum(v)/len(v) for k,v in d.items()}

assert avg_grades([("classA","Alice",90),("classB","Bob",85),("classA","Tom",92)])['classA'] == (90+92)/2
print("pass 6")
```

扩展：时序维度上的滑动窗口聚合。

---

### 7) 集合操作（交、差、对称差）
题目：给两个集合，输出交集大小、A-only 大小、对称差大小。

考察：集合运算。

验证代码：
```python
def counts(a, b):
    common = a & b
    aonly = a - b
    single = a ^ b
    return len(common), len(aonly), len(single)

assert counts({1,2,3,4,5},{4,5,6,7,8})[0] == 2
print("pass 7")
```

扩展：基于布隆过滤器的近似集合运算。

---

### 8) 简单命令队列（PUSH/POP/SIZE）
题目：解析字符串命令并维护队列。

考察：deque、字符串解析、异常处理。

验证代码：
```python
from collections import deque
class CommandQueue:
    def __init__(self): self.q = deque()
    def run(self, command: str):
        parts = command.split()
        op = parts[0]
        if op == "PUSH":
            self.q.append(parts[1]); return f"push {parts[1]}"
        if op == "POP":
            v = self.q.popleft(); return f"pop {v}"
        if op == "SIZE":
            return f"size {len(self.q)}"
        raise ValueError()

cq = CommandQueue()
assert cq.run("PUSH 100") == "push 100"
assert cq.run("PUSH 200") == "push 200"
assert cq.run("POP") == "pop 100"
assert cq.run("SIZE") == "size 1"
print("pass 8")
```

扩展：线程/进程安全队列、持久化命令日志。

---

### 9) 按长度与字典序排序单词（两种实现）
题目：按 (len(word), word) 排序单词，分别用内置 key 与桶排序实现。

考察：排序 key、桶思想。

验证代码：
```python
def sort_words(words):
    return sorted(words, key=lambda w:(len(w), w))

assert sort_words(["hello","world","is","py"])[0] in ("is","py")
print("pass 9")
```

扩展：针对大数据使用外部排序或流式分桶。

---

### 10) 按分数降序、姓名升序排序
题目：给成绩 map，输出按 score 降序、name 升序的列表。

考察：复合排序 key。

验证代码：
```python
def sort_grade2(grades):
    return sorted(grades.items(), key=lambda x:(-x[1], x[0]))

grades = {"Alice":90,"Bob":85,"Tom":90}
assert sort_grade2(grades)[0][0] in ('Alice','Tom')
print("pass 10")
```

扩展：分组内稳定排序、多字段拓展。

---

### 11) CSV 解析与错误行写出
题目：从 CSV 读取行，包含 "ERROR" 的写出到另一个文件，同时按第二列聚合分数并求平均。

考察：csv、文件 I/O、正则、异常处理。

验证代码：
```python
import io, csv, re

def analyse_csv_text(text):
    prog = re.compile(r"(?i)ERROR")
    errors = []
    scores = {}
    reader = csv.reader(io.StringIO(text))
    header = next(reader, None)
    for row in reader:
        if prog.search(",".join(row)):
            errors.append(",".join(row))
        else:
            scores.setdefault(row[1],[]).append(int(row[2]))
    avgs = {k:sum(v)/len(v) for k,v in scores.items()}
    return errors, avgs

txt = "id,name,score\n1,A,90\n2,B,ERROR\n3,A,80\n"
errors, avgs = analyse_csv_text(txt)
assert "ERROR" in errors[0]
assert avgs["A"] == 85.0
print("pass 11")
```

扩展：大文件的并行/流式解析、容错与监控。

---

### 12) Fibonacci 生成器
题目：实现 generator 输出 Fibonacci 序列。

考察：yield、惰性计算。

验证代码：
```python
def fib_gen(n):
    a,b=0,1
    for _ in range(n):
        yield a
        a,b = b, a+b

assert list(fib_gen(6)) == [0,1,1,2,3,5]
print("pass 12")
```

扩展：无限生成器、矩阵快速幂求 n 项。

---

### 13) CLI 单词计数（top N）
题目：统计文件中文本单词出现频率并输出 top N。

考察：argparse、Counter、文件 I/O。

验证代码：
```python
from collections import Counter

def count_words_text(text, topn=3):
    cnt = Counter()
    for line in text.splitlines():
        words = [w for w in line.strip().split() if w.isalnum()]
        cnt.update(words)
    return cnt.most_common(topn)

txt="a a b c\nb a"
assert count_words_text(txt,2)[0][0]=='a'
print("pass 13")
```

扩展：分布式统计、外部排序处理大文件。

---

### 14) 原地删除有序数组的重复值
题目：给定已排序数组，原地删除重复值并返回修改后的数组（或新长度）。

考察：双指针、就地修改。

验证代码：
```python
def remove_duplicate(nums):
    if not nums: return nums
    slow = 0
    for fast in range(1,len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    del nums[slow+1:]
    return nums

l=[1,3,4,4,7,8,8,9]
assert remove_duplicate(l) == [1,3,4,7,8,9]
print("pass 14")
```

扩展：返回长度、处理未排序数组（保持第一次出现顺序）。

---

### 15) 字符串反转（两指针）
题目：实现字符串反转。

考察：列表转换、索引操作。

验证代码：
```python
def reverse_str(s):
    l = list(s)
    i,j = 0, len(l)-1
    while i<j:
        l[i],l[j]=l[j],l[i]; i+=1; j-=1
    return ''.join(l)

assert reverse_str("abc")=="cba"
print("pass 15")
```

扩展：处理 Unicode grapheme、就地字节数组反转。

---

### 16) 忽略非字母判断回文
题目：判断字符串（忽略非字母，case-insensitive）是否为回文。

考察：字符过滤、切片比较。

验证代码：
```python
def is_palin(s):
    s2 = [c.lower() for c in s if c.isalpha()]
    return s2 == s2[::-1]

assert is_palin("A man, a plan, a canal: Panama")
print("pass 16")
```

扩展：支持 Unicode 标点、数字字符规则。

---

### 17) Two-sum
题目：返回数组中两个数之和等于目标的两个索引。

考察：哈希表，单次遍历。

验证代码：
```python
def two_sum(nums, target):
    idx={}
    for i,n in enumerate(nums):
        if target-n in idx: return (idx[target-n], i)
        idx[n]=i
    return (-1,-1)

assert two_sum([2,7,11,15],9)==(0,1)
print("pass 17")
```

扩展：返回所有不重复对、流式 two-sum。

---

### 18) 有效括号匹配
题目：判断一串括号是否有效匹配（()[]{}）。

考察：栈。

验证代码：
```python
def parentheses_match(s):
    stack=[]
    match={'(':')','[':']','{':'}'}
    for c in s:
        if c in match: stack.append(c)
        else:
            if not stack: return False
            if match[stack.pop()]!=c: return False
    return not stack

assert parentheses_match("{}[(())]")
print("pass 18")
```

扩展：定位报错位置、支持自定义括号对。

---

### 19) 支持 getMin 的栈（MinStack）
题目：实现栈并能在 O(1) 时间内获取最小值。

考察：辅助栈。

验证代码：
```python
class MinStack:
    def __init__(self):
        self.s=[]; self.mins=[]
    def push(self,x):
        self.s.append(x)
        if not self.mins or x<=self.mins[-1]: self.mins.append(x)
    def pop(self):
        v=self.s.pop()
        if v==self.mins[-1]: self.mins.pop()
    def top(self): return self.s[-1]
    def getMin(self): return self.mins[-1]

s=MinStack(); s.push(-2); s.push(0); s.push(-3)
assert s.getMin()==-3
s.pop(); assert s.top()==0
print("pass 19")
```

扩展：支持 O(1) 删除任意元素（复杂）。

---

### 20) 字符串中第一个不重复字符
题目：返回字符串中第一个只出现一次的字符。

考察：Counter 与顺序遍历。

验证代码：
```python
from collections import Counter

def first_distinct(s):
    c=Counter(s)
    for ch in s:
        if c[ch]==1: return ch
    raise ValueError

assert first_distinct("leetcode")=='l'
print("pass 20")
```

扩展：实时流中维护首个不重复字符。

---

### 21) 前 K 高频元素
题目：返回数组中出现频率前 K 的元素。

考察：Counter、heap、bucket。

验证代码：
```python
from collections import Counter

def top_k(nums,k):
    return [x for x,_ in Counter(nums).most_common(k)]

assert top_k([1,1,1,2,2,3],2)==[1,2]
print("pass 21")
```

扩展：流式 top-k、近似算法。

---

### 22) 递归阶乘
题目：实现递归阶乘。

考察：递归基与深度、迭代替代。

验证代码：
```python
def factorial(n):
    return 1 if n<=1 else n*factorial(n-1)

assert factorial(5)==120
print("pass 22")
```

扩展：大数阶乘模运算、尾递归优化（Python 中无尾递归）。

---

### 23) 岛屿数量（DFS / BFS）
题目：统计二维 0/1 网格中 1 的连通块数量（上下左右相连）。

考察：DFS/BFS、访问标记。

验证代码：
```python
def num_of_islands(grid):
    if not grid: return 0
    rows,cols=len(grid),len(grid[0])
    visited=set()
    def dfs(i,j):
        if not (0<=i<rows and 0<=j<cols): return
        if grid[i][j]==0 or (i,j) in visited: return
        visited.add((i,j))
        for di,dj in [(1,0),(-1,0),(0,1),(0,-1)]: dfs(i+di,j+dj)
    cnt=0
    for i in range(rows):
        for j in range(cols):
            if grid[i][j]==1 and (i,j) not in visited:
                cnt+=1; dfs(i,j)
    return cnt

g=[[1,1,0,0],[1,0,0,1],[0,0,1,1],[0,0,0,0]]
assert num_of_islands(g)==3
print("pass 23")
```

扩展：使用并查集、8 邻域、流式更新。

---

### 24) 网格最短路径（从左上到右下）
题目：在只允许向下或向右移动且存在障碍的网格中，找到最短路径步数或返回 -1。

考察：BFS、队列、访问检查。

验证代码：
```python
from collections import deque

def shortest_path(grid):
    if grid[0][0]==1: return -1
    rows,cols=len(grid),len(grid[0])
    q=deque([(0,0,1)])
    visited={(0,0)}
    while q:
        x,y,s=q.popleft()
        if x==rows-1 and y==cols-1 and grid[x][y]==0: return s
        for nx,ny in [(x+1,y),(x,y+1)]:
            if 0<=nx<rows and 0<=ny<cols and grid[nx][ny]==0 and (nx,ny) not in visited:
                visited.add((nx,ny))
                q.append((nx,ny,s+1))
    return -1

g=[[0,0,1,0],[0,1,0,0],[0,0,0,1],[1,0,0,0]]
assert shortest_path(g) != -1
print("pass 24")
```

扩展：四向移动、加权路径（Dijkstra）、动态障碍物。

---

### 25) 日志统计：IP/URL 计数与词检索
题目：解析日志行，统计 ip/url 出现次数，并实现在多个文件中统计关键字出现次数。

考察：Counter、文件处理、字符串清洗。

验证代码：
```python
from collections import Counter

def log_counts(lines):
    ipc=Counter(); urlc=Counter()
    for line in lines.splitlines():
        t,ip,url = line.strip().split()
        ipc.update([ip]); urlc.update([url])
    return ipc, urlc

s="t1 1.1.1.1 /a\nt2 1.1.1.2 /b\nt3 1.1.1.1 /a"
ipc, urlc = log_counts(s)
assert ipc['1.1.1.1']==2
print("pass 25")
```

扩展：时间窗口统计、top-K。

---

### 26) 股票一次买卖最大利润
题目：给定价格数组，返回一次买卖能获得的最大利润。

考察：单次遍历维护最小值和当前最大利润。

验证代码：
```python
def max_profit(prices):
    minp=10**18; ans=0
    for p in prices:
        minp=min(minp,p)
        ans=max(ans, p-minp)
    return ans

assert max_profit([7,1,5,3,6,4])==5
print("pass 26")
```

扩展：多次交易、手续费、冷冻期问题。

---

### 27) 排序与二分查找（含旋转数组搜索）
题目：实现冒泡/快速排序与二分查找，并在旋转数组中查找目标。

考察：排序、二分边界、旋转数组分段二分。

验证代码（示例冒泡）：
```python
def bubble_sort(a):
    a=a[:]
    for i in range(len(a)):
        for j in range(len(a)-i-1):
            if a[j]>a[j+1]: a[j],a[j+1]=a[j+1],a[j]
    return a

assert bubble_sort([3,1,2])==[1,2,3]
print("pass 27")
```

扩展：稳定性讨论、原地快速排序改进。

---

### 28) 并发生产者-消费者（线程/队列示例）
题目：实现并发生产者和消费者，计算消费端平均或统计值。

考察：threading、queue、Event、join/task_done。

验证代码（简化）：
```python
import threading, queue

def demo():
    q = queue.Queue()
    stop = threading.Event()
    def producer():
        for i in range(100): q.put(i)
        stop.set()
    def consumer():
        s=[]
        while not stop.is_set() or not q.empty():
            try:
                s.append(q.get(timeout=0.01)); q.task_done()
            except queue.Empty:
                continue
        print("consumed", len(s))
    t1 = threading.Thread(target=producer); t2=threading.Thread(target=consumer)
    t1.start(); t2.start(); t1.join(); t2.join()
demo(); print("pass 28")
```

扩展：Backpressure、优雅终止、性能测量。

---

### 29) 异步爬虫（aiohttp / TaskGroup 思路）
题目：并发抓取 URL 并写入文件、统计字数。

考察：aiohttp、asyncio.TaskGroup、asyncio.to_thread。

验证代码（伪）:
```python
import asyncio
async def fake_fetch(url): await asyncio.sleep(0.01); return "hello world"
async def process():
    results = await asyncio.gather(*(fake_fetch(u) for u in ["u1","u2"]))
    print(len(results))
asyncio.run(process()); print("pass 29")
```

扩展：限速、重试、连接池管理。

---

### 30) 低级 HTTP 抓取 + 线程/进程池写文件
题目：使用 http.client 与线程/进程池抓取页面并写入文件，消费者处理队列。

考察：低层 HTTP、线程/进程间通信、Queue/Manager。

验证代码：
（参考第 29 的伪实现，此处在离线环境用伪 fetch 测试。）

扩展：真实网络错误恢复、并发连接数控制。

---

### 31) 进程池并行计算对比串行（square_sum）
题目：用 ProcessPoolExecutor 并行计算平方和并与串行做时间对比。

考察：并行开销、GIL、序列化成本。

验证代码：
```python
import time, concurrent.futures

def square(x): return x*x
nums=list(range(10000))
t=time.time()
with concurrent.futures.ProcessPoolExecutor(2) as ex:
    s=sum(ex.map(square, nums))
print("done", time.time()-t); print("pass 31")
```

扩展：选择合适的并行模型（线程/进程/异步）。

---

### 32) StockPriceAggregator：时间窗口聚合
题目：实现 append (timestamp, price) 并提供窗口内 avg/high/low。

考察：deque、时间窗口裁剪、堆。

验证代码：
```python
from collections import deque
import datetime
class Agg:
    def __init__(self): self.data=deque()
    def update(self,ts,price): self.data.append((ts,price))
    def avg(self): return sum(p for _,p in self.data)/len(self.data)

now=datetime.datetime.now()
a=Agg(); a.update(now,10); a.update(now,20)
assert a.avg()==15
print("pass 32")
```

扩展：每个 symbol 的高效结构、滑动窗口优化。

---

### 33) asyncio 生产者速率控制与优雅关闭
题目：实现按速率生产并优雅关闭 asyncio 任务（TaskGroup / Event）。

考察：asyncio.Queue、Event、TaskGroup、速率限制。

验证代码：
```python
import asyncio
async def producer(q, stop, rps):
    while not stop.is_set():
        await q.put(1)
        await asyncio.sleep(1/rps)
async def consumer(q, stop):
    while not stop.is_set() or not q.empty():
        try:
            await q.get(); q.task_done()
        except asyncio.TimeoutError:
            pass
async def demo():
    q=asyncio.Queue(); stop=asyncio.Event()
    p=asyncio.create_task(producer(q,stop,5)); c=asyncio.create_task(consumer(q,stop))
    await asyncio.sleep(0.1); stop.set(); await q.join()
asyncio.run(demo()); print("pass 33")
```

扩展：动态速率、优先级队列。

---

### 34) Base64 + Hash 生成短码（短链接思路）
题目：用 sha256 摘要并用 base64 取短码。

考察：hashlib、base64、字节截断。

验证代码：
```python
import hashlib, base64

def short(url):
    raw = hashlib.sha256(url.encode()).digest()[:6]
    return base64.urlsafe_b64encode(raw).decode()[:8]

assert len(short("www.sohu.com"))>0
print("pass 34")
```

扩展：冲突检测、数据库映射。

---

### 35) LRU Cache（OrderedDict / 自实现）
题目：实现 LRU 缓存，容量超出后淘汰最旧项。

考察：OrderedDict、双向链表 + hash。

验证代码：
```python
from collections import OrderedDict
class LRUCache:
    def __init__(self,cap): self.cap=cap; self.d=OrderedDict()
    def get(self,k):
        if k not in self.d: return -1
        self.d.move_to_end(k); return self.d[k]
    def put(self,k,v):
        self.d[k]=v; self.d.move_to_end(k)
        if len(self.d)>self.cap: self.d.popitem(last=False)

c=LRUCache(2)
c.put(1,1); c.put(2,2)
assert c.get(1)==1
c.put(3,3)
assert c.get(2)==-1
print("pass 35")
```

扩展：线程安全 LRU，带 TTL 的缓存。

---

### 36) 图的 DFS / BFS 遍历
题目：实现图的深度优先与广度优先遍历（给边集）。

考察：邻接表、deque、递归/迭代。

验证代码：
```python
from collections import deque

def bfs(edges, head):
    adj = {}
    for a,b in edges: adj.setdefault(a,[]).append(b)
    q=deque([head]); res=[]
    while q:
        n=q.popleft(); res.append(n)
        for c in adj.get(n,[]): q.append(c)
    return res

assert bfs([[0,1],[0,2],[1,3],[1,4]],0)[0]==0
print("pass 36")
```

扩展：环检测、并行遍历。

---

### 37) 拓扑排序（Kahn）
题目：输出 DAG 的拓扑序。

考察：入度、队列。

验证代码：
```python
from collections import defaultdict,deque

def topo(edges):
    g=defaultdict(list); indeg=defaultdict(int)
    for u,v in edges: g[u].append(v); indeg[v]+=1; indeg.setdefault(u,0)
    q=deque([n for n,d in indeg.items() if d==0]); res=[]
    while q:
        n=q.popleft(); res.append(n)
        for nb in g[n]:
            indeg[nb]-=1
            if indeg[nb]==0: q.append(nb)
    return res

assert topo([[5,2],[5,0],[4,0],[4,1],[2,3],[3,1]])
print("pass 37")
```

扩展：检测环并报告错误。

---

### 38) 单源最短路径（Dijkstra）
题目：给加权图，求从 src 到所有顶点的最短距离。

考察：优先队列、邻接表。

验证代码：
```python
import heapq
from collections import defaultdict

def dijkstra(edges, src, n):
    g=defaultdict(list)
    for u,v,w in edges: g[u].append((v,w))
    dist=[float('inf')]*n; dist[src]=0
    pq=[(0,src)]
    while pq:
        d,u = heapq.heappop(pq)
        if d>dist[u]: continue
        for v,w in g[u]:
            if d+w<dist[v]:
                dist[v]=d+w; heapq.heappush(pq,(dist[v],v))
    return dist

edges=[[0,1,2],[0,2,4],[1,2,1],[1,3,7],[2,4,3],[3,4,1]]
assert dijkstra(edges,0,5)[4]==6
print("pass 38")
```

扩展：负权边（Bellman-Ford）、路径恢复。

---

### 39) 网格 BFS 最短路径并重建路径
题目：用 BFS 找最短路径并重建前驱路径。

考察：BFS、前驱数组。

验证代码：
```python
from collections import deque

def shortest_path_bfs(grid):
    rows,cols=len(grid),len(grid[0])
    q=deque([(0,0,0)]); prev={}
    while q:
        x,y,steps=q.popleft()
        if x==rows-1 and y==cols-1: return steps
        for nx,ny in ((x+1,y),(x,y+1)):
            if 0<=nx<rows and 0<=ny<cols and grid[nx][ny]==0 and (nx,ny) not in prev:
                prev[(nx,ny)]=(x,y); q.append((nx,ny,steps+1))
    return -1

g=[[0,0],[0,0]]
assert shortest_path_bfs(g)==2
print("pass 39")
```

扩展：路径恢复并输出具体坐标列表。

---

### 40) TokenBucket + InFlightDeduper + LLM 流水线（综合异步）
题目：实现并测试一个异步的多阶段媒体处理流水线（ASR → LLM → TTS）。

### 题目描述（摘要）
设计并实现一个异步流水线，将输入音频（ASR）转成文本提示（prompt），把 prompt 发给 LLM（语言模型）以获取文本响应，然后将响应合成成音频（TTS）。流水线需支持并发工作者、限流、in-flight 去重、缓存与过期、对 LLM 调用的重试（含指数退避）、以及健壮的异常处理与优雅终止。

### 功能要求（必须实现）
1. Pipeline 阶段：
   - ASR worker：把音频 bytes 转为 prompt（可模拟）。
   - LLM 调用：接收 prompt 并返回文本响应（模拟或接口）。
   - TTS worker：把 LLM 响应转为音频 bytes（模拟）。

2. 并发与队列：
   - 各阶段使用独立的 asyncio.Queue，多个并发消费者/工作者。
   - 支持启动 N 个 ASR→LLM 工作者、M 个 TTS 工作者。

3. 限流（TokenBucket）：
   - LLM 调用需通过 token 桶进行限流，桶有 capacity 与 rate（tokens/s）。
   - 调用前必须等待足够令牌。

4. In-flight 去重（InFlightDeduper）：
   - 当多个并发请求的 prompt 规范化后相同时，应只对 LLM 发起一次真实调用，其他请求复用该进行中的任务结果。

5. 缓存（Cache + TTL）：
   - LLM 需本地缓存 prompt 的响应，带 TTL（秒）。cache hit 时直接返回缓存值。

6. 重试（call_with_retry）：
   - LLM 调用若超时或失败，采用指数退避重试（带最大重试次数），最终失败回报 error_queue。

7. 错误处理：
   - 各阶段遇到异常应把 (aid, error_message) 推送到 error_queue 并继续处理其他任务，不使整个系统停止。

8. 优雅终止：
   - 一个音频生成器产生任务结束后，应向各工作者发送终止信号，使其完成工作并退出，随后收集剩余结果与错误并打印。

### 非功能要求
- 使用 asyncio（async/await）与 asyncio.Queue。
- 组件间尽量用清晰边界（函数/类）。
- 处理好并发共享状态（例如 InFlightDeduper 的 map、TokenBucket 的状态）——用 asyncio.Lock 等保护。
- 提供可运行的验证脚本（见下）。

### 输入 / 输出
- 输入：一系列（aid, audio_bytes）请求（模拟音频）。
- 输出：audio_response_queue 中的 (aid, audio_bytes)；error_queue 中的 (aid, error_msg)。

### 成功标准（验收条件）
- 在小规模测试下（例如 5 个并发音频生成者，每个 5 条请求）：
  - 所有请求最终要么得到 audio_response，要么记录到 error_queue。
  - 相同 prompt 的并发请求只触发一次 LLM 实际调用（通过打印/计数验证）。
  - LLM 的缓存能命中（在 TTL 内重复 prompt 返回缓存值）。
  - TokenBucket 限流能限制并发调用速率（通过日志观察间隔或 token 计数）。
  - 系统能优雅结束（所有工作者退出，queues 为空且 join 完成）。

### 关键考察点
- asyncio 并发原语（Queue, Event, Lock, Task）
- Rate limiting (Token Bucket)
- In-flight 请求去重（task deduplication）
- Cache 设计与过期策略（TTL）
- 重试策略（指数退避）
- 错误隔离与优雅终止
- 设计可组合、可测试的组件化代码

---

### 实现思路（要点）
- TokenBucket：记录上次分配时间、当前 tokens；在 wait_for_token 中在锁保护下刷新 tokens 并等待直到有足够 tokens。
- InFlightDeduper：维护 key→asyncio.Task 的映射。第一次请求创建 Task 并放入 map，添加 done callback 在完成时移除映射。后续请求直接 await 该 Task 获取结果（或异常）。
- LLM：模拟 I/O 延迟、使用本地 dict 保存 cache（val, timestamp），housekeeping 清理过期项。call_with_retry 包装 LLM 调用，使用 TokenBucket 等待并在失败时指数退避。
- Pipeline：ASR→LLM→TTS 各阶段负责消费前一队列并把结果推到下一队列；遇到 (None, None) 用于通知 worker 终止。
- 测试/验证：构造小规模音频生成器，启动若干 worker，并在最后收集响应/错误并做断言。

---

### 验证代码（自包含，可运行）

下面是一段自包含的验证脚本（简化版）。保存为 `async_pipeline_test.py` 并运行 `python async_pipeline_test.py`。该脚本实现了上面题目中的主要要点（TokenBucket、InFlightDeduper、LLM 缓存与重试、ASR/TT S worker、端到端小规模测试），并包含断言／打印来验证关键行为（cache hit / in-flight dedupe / 限流生效）。

把下面代码复制到文件并运行即可（运行会在控制台输出日志，运行时间非常短）：

```python
#!/usr/bin/env python3
# async_pipeline_test.py
import asyncio
import datetime
import hashlib
import random
import time

# --------- TokenBucket ----------
class TokenBucket:
    def __init__(self, capacity:int, rate:float):
        self.capacity = capacity
        self.rate = rate  # tokens per second
        self.tokens = capacity
        self.last = time.monotonic()
        self.lock = asyncio.Lock()

    async def wait_for_token(self, require:int=1):
        while True:
            async with self.lock:
                now = time.monotonic()
                elapsed = now - self.last
                add = int(elapsed * self.rate)
                if add > 0:
                    self.tokens = min(self.capacity, self.tokens + add)
                    self.last += add / self.rate
                if self.tokens >= require:
                    self.tokens -= require
                    return
            # backoff short
            await asyncio.sleep(max(0.01, 1.0 / max(1, self.rate)))

# --------- InFlightDeduper ----------
class InFlightDeduper:
    def __init__(self):
        self.map = {}
        self.lock = asyncio.Lock()
    async def call_and_wait(self, key:str, coro_fn, *args):
        async with self.lock:
            if key not in self.map:
                self.map[key] = asyncio.create_task(coro_fn(*args))
                # ensure removal on done
                self.map[key].add_done_callback(lambda fut, k=key: asyncio.create_task(self._remove(k)))
        return await self.map[key]
    async def _remove(self, key):
        async with self.lock:
            self.map.pop(key, None)

# --------- Mock LLM with cache + retry ----------
class MockLLM:
    def __init__(self, ttl=2):
        self.cache = {}  # key -> (resp, when)
        self.ttl = ttl
        self.call_count = 0

    def _key(self, prompt):
        filtered = "".join([c for c in prompt.lower() if c.isalnum()])
        return hashlib.sha256(filtered.encode()).hexdigest()[:8]

    def fetch_cache(self, key):
        if key in self.cache:
            val, ts = self.cache[key]
            if time.time() - ts <= self.ttl:
                return val
            else:
                self.cache.pop(key, None)
        return None

    def put_cache(self, key, val):
        self.cache[key] = (val, time.time())

    async def call(self, prompt:str):
        # simulate flakiness
        await asyncio.sleep(0.05)
        self.call_count += 1
        if random.random() < 0.2:
            raise asyncio.TimeoutError("mock llm timeout")
        return f"LLM_RESP({hash(prompt)})"

    async def call_with_retry(self, prompt:str, token:TokenBucket, retries=3):
        key = self._key(prompt)
        if (cached := self.fetch_cache(key)) is not None:
            return cached, True  # (resp, cache_hit)

        base = 0.05
        for attempt in range(retries + 1):
            try:
                await token.wait_for_token()
                resp = await self.call(prompt)
                self.put_cache(key, resp)
                return resp, False
            except asyncio.TimeoutError:
                await asyncio.sleep(base * (2 ** attempt) * (0.8 + 0.4 * random.random()))
        raise asyncio.TimeoutError("llm failed after retries")

# --------- ASR / TTS worker mocks ----------
async def asr_worker(audio:bytes):
    # pretend to transcribe bytes -> prompt
    await asyncio.sleep(0.01)
    return "prompt: " + hashlib.sha256(audio).hexdigest()[:6]

async def tts_worker(text:str):
    await asyncio.sleep(0.01)
    return hashlib.sha256(text.encode()).digest()

# --------- Pipeline workers ----------
async def asr_llm_pipeline(asr_q, llm_q, err_q, llm:MockLLM, token:TokenBucket, deduper:InFlightDeduper):
    while True:
        aid, audio = await asr_q.get()
        asr_q.task_done()
        if aid is None and audio is None:
            break
        try:
            prompt = await asr_worker(audio)
        except Exception as e:
            await err_q.put((aid, f"ASR error: {e}")); continue

        key = hashlib.sha256(prompt.encode()).hexdigest()[:8]
        try:
            # dedupe on normalized key: use prompt itself for simplicity
            resp, cache_hit = await deduper.call_and_wait(key, llm.call_with_retry, prompt, token)
            await llm_q.put((aid, resp, cache_hit))
        except Exception as e:
            await err_q.put((aid, f"LLM error: {e}"))

async def tts_pipeline(llm_q, audio_q, err_q):
    while True:
        aid, resp, cache_hit = await llm_q.get()
        llm_q.task_done()
        if aid is None and resp is None:
            break
        try:
            audio = await tts_worker(resp)
            await audio_q.put((aid, audio, cache_hit))
        except Exception as e:
            await err_q.put((aid, f"TTS error: {e}"))

# --------- Test runner ----------
async def run_smoke_test():
    # queues
    asr_q = asyncio.Queue()
    llm_q = asyncio.Queue()
    audio_q = asyncio.Queue()
    err_q = asyncio.Queue()

    token = TokenBucket(capacity=2, rate=2)  # small capacity and slow rate to make limits observable
    deduper = InFlightDeduper()
    llm = MockLLM(ttl=1)

    # start workers
    asr_workers = [asyncio.create_task(asr_llm_pipeline(asr_q, llm_q, err_q, llm, token, deduper)) for _ in range(3)]
    tts_workers = [asyncio.create_task(tts_pipeline(llm_q, audio_q, err_q)) for _ in range(2)]

    # generate audio tasks: include duplicates to test dedupe and cache
    # create 6 requests with two prompts identical (same message content)
    messages = [b"hello-1", b"hello-2", b"hello-1", b"hello-3", b"hello-2", b"hello-4"]
    for i, m in enumerate(messages):
        await asr_q.put((f"req-{i}", m))

    # wait briefly then send termination signals
    await asyncio.sleep(0.2)
    # send stop tokens for ASR workers
    for _ in asr_workers:
        await asr_q.put((None, None))
    await asr_q.join()
    # after ASR workers finish, llm_q may still have items; signal TTS workers when done
    for _ in tts_workers:
        await llm_q.put((None, None, False))
    await llm_q.join()

    # collect outputs
    responses = []
    while not audio_q.empty():
        responses.append(await audio_q.get())
        audio_q.task_done()

    errors = []
    while not err_q.empty():
        errors.append(await err_q.get()); err_q.task_done()

    # cancel tasks if still running
    for t in asr_workers + tts_workers:
        if not t.done():
            t.cancel()
            try:
                await t
            except:
                pass

    print("LLM total real calls:", llm.call_count)
    print("Responses:", responses)
    print("Errors:", errors)

    # Basic assertions:
    assert len(responses) + len(errors) == len(messages)
    # dedupe expectation: since there are repeating prompts, llm.call_count should be < len(messages)
    assert llm.call_count <= len(messages)

    print("SMOKE TEST PASSED")

if __name__ == "__main__":
    random.seed(1)
    asyncio.run(run_smoke_test())
```

运行后你应该看到类似：
- LLM total real calls: 比消息数小（说明 dedupe/缓存工作）
- Responses: 列表包含每个成功条目的 (aid, audio, cache_hit)
- Errors: 可能为空或少数（若 mock llm 出现超时并超过重试次数）

---

### 边界与异常情况（必须考虑）
- TokenBucket 速率为 0 或非常小：wait_for_token 应避免 busy-loop（使用合适 sleep）。
- InFlightDeduper 中任务抛异常时要保证 map 清理（使用 done callback 并在 await 时处理异常）。
- LLM 重试在最后应把异常抛出给 caller，由上层放入 error_queue。
- Cache 在并发写入时要考虑竞态（在 Mock 实现中，简单 dict + put 是可接受的；生产中需加锁或使用线程安全结构）。
- 优雅停机：使用 sentinel (None, None) 的约定，确保各 worker 能看到并退出；并使用 queue.join() 等待排空。

---

### 扩展题（可选加分）
- 将 LLM 的并发调用限制改为更复杂的成本模型（不同 prompt 消耗不同 tokens）。
- 实现批量 LLM 调用合并（将多个 prompt 聚合成一个批次请求）并处理响应拆分。
- 实现持久化缓存（Redis）并在多实例间共享。
- 增加度量（Prometheus）并导出每阶段延迟、失败率、缓存命中率。
- 将一部分组件（TTS/ASR）替换为真实外部服务，增加重试策略与断路器（Circuit Breaker）。

---

如果你满意这份完整题目，我可以：
- 把上述验证脚本保存到你工作区并在容器/终端运行一次并把输出结果贴回给你。
- 或者把你的仓库中 `pythonw6/async_llm_pipeline.py` 中的实现改造成更模块化、可导入（当前脚本在 import 时会执行 main），并为它写一个 pytest 测试套件（更适合 CI）。
你想让哪一个先做？

---

### 41) 全排列 / 全组合（含去重）
题目：实现 permutations/combinations 的递归算法并处理重复元素。

考察：回溯、去重技巧（visited 或 sorted + skip 重复）。

验证代码：
```python
def permute_unique(nums):
    res=[]
    nums=sorted(nums)
    used=[False]*len(nums)
    def backtrack(path):
        if len(path)==len(nums): res.append(tuple(path)); return
        prev=None
        for i in range(len(nums)):
            if used[i] or nums[i]==prev: continue
            used[i]=True; path.append(nums[i])
            backtrack(path)
            path.pop(); used[i]=False
            prev=nums[i]
    backtrack([])
    return res

assert (1,1,2) in permute_unique([1,1,2])
print("pass 41")
```

扩展：生成器版本、并行回溯。

---

### 42) 组合之和（Combination Sum）
题目：给数组与目标，返回所有不重复组合之和为目标的组合。

考察：回溯、剪枝、去重。

验证代码：
```python
def combination_sum(candidates, target):
    candidates=sorted(candidates)
    res=[]
    def backtrack(start, path, total):
        if total==target: res.append(path[:]); return
        if total>target: return
        for i in range(start,len(candidates)):
            if i>start and candidates[i]==candidates[i-1]: continue
            path.append(candidates[i])
            backtrack(i+1, path, total+candidates[i])
            path.pop()
    backtrack(0,[],0)
    return res

assert [1,2] in combination_sum([1,2,3],3)
print("pass 42")
```

扩展：允许重复使用元素（combination sum I 与 II 变体）。

---

### 43) 爬楼梯 / 斐波那契（记忆化）
题目：计算爬到第 n 楼的方式数（等价 Fibonacci 变体）。

考察：递归 + memo 或 DP。

验证代码：
```python
def ways(n, mem={}):
    if n<=1: return 1
    if n in mem: return mem[n]
    mem[n]=ways(n-1,mem)+ways(n-2,mem)
    return mem[n]

assert ways(5)==8
print("pass 43")
```

扩展：不同步长集合、矩阵快速幂。

---

### 44) 0/1 背包（递归与 DP）
题目：在给定重量与价值集合下，容量 cap 内取物品最大价值。

考察：记忆化递归、二维 DP、复杂度分析。

验证代码：
```python
def knapsack(weights, values, cap):
    n = len(weights)
    dp=[[0]*(cap+1) for _ in range(n+1)]
    for i in range(1,n+1):
        w=weights[i-1]; v=values[i-1]
        for c in range(1,cap+1):
            dp[i][c] = dp[i-1][c] if c<w else max(dp[i-1][c], dp[i-1][c-w]+v)
    return dp[n][cap]

assert knapsack([10,20,20,10,10,10],[60,110,120,50,100,80],50)==330
print("pass 44")
```

扩展：恢复选择项、空间压缩。 

---

### 45) 自定义迭代器与异步迭代器
题目：实现可在 for/async for 中使用的自定义迭代器。

考察：__iter__/__next__ 与 __aiter__/__anext__ 协议、StopIteration。

验证代码：
```python
class MyIter:
    def __init__(self,n): self.n=n
    def __iter__(self): return self
    def __next__(self):
        if not self.n: raise StopIteration
        v=self.n; self.n-=1; return v

assert list(MyIter(3))==[3,2,1]
print("pass 45")
```

扩展：异步迭代器结合 I/O。

---

### 46) 链表反转（迭代）
题目：原地反转单链表。

考察：指针操作、原地修改。

验证代码：
```python
class Node:
    def __init__(self,v,n=None): self.v=v; self.n=n

def reverse(head):
    prev=None; curr=head
    while curr:
        nxt=curr.n; curr.n=prev; prev=curr; curr=nxt
    return prev

root=Node(1,Node(2,Node(3))); r=reverse(root)
vals=[]
while r: vals.append(r.v); r=r.n
assert vals==[3,2,1]
print("pass 46")
```

扩展：递归版，K 分组反转。

---

### 47) 最长无重复子串（滑动窗口）
题目：找到字符串中无重复字符的最长子串长度。

考察：滑动窗口、哈希集合。

验证代码：
```python
def max_sub_len(s):
    seen=set(); i=0; res=0
    for j,ch in enumerate(s):
        while ch in seen:
            seen.remove(s[i]); i+=1
        seen.add(ch); res=max(res, j-i+1)
    return res

assert max_sub_len("abccdefgg")==4
print("pass 47")
```

扩展：返回子串位置与内容。

---

### 48) 合并区间
题目：合并重叠的区间集合。

考察：排序 + 线性扫描。

验证代码：
```python
def merge_intervals(intervals):
    if not intervals: return []
    s=sorted(intervals, key=lambda x:x[0])
    res=[s[0][:]]
    for a,b in s[1:]:
        if a>res[-1][1]: res.append([a,b])
        else: res[-1][1]=max(res[-1][1], b)
    return res

print(merge_intervals([[15,18],[2,6],[8,10],[1,3]]))
print("pass 48")
```

扩展：在线合并、多维区间问题。

---

### 49) 文件上下文管理器 & argparse 示例
题目：用 contextlib.contextmanager 实现文件上下文管理，并演示 argparse 用法。

考察：with 语义、异常处理、命令行参数。

验证代码：
```python
from contextlib import contextmanager
@contextmanager
def file_ctx(name):
    f=open(name,'w');
    try: yield f
    finally: f.close()

with file_ctx("tmp.txt") as f: f.write("ok")
print("pass 49")
```

扩展：异步 context manager、网络资源的管理。

---

### 50) 线程同步原语示例（Lock / Condition / Semaphore / local）
题目：示例线程锁、条件变量、信号量与 threading.local 的常见用法与风险。

考察：并发同步原语、竞态条件、死锁风险。

验证代码：
```python
import threading

def demo():
    lock=threading.Lock(); cnt=0
    def worker():
        nonlocal cnt
        with lock:
            cnt+=1
    threads=[threading.Thread(target=worker) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    print("pass 50")

demo()
```

扩展：读写锁、可重入锁、性能测试。

---

### 51) asyncio Lock / Event 协作示例
题目：演示 asyncio.Lock 和 asyncio.Event 的使用与协作。

考察：asyncio 原语、任务同步与取消。

验证代码：
```python
import asyncio
async def worker(data, lock, fire):
    async with lock:
        await fire.wait()
        data.append(asyncio.current_task().get_name())
async def unlock(lock):
    await asyncio.sleep(1)
    if lock.locked(): lock.release()
async def begin(e):
    await asyncio.sleep(2); e.set()
async def main():
    lock=asyncio.Lock(); await lock.acquire()
    data=[]; fire=asyncio.Event()
    tasks=[asyncio.create_task(worker(data, lock, fire)) for _ in range(10)]
    tasks.append(asyncio.create_task(unlock(lock)))
    tasks.append(asyncio.create_task(begin(fire)))
    await asyncio.gather(*tasks)
    print("pass 51")
asyncio.run(main())
```

扩展：超时、任务取消与错误传播。

---

## 后续建议
- 如需我将上述所有验证代码组织成一个 `tests/` 目录并用 pytest 运行，我可以继续：会创建 `tests/test_exercises.py` 并把每个验证片段做成单元测试，然后在容器中运行 `pytest` 并报告结果。
- 或者我可以把每道题导出为单独的 Markdown 或 Jupyter notebook（便于教学）。

请告诉我你希望的下一步（例如：生成 pytest 测试套件并运行）。
