import aiohttp
import asyncio

links = [
    "https://python.org",
    "https://docs.python.org",
    "https://peps.python.org",
]

async def read_page(link: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(link) as response:
                return await response.text()
        except Exception as e:
            print(e)

def write_html(text: str, file_name: str):
    try:
        with open(file_name, "w", encoding="UTF-8") as f:
            f.write(text)
    except Exception as e:
        print(e)

def count_words(text:str):
    return len(text.strip().split())

async def process_link(link:str, file_name:str, counts: list):
    results = await read_page(link)
    if results:
        write_task = asyncio.create_task(asyncio.to_thread(write_html, results, file_name))
        count_task = asyncio.create_task(asyncio.to_thread(count_words, results))
        _, count = await asyncio.gather(write_task, count_task)
        counts[link] = count
    
async def main():
    counts = {}
    try:
        async with asyncio.TaskGroup() as group:
            for idx, link in enumerate(links):
                group.create_task(process_link(link, str(idx) + ".log", counts))
    except* Exception as eg:
        print(eg.exceptions)

    for k, v in counts.items():
        print(k, " => ", v)

asyncio.run(main())