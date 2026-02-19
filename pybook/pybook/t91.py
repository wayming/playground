def t91_permute_unique(nums: list[int]) -> list[tuple[int, ...]]:
    def dfs(nums):
        results = []
        if len(nums) == 1:
            return [(nums[0],)]

        visited = set()
        for idx in range(len(nums)):
            curr = nums[idx]
            if curr not in visited:
                visited.add(curr)
                remain = []
                if idx == len(nums) - 1:
                    remain = nums[:idx]
                else:
                    remain = nums[:idx] + nums[idx + 1 :]
                for r in dfs(remain):
                    results.append((curr,) + r)

        return results

    return dfs(nums)


def t91_permute_unique_op(nums: list[int]) -> list[tuple[int, ...]]:
    def dfs(first):
        results = []
        if first == len(nums) - 1:
            return [(nums[first],)]

        visited = set()
        for idx in range(first, len(nums)):
            curr = nums[idx]
            if curr not in visited:
                visited.add(curr)
                nums[first], nums[idx] = nums[idx], nums[first]
                for r in dfs(first + 1):
                    results.append((curr,) + r)
                nums[idx], nums[first] = nums[first], nums[idx]

        return results

    return dfs(0)
