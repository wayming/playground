def buble_sort(nums: list):
    for i in range(len(nums)):
        for j in range(len(nums) - i - 1):
            if nums[j] > nums[j+1]:
                nums[j], nums[j+1] = nums[j+1], nums[j]

def quick_sort(nums: list, low: int, high: int):
    if high - low < 2:
        return
    pivot = nums[high]
    pre = low
    post = high-1
    while pre <= post:
        while nums[pre] < pivot and pre <= post:
            pre += 1
        while nums[post] >= pivot and pre <= post:
            post -= 1
        print("pre=", pre, ", post=", post, ", pivot=", pivot)
        if post > pre:
            nums[pre], nums[post] = nums[post], nums[pre]
    nums[pre], nums[high] = nums[high], nums[pre]
    quick_sort(nums, low, pre-1)
    quick_sort(nums, pre+1, high)
    
nums = [5, 2, 9, 1, 5, 6]
buble_sort(nums)
print(nums)


nums = [5, 2, 9, 1, 5, 6]
quick_sort(nums, 0, len(nums)-1)
print(nums)

def func(nums: list = []) :
    nums.append(1)
    print(nums)

n1 = []
func(n1)
n2 = []
func(n2)
n3 = []
func(n3)


def bin_search(nums: list, target: int):
    low = 0
    high = len(nums) - 1
    while low <= high:
        m = (high - low)//2
        if nums[low+m] > target:
            high = m - 1
        elif nums[low+m] < target:
            low = low + m + 1
        else:
            return low+m
    
    return -1
print(bin_search([-1,0,3,5,9,12], 9))

def rotate_search(nums:list, target: int):
    max = nums[0]
    part1 = []
    part2 = []
    for i in range(len(nums)):
        if nums[i] >= max:
            max = nums[i]
        else:
            part1 = nums[:i]
            part2 = nums[i:]
            break
    print(part1)
    print(part2)
    if target >= nums[0]:
        return bin_search(part1, target)
    else:
        find = bin_search(part2, target)
        if find != -1:
            return len(part1) + find
        else:
            return find
        
print(rotate_search([4,5,6,7,0,1,2], 0))