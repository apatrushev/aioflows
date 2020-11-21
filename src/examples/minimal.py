import asyncio

from aioflows.samples import Printer, Ticker


async def start():
    await (Ticker() >> Printer()).start()


asyncio.run(start())
