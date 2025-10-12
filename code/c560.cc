#include <iostream>
#include <vector>

using namespace std;

int subarraySum(vector<int>& nums, int k) {
    size_t len = nums.size();
    if (len == 0) {
        return 0;
    }

    size_t a = 0;
    size_t b = 0;

    int sum = nums[0];
    int count = 0;
    if (sum == k) {
        count = 1;
    }

    while(++b < len) {
        sum += nums[b];

        if (sum > k) {
            while (sum > k) {
                sum -= nums[a];
                a++;
            }
        } else if (sum < k) {
            while (sum < k) {
                sum -= nums[a];
                a++;
            }
        } else {
            count++;
            continue;
        }
        
        if (sum == k) {
            count++;
        }
    }

    return count;
}

int main() {
    vector<int> v{-1, -1, 1};
    cout << subarraySum(v, 0) << endl;
}
