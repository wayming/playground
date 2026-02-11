import collections


def two_sum(nums, target):
    processed = collections.defaultdict(int)
    results = []
    for idx, n in enumerate(nums):
        if n in processed:
            results.append((idx, processed[n]))
        else:
            processed[target - n] = idx
    return results
