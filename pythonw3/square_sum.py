import http.client
import urllib.parse
import threading
import concurrent.futures
import queue
import time
import multiprocessing


def square(x):
    return x * x            
def square_sum(nums: list):
    with concurrent.futures.ProcessPoolExecutor(10) as ex:
        try:
            squares = ex.map(square, nums)
            result = sum(squares)
        except TypeError as e:
            print(e)
            return None
        except Exception as e:
            print(e)
            return None
        
        return result

nums = [10000000 * i for i in range(1, 20)]
begin = time.time()
print(square_sum(nums))
elapsed = time.time() - begin
print(elapsed, " seconds")

begin = time.time()
print(sum([x * x for x in nums]))
elapsed = time.time() - begin
print(elapsed, " seconds")