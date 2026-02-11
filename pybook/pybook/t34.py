def remove_duplicate_from_ordered_list(nums: list):
    idx1 = 0
    idx2 = 1
    while idx2 < len(nums):
        if nums[idx2] != nums[idx2 - 1]:
            idx1 += 1
            nums[idx1] = nums[idx2]

        idx2 += 1
    nums = nums[0 : idx1 + 1]
    return len(nums)
