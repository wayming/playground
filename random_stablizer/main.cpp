#include <iostream>
#include <memory>
#include <thread>
#include <chrono>
#include <map>
#include <vector>
#include <string>
#include <cstring>

using namespace std;

/*
{
  "final": "B",
  "strategy": "majority",
  "samples":  nine,
  "agreement_rate": 0.67,
  "unique_candidates": 3,
  "outlier_rate": 0.11,
  "latency_ms": 42,
  "diagnostics": {
    "counts": {"A": 2, "B": 6, "C": 1},
    "seed": 123,
    "max_workers": 4
  }
}
*/
struct Result {
    string final;
    string strategy;
    int samples;
    double agreement_rate;
    int unique_candidates;
    double outlier_rate;
    int latency_ms;
    struct Diagnostics {
        map<string, int> counts;
        int seed;
        int max_workers;
    } diagnostics;
};

int gen_probability (const string &input, int seed) {

    long sum = seed;
    for (int i = 0; i < input.length(); i++) {
        sum = (sum * 31 + input[i]) % 1000000007;
    }
    
    return sum % 100 + 1;      
}


string noisy_eval(const string &input) {
    int p1 = gen_probability(input + "0", 0);
    int p2 = gen_probability(input + "1", 1);
    int p3 = gen_probability(input + "2", 2);
    int p4 = gen_probability(input + "3", 3);
    int total = p1 + p2 + p3 + p4;
    int r = rand() % total;
    if (r < p1) {
        cout << "probabilities: " << (double)p1/total << endl;
        return "OK";
    } else if (r < p1 + p2) {
        cout << "probabilities: " << (double)p2/total << endl;
        return "FAIL";
    } else if (r < p1 + p2 + p3) {
        cout << "probabilities: " << (double)p3/total << endl;
        return "Timeout";
    } else {
        cout << "probabilities: " << (double)p4/total << endl;
        return "Retry";
    }
}


class Strategy {
public:
    virtual string eval(const vector<string> &input) = 0;
    virtual string name() = 0;
};
class MajorityStrategy : public Strategy {
public:
    string eval(const vector<string> &input) override {
        map<string, int> counts;
        for (const string &s : input) {
            counts[s]++;
        }
        int max_count = 0;
        string max_str;
        for (const auto &p : counts) {
            if (p.second > max_count) {
                max_count = p.second;
                max_str = p.first;
            }
        }
        return max_str;
    }
    string name() override {
        return "majority";
    }
};

class StragetyFactory {
public:
    static unique_ptr<Strategy> create(const string &strategy) {
        if (strategy == "majority") {
            return unique_ptr<Strategy>(new MajorityStrategy());
        }
        return nullptr;
    }
};

class StabliseResultGenerator {
public:
    StabliseResultGenerator(unique_ptr<Strategy> strategy, int samples, int seed, int max_workers, bool numeric) {
        this->strategy = move(strategy);
        this->samples = samples;
        this->seed = seed;
        this->max_workers = max_workers;
        this->numeric = numeric;
    }
    
    Result generate(const string &query) {
        auto begin = chrono::steady_clock::now();
        srand(seed);
        vector<string> raw_results;
        for (int i = 0; i < samples; i++) {
            raw_results.push_back(noisy_eval(query));
        }

        result.diagnostics.counts = counts(raw_results);
        result.diagnostics.seed = seed;
        result.diagnostics.max_workers = max_workers;

        result.final = strategy->eval(raw_results);
        result.strategy = strategy->name();
        result.samples = samples;
        result.agreement_rate = result.diagnostics.counts[result.final] / samples;
        result.unique_candidates = result.diagnostics.counts.size();
        result.outlier_rate = (result.diagnostics.counts.size() - 1) / samples;
        result.latency_ms = chrono::duration_cast<chrono::milliseconds>(chrono::steady_clock::now() - begin).count();
        return result;
    }
private:
    map<string, int> counts(const vector<string> &results) {
        map<string, int> counts;
        for (const string &result : results) {
            counts[result]++;
        }
        return counts;
    }

private:
    unique_ptr<Strategy> strategy;
    int samples;
    int seed;
    int max_workers;
    bool numeric;

    Result result;
};

void dump_result(const Result &result) {
    cout << "{" << endl;
    cout << "final: " << result.final << "," << endl;
    cout << "strategy: " << result.strategy << "," << endl;
    cout << "samples: " << result.samples << "," << endl;
    cout << "agreement_rate: " << result.agreement_rate << "," << endl;
    cout << "unique_candidates: " << result.unique_candidates << "," << endl;
    cout << "outlier_rate: " << result.outlier_rate << "," << endl;
    cout << "latency_ms: " << result.latency_ms << "," << endl;
    cout << "diagnostics: " << endl;
    cout << "{" << endl;
    cout << "  counts: {";
    bool first = true;
    for (const auto &p : result.diagnostics.counts) {
        if (!first) {
            cout << ",";
        }
        cout << p.first << ": " << p.second;
        first = false;
    }
    cout << "}" << endl;
    cout << "  seed: " << result.diagnostics.seed << "," << endl;
    cout << "  max_workers: " << result.diagnostics.max_workers << "," << endl;
    cout << "}" << endl;
    cout << "}" << endl;
}


// --query "text"              (required)
// --strategy single|majority|median   (default: majority)
// --samples N                 (default: 9, 1<=N<=101)
// --seed 123                  (default: 0)
// --max-workers 4             (default: hardware_concurrency)
// --numeric                   (switch oracle to numeric mode)
void usage(){
    cout << "Usage: " << " --query <query> --strategy <strategy> --samples <samples> --seed <seed> --max-workers <max-workers> --numeric" << endl;
    exit(1);
}

int main(int argc, char *argv[]) {
    string query;
    string strategy = "majority";
    int samples = 9;
    int seed = 0;
    int max_workers = thread::hardware_concurrency();
    bool numeric = false;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--query") == 0) {
            query = argv[i + 1];
        } else if (strcmp(argv[i], "--strategy") == 0) {
            strategy = argv[i + 1];
        } else if (strcmp(argv[i], "--samples") == 0) {
            samples = atoi(argv[i + 1]);
        } else if (strcmp(argv[i], "--seed") == 0) {
            seed = atoi(argv[i + 1]);
        } else if (strcmp(argv[i], "--max-workers") == 0) {
            max_workers = atoi(argv[i + 1]);
        } else if (strcmp(argv[i], "--numeric") == 0) {
            numeric = true;
        }
    }

    auto stablise_result_generator = StabliseResultGenerator(StragetyFactory::create(strategy), samples, seed, max_workers, numeric);
    auto result = stablise_result_generator.generate(query);
    dump_result(result);

    return 0;
}
