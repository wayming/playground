from re import S


def dump_dp(dp: list[list[int]]):
    print("----------------")
    for row in dp:
        print(row)
def dp_resolver(elemVal: list[int], elemWeight: list[int], capWeight: int) -> tuple[int, list[int]]:
    s = len(elemVal)
    dp = [[0 for _ in range(capWeight+1)] for _ in range(s+1)]
    for elemIdx in range(1, s+1):
        for weight in range(capWeight+1):
            if weight >= elemWeight[elemIdx-1]:
                dp[elemIdx][weight] = max(dp[elemIdx-1][weight], dp[elemIdx-1][weight - elemWeight[elemIdx-1]] + elemVal[elemIdx-1])
            else:
                dp[elemIdx][weight] = dp[elemIdx-1][weight]
            # dump_dp(dp)
            
    maxResult = dp[s][capWeight]
    selected = []
    for elemIdx in range(s, 0, -1):
        if capWeight >= elemWeight[elemIdx-1] and dp[elemIdx][capWeight] == dp[elemIdx -1][capWeight - elemWeight[elemIdx-1]] + elemVal[elemIdx-1]:
            selected.append(elemVal[elemIdx-1])
            capWeight -= elemWeight[elemIdx-1]
    return maxResult, selected

def main():
    vals = [2, 8, 4, 5, 9]
    weights = [2, 3, 1, 3, 2]
    max, selected = dp_resolver(vals, weights, 6)
    print(max)  
    print(selected)


if __name__ == "__main__":
    main()
