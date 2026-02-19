def combination_sum(nums: list[int], target: int) -> list[list[int]]:

    results = set()

    def dfs(idx, path, target):

        if target == 0:
            results.add(tuple(sorted(path)))
            return

        if idx >= len(nums) or target < 0:
            return

        path.append(nums[idx])
        dfs(idx + 1, path, target - nums[idx])
        path.pop()
        dfs(idx + 1, path, target)

    dfs(0, [], target)
    return [list(x) for x in results]
