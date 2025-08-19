#include <iostream>
#include <memory>
#include <thread>
#include <chrono>
#include <map>
#include <vector>
#include <string>
#include <cstring>
#include <mutex>
#include <thread>

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





class RetCodeGeneratorInterface {
public:
    virtual vector<string> generate(const string &input, int sample, int seed) = 0;
};

class RetCodeGenerator : public RetCodeGeneratorInterface {
public:
    RetCodeGenerator() {}
    vector<string> generate(const string &input, int sample, int seed) override {
        this->setProbability(input, seed);
        vector<string> results;
        for (int i = 0; i < sample; i++) {
            results.push_back(noisyEval(input, seed));
        }
        return results;
    }

protected:
    void setProbability(const string &input, int seed) {
        srand(time(NULL));
        this->p1 = genProbability(input + "0", seed);
        this->p2 = genProbability(input + "1", seed);
        this->p3 = genProbability(input + "2", seed);
        this->p4 = genProbability(input + "3", seed);
        this->total = p1 + p2 + p3 + p4;
    }
    string noisyEval(const string &input, int seed) {

        // simulate delay
        this_thread::sleep_for(chrono::nanoseconds(10));


        int r = rand() % total;
        if (r < p1) {
            return "OK";
        } else if (r < p1 + p2) {
            return "FAIL";
        } else if (r < p1 + p2 + p3) {
            return "Timeout";
        } else {
            return "Retry";
        }
    }

    int genProbability (const string &input, int seed) {

        long sum = seed;
        for (int i = 0; i < input.length(); i++) {
            sum = (sum * 31 + input[i]) % 1000000007;
        }
        
        return sum % 100 + 1;      
    }
    int p1;
    int p2;
    int p3;
    int p4;
    int total;

};

class ParallelRetCodeGenerator : public RetCodeGenerator {
public:
    ParallelRetCodeGenerator(int max_workers) : max_workers(max_workers) {}
    vector<string> generate(const string &input, int sample, int seed) override {
        this->setProbability(input, seed);
        vector<string> results;
        mutex results_mutex;
        vector<thread> threads;
        int remaining_samples = sample;
        for (int i = 0; i < max_workers; i++) {
            int thread_samples;
            if (i == max_workers - 1) {
                thread_samples = remaining_samples;
            } else {
                thread_samples = sample / max_workers;
            }
            thread t([=, &results, &results_mutex]() {
                for (int j = 0; j < thread_samples; j++) {
                    lock_guard<mutex> lock(results_mutex);
                    results.push_back(noisyEval(input, seed));
                }
            });
            threads.push_back(move(t));
            remaining_samples -= thread_samples;
        }
        for (auto &t : threads) {
            t.join();
        }

        return results;
    }
private:
    int max_workers;
};

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
    StabliseResultGenerator(unique_ptr<RetCodeGeneratorInterface> code_generator, unique_ptr<Strategy> strategy, int samples, int seed, int max_workers, bool numeric) {
        this->code_generator = move(code_generator);
        this->strategy = move(strategy);
        this->samples = samples;
        this->seed = seed;
        this->max_workers = max_workers;
        this->numeric = numeric;
    }
    
    Result generate(const string &query) {
        auto begin = chrono::steady_clock::now();

        auto raw_results = code_generator->generate(query, samples, seed);
        result.diagnostics.counts = counts(raw_results);
        result.diagnostics.seed = seed;
        result.diagnostics.max_workers = max_workers;

        result.final = strategy->eval(raw_results);
        result.strategy = strategy->name();
        result.samples = samples;
        result.agreement_rate = double(result.diagnostics.counts[result.final]) / samples;
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
    unique_ptr<RetCodeGeneratorInterface> code_generator;
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

    unique_ptr<RetCodeGeneratorInterface> retCodeGenerator;
    if (max_workers == 1) {
        retCodeGenerator = make_unique<RetCodeGenerator>();
    } else {
        retCodeGenerator = make_unique<ParallelRetCodeGenerator>(max_workers);
    }
    auto stablise_result_generator = StabliseResultGenerator(move(retCodeGenerator), StragetyFactory::create(strategy), samples, seed, max_workers, numeric);
    auto result = stablise_result_generator.generate(query);
    dump_result(result);

    return 0;
}
