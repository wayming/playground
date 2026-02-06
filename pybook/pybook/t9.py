from contextlib import contextmanager


@contextmanager
def transaction():
    print("transaction begin")
    try:
        yield
        print("transaction commit")
    except Exception:
        print("transaction rollback")
        raise
    finally:
        print("transaction end")


def run():
    with transaction():
        print("insert")

    with transaction():
        raise Exception("primary key conflicts")
