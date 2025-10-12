#include <vector>
#include <iostream>
using namespace std;

void dumpVec(vector<int>& v) {
    for (auto i : v) {
        cout << i << " ";
    }
    cout << endl;
}

void dumpVecVec(vector<vector<int>>& v) {
    for (auto i : v) {
        dumpVec(i);
    }
}
vector<vector<int>> permute(vector<int>& nums) {
    vector<vector<int>> ret;
    if (nums.empty()) {
        return ret;
    }
    
    for (auto v : nums) {
        vector<int> remain;
        for (auto v2 : nums) {
            if (v2 != v) {
                remain.push_back(v2);
            }
        }
        vector<vector<int>> res = permute(remain);
        if (res.empty()) {
            ret.emplace_back(vector<int>{v});
        } else {
            for (auto r : res) {
                vector<int> oneRes;
                oneRes.push_back(v);
                oneRes.insert(oneRes.end(), r.begin(), r.end());
                ret.push_back(oneRes);
            }
        }

    }

    return ret;
}

int main() {
    vector<int> v{1, 2, 3};
    for (auto i : permute(v)) {
        for (auto j : i) {
            cout << j << " ";
        }
        cout << endl;
    }
}