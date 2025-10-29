import concurrent.futures
import threading
import queue
import time
import datetime
import random

def producer(iterations: int, q: queue.Queue):
    text = str(threading.current_thread().ident) + " "+\
           datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S:%f")
    for _ in range(iterations):
        try:
            n = random.randint(0, 1000)
            print(f"producer: put {n}")
            q.put((text, n))
        except Exception as e:
            print(f"producer: Failed to put into queue. {e}")


def consumer(q: queue.Queue, stop: threading.Event):
    nums = []
    while not stop.is_set() or not q.empty():
        try:
            text, num = q.get(0.1)
            print("consumer:", text)
            nums.append(num)
            q.task_done()
        except queue.Empty as e:
            continue
        except Exception as e:
            print(e)
    
    if nums:
        print("consumer: avg=", sum(nums)/len(nums))
    else:
        print("consumer: no data received")

def main():
    num_producers = 10
    num_consumers = 5
    data_queue = queue.Queue()
    stop = threading.Event()

    with concurrent.futures.ThreadPoolExecutor(num_producers + num_consumers) as e:
        producer_jobs = [e.submit(producer, 10000, data_queue) for _ in range(num_producers)]
        consumer_jobs = [e.submit(consumer, data_queue, stop) for _ in range(num_consumers)]
        for f in concurrent.futures.as_completed(producer_jobs):
            try:
                f.result()
            except Exception as e:
                print(e)
        stop.set()
        for f in concurrent.futures.as_completed(consumer_jobs):
            try:
                f.result()
            except Exception as e:
                print(e)

if __name__ == "__main__":
    main()