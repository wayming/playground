import math
import multiprocessing as mt


def computeSqrt(n):
    return math.sqrt(n)


def process(nums):
    results = []
    for n in nums:
        results.append(computeSqrt(n))
    return results


def processMt(nums):
    with mt.Pool(20) as pool:
        results = pool.map(computeSqrt, nums)
        return results
