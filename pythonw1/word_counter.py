import argparse
from collections import Counter

def count_words(filename: str, topn: int):
    cnt = Counter()
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line in f:
                print(line)
                words = [x for x in line.strip().split(" ") if x.isalnum()]
                print(words)
                cnt.update(words)
    except Exception as e:
        print("error {e}")
    
    print(cnt.most_common(topn))
    
def main() :
    parser = argparse.ArgumentParser(prog="word_counter", description="count words")
    parser.add_argument("--file", required=True, help="input file")
    parser.add_argument("--n", type=int, default=10, help="top n, defaults to 10")
    args = parser.parse_args()
    
    count_words(args.file, args.n)

if __name__ == "__main__":
    main()