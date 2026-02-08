def find_duplicte(nums):
    slow = nums[0]
    fast = nums[nums[0]]
    while slow != fast:
        slow = nums[slow]  # 1 step
        fast = nums[nums[fast]]  # 2 Steps

    slow = 0
    while slow != fast:
        slow = nums[slow]  # 1 step
        fast = nums[fast]  # 1 step

    return slow
