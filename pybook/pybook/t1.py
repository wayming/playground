def two_sum(nums: list, target: int):
    nums_dict = {}
    for idx, n in enumerate(nums):
        if target - n in nums_dict:
            return [idx, nums_dict[target - n]]
        else:
            nums_dict[n] = idx
    return []
