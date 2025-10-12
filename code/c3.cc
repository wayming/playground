#include <iostream>
#include <vector>

using namespace std;

int lengthOfLongestSubstring(string s) {
    if (s.length() < 2) {
        return s.length();
    }
    size_t first = 0;
    size_t second = 0;
    int max = 0;
    vector<bool> dict(128, false);

    dict[s[second]] = true;
    while (++second < s.length()) {
        if (dict.at(s[second])) {
            if (second-first > max) {
                max = second-first;
            }
            while (s[first] != s[second]) {
                dict[s[first]] = false;
                first++;
            }
            first++;
        } else {
            dict[s[second]] = true;
        }
    }

    if (second-first > max) {
        max = second-first;
    }
    
    return max;
}

int main() {
    cout << lengthOfLongestSubstring("au") << endl;
}