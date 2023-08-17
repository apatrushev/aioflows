import asyncio

from aioflows.simple import Printer, Ticker


async def start():
    await (Ticker(timeout=0.1, limit=5) >> Printer()).start()


asyncio.run(start())
