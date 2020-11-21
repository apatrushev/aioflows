import asyncio
import logging

from spherical.dev.log import init_logging

from aioflows.samples import (
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
        Ticker()
        >> Logger('before', logging.DEBUG)
        >> Counter()
        >> Tee(
            Filter(lambda x: x % 2)
            >> Logger('tee', logging.DEBUG)
            >> Null()
        )
        >> Applicator(lambda x: x * 2)
        >> Logger('after', logging.ERROR)
        >> Printer()
    )
    await flow.start()


def main():
    init_logging()
    asyncio.run(start())


main()
