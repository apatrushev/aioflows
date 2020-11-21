import asyncio

from aioflows.simple import Printer, Ticker


async def start():
    await (Ticker() >> Printer()).start()


asyncio.run(start())
