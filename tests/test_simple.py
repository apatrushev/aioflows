import asyncio
import io
import threading

import pytest

from aioflows.core import (
    DATA_FINISH_MARKER,
    Actor,
    ActorArgumentsError,
    ActorSyntaxError,
)
from aioflows.simple import (
    Applicator,
    Batcher,
    Counter,
    Filter,
    List,
    Logger,
    Null,
    Printer,
    Repeat,
    Take,
    Tee,
    Ticker,
)
from aioflows.thread import Thread


@pytest.mark.asyncio
async def test_printer(helpers):
    stream = io.StringIO()
    result = await asyncio.wait(
        list(map(asyncio.ensure_future, (
            (
                List(data=[0, 1, 2])
                >> Printer(stream=stream)
            ).start(),
            asyncio.sleep(0.01),
        ))),
        return_when=asyncio.FIRST_COMPLETED,
    )
    assert [k.done() and k.exception() for x in result for k in x] == [None, False]
    await helpers.finalize()

    assert stream.getvalue() == '0\n1\n2\n'


@pytest.mark.asyncio
async def test_tee_filter_applicator_null_logger(helpers):
    async def double(x):
        return x * 2

    stream = io.StringIO()
    pipeline = (
        List(data=[1, 2, 3])
        >> Filter(func=lambda x: x > 1)
        >> Applicator(func=lambda x: x * 2, thread=True)
        >> Applicator(func=lambda x: x * 2)
        >> Applicator(func=double)
        >> Tee(sink=Printer(stream=stream))
        >> Tee(sink=(Logger() >> Null()))
        >> Null()
    )
    await helpers.execute(pipeline)

    assert stream.getvalue() == '16\n24\n'


@pytest.mark.asyncio
async def test_ticker_counter_printer_finishing(helpers):
    stream = io.StringIO()

    pipeline = (
        Ticker(timeout=0.01, limit=5)
        >> Counter()
        >> Filter(func=lambda x: x % 2)
        >> Applicator(func=lambda x: x * 2)
        >> Printer(stream=stream)
    )
    await helpers.execute(pipeline)

    assert stream.getvalue() == '2\n6\n'


@pytest.mark.asyncio
async def test_thread_printer(helpers):
    stream = io.StringIO()

    def func(getter, putter):
        while True:
            data = getter()
            if data == DATA_FINISH_MARKER:
                break
            print(data, file=stream, flush=True)
            putter(data)
        putter(DATA_FINISH_MARKER)
        print('FINISHED', file=stream, flush=True)

    stream_out = io.StringIO()
    pipeline = (
        List(data='abc')
        >> Thread(name='ThreadActor', func=func)
        >> Batcher(size=2)
        >> Applicator(func=lambda x: ''.join(x))
        >> Printer(stream=stream_out)
    )
    await helpers.execute(pipeline)

    assert stream.getvalue() == 'a\nb\nc\nFINISHED\n'
    assert stream_out.getvalue() == 'ab\nc\n'
    assert not [x for x in threading.enumerate() if x.name == 'ThreadActor']


def test_positional_argument_exception():
    with pytest.raises(ActorArgumentsError):
        Printer(1)


def test_pinit_in_actor_exception():
    with pytest.raises(ActorSyntaxError):
        class Some(Actor):
            def __init__(self):
                pass


@pytest.mark.asyncio
async def test_appicator_generator(helpers):
    stream = io.StringIO()

    def generate(x):
        for i in range(x):
            yield i

    pipeline = (
        List(data=[1, 2, 3])
        >> Applicator(func=generate)
        >> Printer(stream=stream)
    )
    await helpers.execute(pipeline)

    assert stream.getvalue() == '0\n0\n1\n0\n1\n2\n'


@pytest.mark.asyncio
async def test_repeat(helpers):
    stream = io.StringIO()

    pipeline = (
        List(data='a')
        >> Repeat()
        >= Take(limit=2)
        >> Printer(stream=stream)
    )
    await helpers.execute(pipeline)

    assert stream.getvalue() == 'a\na\n'


@pytest.mark.asyncio
async def test_applicator_exception(helpers):
    stream = io.StringIO()

    pipeline = (
        Ticker(limit=2, timeout=0.01)
        >> Counter()
        >> Applicator(func=lambda x: 1 - x)
        >> Applicator(func=lambda x: 1 / x)
        >> Printer(stream=stream)
    )
    with pytest.raises(ZeroDivisionError):
        await helpers.execute(pipeline)

    assert stream.getvalue() == '1.0\n'
