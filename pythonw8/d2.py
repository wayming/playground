import threading
import logging
import time
import traceback
import random
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
)

class SharedData:
    def __init__(self):
        self.lock = threading.Lock()
        self.cnt = 0
        
    def increment(self):
        with self.lock:
            self.cnt += 1
            logging.info(self.cnt)
            logging.info(self.lock.acquire(0))

def func(data: SharedData, stop: threading.Event, fire: threading.Condition, concurr: threading.Semaphore, local_data: threading.local):
        with fire:
            fire.wait()
        with concurr:
            while not stop.is_set():
                data.increment()
        local_data = random.randint(200, 300)

threads = []
stop = threading.Event()
data = SharedData()
fire = threading.Condition()
max_concurr = threading.Semaphore(1)
local_data = threading.local()
local_data.val = 100
for i in range(5):
    threads.append(threading.Thread(target=func, args=(data, stop, fire, max_concurr, local_data)))

for t in threads:
    t.start()

time.sleep(0.1)
with fire:
    fire.notify_all()
time.sleep(0.1)
stop.set()

for t in threads:
    t.join()

logging.info(local_data.val)