from collections import defaultdict
weight = [10, 20, 20, 10, 10, 10]
value = [60, 110, 120, 50, 100, 80]

mem = defaultdict(lambda: defaultdict(int))
def max_weight(weight, value, i, cap):
    if i == 0 or cap == 0:
        return 0
    if i in mem and cap in mem[i]:
        return mem[i][cap]
    print(i, " ", cap)
    if cap < weight[i-1]:
        return max_weight(weight, value, i - 1, cap)
    no = max_weight(weight, value, i - 1, cap)
    yes = max_weight(weight, value, i - 1, cap - weight[i-1]) + value[i-1]
    mem[i][cap] = max(no, yes)
    return max(no, yes)
print(max_weight(weight, value, 6, 50))


def max_weight2(weight, value, i, cap):
    dp = [[0 for _ in range(cap+1)] for _ in range(i+1)]
    for x in range(1, i+1):
        for y in range(1, cap+1):
            if y < weight[x-1]:
                dp[x][y] = dp[x-1][y]
            else:
                dp[x][y] = max(dp[x-1][y], dp[x-1][y-weight[x-1]] + value[x-1])
    return dp[i][cap]
print(max_weight2(weight, value, 6, 50))
