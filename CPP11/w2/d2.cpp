#include <stdlib.h>
#include <vector>
#include <iostream>
#include <algorithm>

void sort(std::vector<int>& nums) {
    if (nums.empty()) {return;}
    size_t endIdx = nums.size() - 1;
    while( endIdx > 0) {
        size_t idx = 0;
        for(idx; idx < endIdx; idx++) {
            if (nums[idx] < nums[idx+1]) {
                std::swap(nums[idx], nums[idx+1]);
            }
        }
        endIdx--;
   }
}
void topK(std::vector<int>& nums, int k) {
    if (k > nums.size() || k <= 0) {
        throw std::runtime_error("invalid number");
    }
    sort(nums);
    for (size_t i = 0; i < k; i++) {
        std::cout << nums[i] << std::endl;
    }
}

void topK2(std::vector<int>& nums, int k) {
    if (k > nums.size() || k <= 0) {
        throw std::runtime_error("invalid number");
    }
    std::make_heap(nums.begin(), nums.end());
    for (size_t i = 0; i < k; i++) {
        std::pop_heap(nums.begin(),nums.end()-i);
        std::cout << nums[nums.size() - i - 1] << std::endl;
    }
}

void topK3(std::vector<int>& nums, int k) {
    if (k > nums.size() || k <= 0) {
        throw std::runtime_error("invalid number");
    }
    std::nth_element(nums.begin(), nums.begin() + k - 1, nums.end(), std::greater<int>{});
    for (size_t i = 0; i < k; i++) {
        std::cout << nums[i] << std::endl;
    }
}

int main(){

    std::vector v1 = {5,1,9,3,7,2};
    topK(v1, 3);
    topK(v1, 6);

    std::vector v2 = {5,1,9,3,7,2};
    topK(v2, 3);
    topK(v2, 6);

    std::vector v3 = {5,1,9,3,7,2};
    topK(v3, 3);
    topK(v3, 6);
}