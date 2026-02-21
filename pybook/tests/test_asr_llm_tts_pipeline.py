import asyncio

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


async def atest_LLMCache_gen_key():
    cache = alt.LLMCache(100, 10)
    assert len(await cache.gen_key("test_LLMCache_gen_key")) == 32


def test_LLMCache_gen_key():
    asyncio.run(atest_LLMCache_gen_key())


async def atest_LLMCache_cache_operations():
    cache = alt.LLMCache(100, 3)
    async with asyncio.TaskGroup() as g:
        g.create_task(cache.put("key1", "value1"))
        g.create_task(cache.put("key2", "value2"))
        g.create_task(cache.put("key3", "value3"))
    stats = await cache.get_stats()
    assert stats.hits == 0
    assert stats.misses == 3
    assert stats.size == 3

    tasks: list[asyncio.Task] = []
    async with asyncio.TaskGroup() as g:
        tasks.append(g.create_task(cache.get("key1")))
        tasks.append(g.create_task(cache.get("key2")))
        tasks.append(g.create_task(cache.get("key3")))
    assert [t.result() for t in tasks] == ["value1", "value2", "value3"]

    stats = await cache.get_stats()
    assert stats.hits == 3
    assert stats.misses == 3
    assert stats.size == 3

    await asyncio.sleep(5)

    async with asyncio.TaskGroup() as g:
        g.create_task(cache.get("key1"))
        g.create_task(cache.get("key2"))
        g.create_task(cache.get("key3"))
    stats = await cache.get_stats()
    assert stats.hits == 3
    assert stats.misses == 6
    assert stats.size == 0


def test_LLMCache_cache_operations():
    asyncio.run(atest_LLMCache_cache_operations())
