import asyncio
import collections
import concurrent.futures
import http.client
import queue
import threading
import time
import urllib.error
import urllib.parse
import urllib.request


def t71_top_k(nums: list, topn):
    count = collections.defaultdict(int)
    for n in nums:
        count[n] += 1
    countPairs = [(v, k) for k, v in count.items()]
    return [y for _, y in sorted(countPairs, reverse=True)][0:topn]


def t72_factorial(n):
    return 1 if n == 1 else n * t72_factorial(n - 1)


def t73_islands(grid):
    visited = set()
    count = 0

    def dfs(x, y):
        if x >= len(grid) or y >= len(grid[0]) or x < 0 or y < 0:
            return

        if grid[x][y] == 0 or (x, y) in visited:
            return
        visited.add((x, y))
        dfs(x + 1, y)
        dfs(x, y + 1)
        dfs(x, y - 1)
        dfs(x - 1, y)

    for x, row in enumerate(grid):
        for y, col in enumerate(row):
            if col == 1 and (x, y) not in visited:
                print((x, y))
                count += 1
                dfs(x, y)
    return count


def t74_shortest_path(grid: list[list[int]]):
    rows = len(grid)
    cols = len(grid[0])

    def bfs(root: set):
        x, y = root
        print(f"{x} - {y}")
        if x == rows - 1 and y == cols - 1:
            return 1  # End

        if grid[x][y] == 1:
            return -1  # Blocked
        right, down = -1, -1
        if y < cols - 1:
            right = bfs((x, y + 1))
        if x < rows - 1:
            down = bfs((x + 1, y))
        print(f"{right} - {down}")
        if right < 0 and down < 0:
            return -1

        if right < 0:
            return 1 + down
        elif down < 0:
            return 1 + right
        else:
            return 1 + min(right, down)

    return bfs((0, 0))


def t74_shortest_path2(grid: list[list[int]]):
    processed = collections.deque(tuple())
    if grid[0][0] == 1:
        return -1
    processed.append((0, 0, 1))
    rows = len(grid)
    cols = len(grid[0])
    while processed:
        (x, y, v) = processed.popleft()
        if x == rows - 1 and y == cols - 1:
            return v
        if x < rows - 1 and grid[x + 1][y] != 1:
            processed.append((x + 1, y, v + 1))
        if y < cols - 1 and grid[x][y + 1] != 1:
            processed.append((x, y + 1, v + 1))
    return -1


def t76_max_profit(prices: list):
    low = -1
    high = -1
    up = False
    legs = []
    for p in prices:
        if low < 0:
            low = p
            high = p
            continue
        if up:
            if p >= high:
                high = p
                continue
            else:
                legs.append((low, high))
                low = p
                up = False
                continue
        else:
            if p <= low:
                low = p
                continue
            else:
                legs.append((high, low))
                high = p
                up = True
                continue
    legs.append((low, high)) if up else legs.append((high, low))
    return legs


def t77_bubble_sort(nums: list):
    length = len(nums)
    while length > 1:
        for idx in range(length - 1):
            if nums[idx] > nums[idx + 1]:
                nums[idx], nums[idx + 1] = nums[idx + 1], nums[idx]
        length -= 1


class T78:
    def __init__(self, p, c, m):

        self.messages_per_producer = m
        self.consumers = []
        self.producers = []
        self.queue = queue.Queue()
        self.run = threading.Event()
        self.complete = threading.Event()
        self.producer(p)
        self.consumer(c)
        pass

    def put(self, num_messages: int):
        self.run.wait()
        for m in range(num_messages):
            self.queue.put(m)

    def get(self):
        self.run.wait()
        while not self.complete.is_set() and not self.queue.empty():
            try:
                print(
                    f"{threading.current_thread().name} - {self.queue.get(timeout=2)}"
                )
                self.queue.task_done()
            except queue.Empty:
                print("ignore queue empty exception")
                time.sleep(0.1)
                continue

    def producer(self, n):
        for _ in range(n):
            self.producers.append(
                threading.Thread(target=self.put, args=(self.messages_per_producer,))
            )

    def consumer(self, n):
        for _ in range(n):
            self.consumers.append(threading.Thread(target=self.get))

    def fire(self):
        for t in self.producers:
            t.start()
        for t in self.consumers:
            t.start()
        self.run.set()

        for t in self.producers:
            t.join()

        self.queue.join()
        self.complete.set()

        for t in self.consumers:
            t.join()


class T79_Async_Crawler:
    def __init__(self):
        pass

    def fetch_url(self, url):
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                encoding = response.headers.get_content_charset()
                print(encoding)
                return response.read().decode(encoding)
        except urllib.error.HTTPError as e:
            print(
                "Failed to read url "
                + url
                + ", Error: "
                + str(e.reason)
                + ", Code: "
                + str(e.code)
            )
        except urllib.error.URLError as e:
            print("Failed to read url " + url + ", Error: " + str(e.reason))
        except Exception as e:
            print("Failed to read url " + url + ", Error: " + str(e))
        return None

    async def run(self, urls: list[str]):
        tasks = []
        async with asyncio.TaskGroup() as tg:
            for url in urls:
                tasks.append(tg.create_task(asyncio.to_thread(self.fetch_url, url)))
        return [t.result() for t in tasks]


class T80_MP_Crawler:
    def __init__(self):
        self.in_queue = queue.Queue()
        self.out_queue = queue.Queue()

        pass

    def fetch_url(self, url):
        try:
            urlComponents = urllib.parse.urlparse(url)
            conn = http.client.HTTPConnection(host=urlComponents.netloc, timeout=2)
            path = urlComponents.path if urlComponents.path else "/"
            conn.request("GET", path)
            resp = conn.getresponse()
            if resp.status != 200:
                return "{resp.status}: {resp.reason}"
            return resp.read().decode("UTF-8")
        except http.client.HTTPException as e:
            print("Failed to read url " + url + "Error: " + str(e))
        finally:
            if conn:
                conn.close()

        return None

    def fetch_url_func(self):
        while not self.in_queue.empty():
            try:
                url = self.in_queue.get_nowait()
                self.in_queue.task_done()
                self.out_queue.put(self.fetch_url(url))
            except queue.Empty as e:
                print(str(e))
            except Exception as e:
                print(str(e))

        return "Execution Completed"

    def run(self, urls, nparallel):
        for url in urls:
            self.in_queue.put(url)

        execFutures: list[concurrent.futures.Future] = []
        with concurrent.futures.ThreadPoolExecutor(nparallel) as executor:
            execFutures = [
                executor.submit(self.fetch_url_func) for _ in range(nparallel)
            ]

        self.in_queue.join()

        for f in concurrent.futures.as_completed(execFutures):
            try:
                print(f.result())
            except Exception as e:
                print("Task Failed:", e)

        results = []
        while not self.out_queue.empty():
            result = self.out_queue.get()
            self.out_queue.task_done()
            print(result)
            results.append(len(result) if result else 0)

        return results
