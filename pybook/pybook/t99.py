import contextlib


@contextlib.contextmanager
def file_ctx(name, mode):
    try:
        fs = open(name, mode)
        yield fs
    except Exception as e:
        raise e
    finally:
        print("close file ", name)
        fs.close()
