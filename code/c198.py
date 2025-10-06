import sys

class Solution(object):
    def rob(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        n = len(nums)
        dp = [0]*(n+1)
        dp[0] = 0
        dp[1] = nums[0]
        for i in range(2, n+1):
            dp[i] = max(dp[i-2] + nums[i-1], dp[i-1])
        
        return dp[n]

if __name__ == '__main__':
    s = Solution()
    print(s.rob([int(x) for x in sys.argv[1].split(",")]))