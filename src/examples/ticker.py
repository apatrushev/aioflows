import asyncio
import logging

from spherical.dev.log import init_logging

from aioflows.simple import (
    Applicator,
    Counter,
    Filter,
    Logger,
    Null,
    Printer,
    Tee,
    Ticker,
)


async def start():
    flow = (
        Ticker(timeout=0.1, limit=3)
        >> Logger(logger='before', level=logging.DEBUG)
        >> Counter()
        >> Tee(
            sink=(
                Filter(func=lambda x: x % 2)
                >> Logger(logger='tee', level=logging.DEBUG)
                >> Null()
            ),
        )
        >> Applicator(func=lambda x: x * 2)
        >> Logger(logger='after', level=logging.ERROR)
        >> Printer()
    )
    await flow.start()


def main():
    init_logging()
    asyncio.run(start())


main()
