import http.client
import urllib.parse
import threading
import concurrent.futures
import queue
import time
import multiprocessing
links = [
    "https://python.org",
    "https://docs.python.org",
    "https://peps.python.org",
]

def get_page(link: str, q, done_event: threading.Event):
    parsed_url = urllib.parse.urlparse(link)
    if not parsed_url.netloc:
        raise ValueError(f"not a valid link {link}")
    log = str(threading.get_ident()) + ".log"
    print(threading.current_thread().ident, " - ", link)
    
    conn = None
    try:
        conn = http.client.HTTPSConnection(parsed_url.netloc)
        path = parsed_url.path if parsed_url.path else "/"
        conn.request("GET", path, headers={"Host": parsed_url.netloc})
        response = conn.getresponse()
        with open(log, "w", encoding="UTF-8") as f:
            while True:
                chunk = response.read(1024)
                if not chunk:
                    break
                f.write(chunk.decode("UTF-8", errors="ignore"))
    except Exception as e:
        print(link, " ", e)
    finally:
        if conn:
            conn.close()
    q.put(log)
    done_event.set()
    return log

def consume_queue(q, done_events: list):
    completes = set()
    while len(completes) < len(done_events):
        for e in done_events:
            if e.is_set():
                if e not in completes:
                    completes.add(e)
                e.clear()
            
        while not q.empty():
            print(threading.current_thread().ident, " - ", q.get())
            q.task_done()
        if len(completes) < len(done_events):
            time.sleep(0.1)

    while not q.empty():
        print(threading.current_thread().ident, " - ", q.get())
        q.task_done()

def use_threads():
    print("use_threads")
    threads = []
    events = []
    q = queue.Queue()
    for link in links:
        e = threading.Event()
        events.append(e)
        t = threading.Thread(target=get_page, args=(link,q, e))
        threads.append(t)
    consumer = threading.Thread(target=consume_queue, args=(q,events))
    
    for t in threads:
        t.start()

    consumer.start()

    for t in threads:
        t.join()

    q.join()
    consumer.join()

#use_threads()

def use_thread_executor():
    print("use_thread_executor")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        tasks = []
        events = []
        q = queue.Queue()
        for link in links:
            e = threading.Event()
            events.append(e)
            tasks.append(ex.submit(get_page, link, q, e))
        
        consumer_task = ex.submit(consume_queue, q, events)
        
        for future in concurrent.futures.as_completed(tasks):
            try:
                resp = future.result()
                print("future response ", resp)
            except Exception as e:
                print(e)

        q.join()
        consumer_task.result()
        
#use_thread_executor()    

def use_process_executor():
    print("use_process_executor")
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as ex:
        tasks = []
        events = []
        manager = multiprocessing.Manager()
        q = manager.Queue()
        for link in links:
            e = manager.Event()
            events.append(e)
            tasks.append(ex.submit(get_page, link, q, e))
        
        consumer_task = ex.submit(consume_queue, q, events)
        
        for future in concurrent.futures.as_completed(tasks):
            try:
                resp = future.result()
                print("future response ", resp)
            except Exception as e:
                print(e)

        q.join()
        consumer_task.result()
        
use_process_executor()    

