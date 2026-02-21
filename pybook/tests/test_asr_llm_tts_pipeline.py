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
