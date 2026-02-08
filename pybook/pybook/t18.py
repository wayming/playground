import asyncio
import http.client
import traceback

import chardet


def read_url(url):
    try:
        conn = http.client.HTTPSConnection(url)
        conn.request("GET", "/")
        response = conn.getresponse()
        raw = response.read()

        encoding = response.getheader("Content-Encoding")
        if encoding == "gzip":
            import gzip

            raw = gzip.decompress(raw)
        elif encoding == "deflate":
            import zlib

            raw = zlib.decompress(raw)

        detected = chardet.detect(raw)
        final_encoding = detected["encoding"] or "utf-8"
        print(final_encoding)
        return (raw.decode(encoding=final_encoding, errors="ignore"), None)
    except Exception:
        return (None, traceback.format_exc())


async def crawler(urls):
    tasks = []
    async with asyncio.TaskGroup() as group:
        for url in urls:
            tasks.append(group.create_task(asyncio.to_thread(read_url, url)))
    return [t.result() for t in tasks]
