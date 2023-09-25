import io

import pytest

from aioflows.simple import Printer, Producer


@pytest.mark.asyncio
async def test_producer_generator(helpers):
    stream = io.StringIO()

    pipeline = (
        Producer(func=(x for x in range(3)))
        >> Printer(stream=stream)
    )
    await helpers.execute(pipeline)

    assert stream.getvalue() == '0\n1\n2\n'


@pytest.mark.asyncio
async def test_producer_generator_factory(helpers):
    stream = io.StringIO()

    pipeline = (
        Producer(func=lambda: (x for x in range(3)))
        >> Printer(stream=stream)
    )
    await helpers.execute(pipeline)

    assert stream.getvalue() == '0\n1\n2\n'


@pytest.mark.asyncio
async def test_producer_asyncgen(helpers):
    stream = io.StringIO()

    async def gen(x):
        for t in range(x):
            yield t

    pipeline = (
        Producer(func=gen(3))
        >> Printer(stream=stream)
    )
    await helpers.execute(pipeline)

    assert stream.getvalue() == '0\n1\n2\n'


@pytest.mark.asyncio
async def test_producer_asyncgen_factory(helpers):
    stream = io.StringIO()

    async def gen(x):
        for t in range(x):
            yield t

    pipeline = (
        Producer(func=lambda: gen(3))
        >> Printer(stream=stream)
    )
    await helpers.execute(pipeline)

    assert stream.getvalue() == '0\n1\n2\n'


@pytest.mark.asyncio
async def test_producer_single_value(helpers):
    stream = io.StringIO()

    pipeline = (
        Producer(func=lambda: 0)
        >> Printer(stream=stream)
    )
    await helpers.execute(pipeline)

    assert stream.getvalue() == '0\n'


@pytest.mark.asyncio
async def test_producer_single_value_async(helpers):
    stream = io.StringIO()

    async def func():
        return 1

    pipeline = (
        Producer(func=func)
        >> Printer(stream=stream)
    )
    await helpers.execute(pipeline)

    assert stream.getvalue() == '1\n'
