def two_sum(nums: list, target: int):
    nums_dict = {}
    for n in nums:
        if target -n in nums_dict:
            return [n, target-n]
        else:
            nums_dict[n] = True
    return []

def main():
    print(two_sum([1,3,4,5,6], 8))

if __name__ == "__main__":
    main()