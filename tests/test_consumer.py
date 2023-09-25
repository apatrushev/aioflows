import io

import pytest

from aioflows.simple import Consumer, Counter, Ticker


@pytest.mark.asyncio
async def test_consumer_simple(helpers):
    stream = io.StringIO()

    def func(msg):
        print(msg, file=stream, flush=True)

    pipeline = (
        Ticker(limit=2, timeout=0.01)
        >> Counter()
        >> Consumer(func=func)
    )
    await helpers.execute(pipeline)

    assert stream.getvalue() == '0\n1\n'


@pytest.mark.asyncio
async def test_consumer_generator(helpers):
    stream = io.StringIO()

    def func(msg):
        while True:
            print(msg, file=stream, flush=True)
            msg = yield

    pipeline = (
        Ticker(limit=2, timeout=0.01)
        >> Counter()
        >> Consumer(func=func)
    )
    await helpers.execute(pipeline)

    assert stream.getvalue() == '0\n1\n'


@pytest.mark.asyncio
async def test_consumer_coro(helpers):
    stream = io.StringIO()

    async def func(msg):
        print(msg, file=stream, flush=True)

    pipeline = (
        Ticker(limit=2, timeout=0.01)
        >> Counter()
        >> Consumer(func=func)
    )
    await helpers.execute(pipeline)

    assert stream.getvalue() == '0\n1\n'


@pytest.mark.asyncio
async def test_consumer_asyncgen(helpers):
    stream = io.StringIO()

    async def func(msg):
        while True:
            print(msg, file=stream, flush=True)
            msg = yield

    pipeline = (
        Ticker(limit=2, timeout=0.01)
        >> Counter()
        >> Consumer(func=func)
    )
    await helpers.execute(pipeline)

    assert stream.getvalue() == '0\n1\n'
