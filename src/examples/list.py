import asyncio

from aioflows.simple import List, Printer


async def start():
    await (List(data=[1, 2, 3]) >> Printer()).start()


asyncio.run(start())
