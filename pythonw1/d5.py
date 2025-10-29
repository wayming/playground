from collections import defaultdict
from argparse import ArgumentParser
import csv

def analyse_file(in_file: str, out_file: str):
    out = None
    try:
        out = open("error.log", "w")
        with open(in_file, mode="r", encoding="UTF-8") as f:
            d = csv.DictReader(f, delimiter=',')
            
            grades_by_name = defaultdict(list)
            for row in d:
                try:
                    grades_by_name[row['name']].append(float(row['score']))
                except (ValueError, KeyError) as e:
                    out.write(f"Failed to read row {row} {e}")

        with open(out_file, "w", encoding="UTF-8") as f:
            for k, v in grades_by_name.items():
                student_avg = sum(v)/len(v)
                student_max = max(v)
                student_cnt = len([x for x in v if x >= 60])
                f.write(f"{k} avg={student_avg} max={student_max} cnt={student_cnt}\n")
    except Exception as e:
        print(e)
    finally:
        if out:
            out.close()

def main():
    parser = ArgumentParser(prog="analyser", description="analyse student grades")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=False, default="output.txt")
    args = parser.parse_args()
    analyse_file(args.input, args.output)

if __name__ == "__main__":
    main()
