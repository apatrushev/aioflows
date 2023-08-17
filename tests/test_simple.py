import asyncio
import io

import pytest

from aioflows.core import DATA_FINISH_MARKER
from aioflows.simple import (
    Applicator,
    Counter,
    Filter,
    List,
    Logger,
    Null,
    Printer,
    Tee,
    Ticker,
)
from aioflows.thread import Thread


async def finalize():
    tasks = []
    for task in asyncio.tasks.all_tasks():
        if task is not asyncio.current_task():
            task.cancel()
            tasks.append(task)
    await asyncio.wait(tasks)


@pytest.mark.asyncio
async def test_tee_filter_applicator_null_logger():
    async def double(x):
        return x * 2

    stream = io.StringIO()
    pipeline = asyncio.create_task(
        (
            List([1, 2, 3])
            >> Filter(lambda x: x > 1)
            >> Applicator(lambda x: x * 2, thread=True)
            >> Applicator(lambda x: x * 2)
            >> Applicator(double)
            >> Tee(Printer(stream))
            >> Tee(Logger() >> Null())
            >> Tee(Logger())
            >> Null()
        ).start(),
    )
    await asyncio.wait(
        (
            pipeline,
            asyncio.sleep(1),
        ),
        return_when=asyncio.FIRST_COMPLETED,
    )
    assert pipeline.done()

    await finalize()
    assert stream.getvalue() == '16\n24\n'


@pytest.mark.asyncio
async def test_ticker_counter_printer_finishing():
    stream = io.StringIO()
    pipeline = asyncio.create_task(
        (
            Ticker(timeout=0.01, limit=5)
            >> Counter()
            >> Filter(lambda x: x % 2)
            >> Applicator(lambda x: x * 2)
            >> Printer(stream)
        ).start(),
    )
    await asyncio.wait(
        (
            pipeline,
            asyncio.sleep(1),
        ),
        return_when=asyncio.FIRST_COMPLETED,
    )
    assert pipeline.done()

    await finalize()
    assert stream.getvalue() == '2\n6\n'


@pytest.mark.asyncio
async def test_thread_printer():
    stream = io.StringIO()

    def func(getter, putter):
        while True:
            data = getter()
            if data == DATA_FINISH_MARKER:
                break
            print(data, file=stream)
            putter(data)
        putter(DATA_FINISH_MARKER)

    pipeline = asyncio.create_task(
        (
            List('abc')
            >> Thread(func)
            >> Null()
        ).start(),
    )
    await asyncio.wait(
        (
            pipeline,
            asyncio.sleep(1),
        ),
        return_when=asyncio.FIRST_COMPLETED,
    )
    assert pipeline.done()

    await finalize()
    assert stream.getvalue() == 'a\nb\nc\n'
