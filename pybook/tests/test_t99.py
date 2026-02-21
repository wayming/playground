import os

import pytest

import pybook.t99 as t


@pytest.fixture
def test_file_manager():
    filenames = []

    def _save_file_to_cleanup(file):
        filenames.append(file)
        return file

    yield _save_file_to_cleanup
    for f in filenames:
        if os.path.exists(f):
            print("remove file ", f)
            os.remove(f)


def test_t99_file_ctx(test_file_manager):
    test_file_manager("test_t99.txt")
    with t.file_ctx("test_t99.txt", "w") as f:
        f.write("test string")

    with t.file_ctx("test_t99.txt", "r") as f:
        print(type(f))
        for line in f:
            print(line)
