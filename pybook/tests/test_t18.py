import asyncio

import pybook.t18 as t


def test_crawler():
    urls = ["www.python.org", "wrong-url-test.com"]
    results = asyncio.run(t.crawler(urls))
    for url, (content, error) in zip(urls, results):
        print(f"{url} - {error} - {content}")
