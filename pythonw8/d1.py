from contextlib import contextmanager
from pprint import pprint
import pickle
import argparse
@contextmanager
def FileContext(f):
    try:
        fd = open(f, encoding="UTF-8")
        print("Enter")
        yield fd
    except Exception as e:
        raise
    finally:
        print("Exit")
        fd.close()

with FileContext("d1.py") as f:
    pprint(f.read())


d1 = (('aa', 1), ('bb', 2))
pprint(hash(d1))

pprint([bin(x) for x in "this is a test".encode()])
pprint(bin(hash("this is a test")))

pprint(pickle.dumps(d1))

if __name__ == "__main__":
    parser = argparse.ArgumentParser("d1", description="this is a test program")
    parser.add_argument("-w", dest="opt_w", required=True)
    args = parser.parse_args()
    print(args.opt_w)