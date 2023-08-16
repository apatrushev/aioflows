import asyncio
import io

import pytest

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


@pytest.mark.asyncio
async def test_printer():
    stream = io.StringIO()
    await asyncio.wait(
        (
            (List([1, 2, 3]) >> Printer(stream)).start(),
            asyncio.sleep(0.01),
        ),
        return_when=asyncio.FIRST_COMPLETED,
    )

    # we need this magic because we do not have
    # proper cancellation of flows yet
    tasks = []
    for task in asyncio.tasks.all_tasks():
        if task is not asyncio.current_task():
            task.cancel()
            tasks.append(task)
    await asyncio.wait(tasks)

    assert stream.getvalue() == '1\n2\n3\n'


@pytest.mark.asyncio
async def test_ticker_counter():
    stream = io.StringIO()
    await asyncio.wait(
        (
            (
                Ticker(timeout=0.001, limit=3)
                >> Counter()
                >> Printer(stream)
            ).start(),
            asyncio.sleep(0.1),
        ),
        return_when=asyncio.FIRST_COMPLETED,
    )

    # we need this magic because we do not have
    # proper cancellation of flows yet
    tasks = []
    for task in asyncio.tasks.all_tasks():
        if task is not asyncio.current_task():
            task.cancel()
            tasks.append(task)
    await asyncio.wait(tasks)

    assert stream.getvalue() == '0\n1\n2\n'


@pytest.mark.asyncio
async def test_tee_filter_applicator_null_logger():
    async def double(x):
        return x * 2

    stream = io.StringIO()
    await asyncio.wait(
        (
            (
                List([1, 2, 3])
                >> Filter(lambda x: x > 1)
                >> Applicator(lambda x: x * 2, thread=True)
                >> Applicator(lambda x: x * 2)
                >> Applicator(double)
                >> Tee(Printer(stream))
                >> Tee(Logger())
                >> Null()
            ).start(),
            asyncio.sleep(0.1),
        ),
        return_when=asyncio.FIRST_COMPLETED,
    )

    # we need this magic because we do not have
    # proper cancellation of flows yet
    tasks = []
    for task in asyncio.tasks.all_tasks():
        if task is not asyncio.current_task():
            task.cancel()
            tasks.append(task)
    await asyncio.wait(tasks)

    assert stream.getvalue() == '16\n24\n'
