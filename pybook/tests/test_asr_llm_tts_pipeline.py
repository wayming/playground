import asyncio
import unittest.mock

import pytest

import pybook.asr_llm_tts_pipeline as alt


async def atest_token_bucket():
    bucket = alt.TokenBucket(10, 1)
    await bucket.wait_for_token(5)
    stats = await bucket.get_stats()
    assert stats.allocated == 5
    assert stats.remaining == 5
    await bucket.wait_for_token(10)
    stats = await bucket.get_stats()
    assert stats.allocated == 15
    assert stats.remaining == 0


def test_token_bucket():
    asyncio.run(atest_token_bucket())


def test_KeyGenerator():
    gen = alt.KeyGenerator()
    assert len(gen("test_LLMCache_gen_key")) == 32


async def atest_LLMCache_cache_operations():
    cache = alt.LLMCache(100, 3)
    async with asyncio.TaskGroup() as g:
        g.create_task(cache.put("key1", "value1"))
        g.create_task(cache.put("key2", "value2"))
        g.create_task(cache.put("key3", "value3"))
    stats = await cache.get_stats()
    assert stats.hits == 0
    assert stats.misses == 0
    assert stats.size == 3

    tasks: list[asyncio.Task] = []
    async with asyncio.TaskGroup() as g:
        tasks.append(g.create_task(cache.get("key1")))
        tasks.append(g.create_task(cache.get("key2")))
        tasks.append(g.create_task(cache.get("key3")))
    assert [t.result() for t in tasks] == ["value1", "value2", "value3"]

    stats = await cache.get_stats()
    assert stats.hits == 3
    assert stats.misses == 0
    assert stats.size == 3

    await asyncio.sleep(5)

    async with asyncio.TaskGroup() as g:
        g.create_task(cache.get("key1"))
        g.create_task(cache.get("key2"))
        g.create_task(cache.get("key3"))
    stats = await cache.get_stats()
    assert stats.hits == 3
    assert stats.misses == 3
    assert stats.size == 0


def test_LLMCache_cache_operations():
    asyncio.run(atest_LLMCache_cache_operations())


async def atest_in_flight_deduper():
    duper = alt.InFlightDeduper()
    tasks: list[asyncio.Task] = []

    async def worker(x, y):
        return x + y

    async with asyncio.TaskGroup() as tg:
        tasks.append(tg.create_task(duper(worker, "param1", "param2")))
        tasks.append(tg.create_task(duper(worker, "param1", "INVALID")))

    for t in tasks:
        print(t.result())
        assert t.result() == "param1param2"


def test_in_flight_depuer():
    asyncio.run(atest_in_flight_deduper())


async def atest_llm_cache_hit():
    cache = alt.LLMCache(100, 5)
    await cache.put("input1", "output1")
    await cache.put("input2", "output2")
    llm = alt.LLM(cache)
    assert await llm.call_retry("input1", 5) == "output1"
    stats = await cache.get_stats()
    assert stats.hits == 1


async def atest_llm_miss():
    cache = alt.LLMCache(100, 5)
    await cache.put("input1", "output1")
    await cache.put("input2", "output2")
    llm = alt.LLM(cache)
    assert await llm.call_retry("input3", 5) == hash("input3")
    stats = await cache.get_stats()
    assert stats.hits == 0


def test_llm_cache():
    asyncio.run(atest_llm_cache_hit())
    asyncio.run(atest_llm_miss())


@pytest.mark.asyncio
async def atest_llm_retry_succeed():
    cache = alt.LLMCache(100, 5)
    llm = alt.LLM(cache)
    with unittest.mock.patch.object(
        llm,
        "call",
        new=unittest.mock.AsyncMock(
            side_effect=[TimeoutError(), TimeoutError(), hash("input1")]
        ),
    ):
        assert await llm.call_retry("input1", 5) == hash("input1")

    stats = await cache.get_stats()
    assert stats.misses == 3


@pytest.mark.asyncio
async def atest_llm_retry_timeout():
    cache = alt.LLMCache(100, 5)
    llm = alt.LLM(cache)
    with (
        unittest.mock.patch.object(
            llm,
            "call",
            new=unittest.mock.AsyncMock(side_effect=TimeoutError),
        ),
        pytest.raises(TimeoutError),
    ):
        await llm.call_retry("input1", 5)

    stats = await cache.get_stats()
    assert stats.misses == 4  # retry 3 times


def test_llm_retry():
    asyncio.run(atest_llm_retry_succeed())
    asyncio.run(atest_llm_retry_timeout())
