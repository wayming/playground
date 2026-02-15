import asyncio

import pybook.t83 as t


def test_t83_pc_runner():
    asyncio.run(t.runner(100, 10, 10, 5))
