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
async def test_printer():
    stream = io.StringIO()
    result = await asyncio.wait(
        (
            (List(data=[1, 2, 3]) >> Printer(stream=stream)).start(),
            asyncio.sleep(0.01),
        ),
        return_when=asyncio.FIRST_COMPLETED,
    )
    assert [k.done() and k.exception() for x in result for k in x] == [None, False]
    await finalize()


@pytest.mark.asyncio
async def test_tee_filter_applicator_null_logger():
    async def double(x):
        return x * 2

    stream = io.StringIO()
    pipeline = asyncio.create_task(
        (
            List(data=[1, 2, 3])
            >> Filter(func=lambda x: x > 1)
            >> Applicator(func=lambda x: x * 2, thread=True)
            >> Applicator(func=lambda x: x * 2)
            >> Applicator(func=double)
            >> Tee(sink=(Printer(stream=stream)))
            >> Tee(sink=(Logger() >> Null()))
            >> Tee(sink=Logger())
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
            >> Filter(func=lambda x: x % 2)
            >> Applicator(func=lambda x: x * 2)
            >> Printer(stream=stream)
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
            print(data, file=stream, flush=True)
            putter(data)
        putter(DATA_FINISH_MARKER)
        print('FINISHED', file=stream, flush=True)

    pipeline = asyncio.create_task(
        (
            List(data='abc')
            >> Thread(name='ThreadActor', func=func)
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

    assert stream.getvalue() == 'a\nb\nc\nFINISHED\n'
    assert not [x for x in threading.enumerate() if x.name == 'ThreadActor']


def test_positional_argument_exception():
    with pytest.raises(ActorArgumentsError):
        Printer(1)


def test_pinit_in_actor_exception():
    with pytest.raises(ActorSyntaxError):
        class Some(Actor):
            def __init__(self):
                pass
