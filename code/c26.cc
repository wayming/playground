#include <vector>
#include <iostream>

using namespace std;
int removeDuplicates(vector<int> &nums) {
    vector<int>::iterator iterFirst = nums.begin();
    vector<int>::iterator iterSecond = nums.begin() + 1;
    while (iterSecond != nums.end()) {
        if (*iterSecond != *iterFirst) {
            iterFirst++;
            *iterFirst = *iterSecond;
        }
        iterSecond++;
    }
    return iterFirst - nums.begin() + 1;
}

int main() {
    vector<int> v{1, 1, 2};
    removeDuplicates(v);
    for (auto i :v) {
        cout << i << " ";
    }
    cout << endl;
}