import asyncio
import dataclasses
import inspect
import logging
import sys
from typing import Any, Callable, Optional, TextIO

from .core import DATA_FINISH_MARKER, Actor, Proc, Sink, Source, receiver


class Ticker(Source, Actor):
    """Source actor of regular time based events."""

    @dataclasses.dataclass
    class Options:
        timeout: float = 1
        '''Timeout between events in seconds.'''

        limit: Optional[int] = None
        '''Number of events to be generated.'''

    async def main(self):
        limit = self.config.limit
        while limit or limit is None:
            await self.send(None)
            await asyncio.sleep(self.config.timeout)
            if limit is not None:
                limit -= 1
        await self.send(DATA_FINISH_MARKER)


class Counter(Proc, Actor):
    """Interim counting actor.

    This actor counts incoming events and sending counter to its
    output on each event.
    """

    async def main(self):
        counter = 0
        async for _ in receiver(self.receive):
            await self.send(counter)
            counter += 1
        await self.send(DATA_FINISH_MARKER)


class Printer(Sink, Actor):
    """Sink actor printing each incoming event to output stream."""

    @dataclasses.dataclass
    class Arguments:
        stream: TextIO = sys.stdout
        '''The stream to be used for printing.'''

    async def main(self):
        async for data in receiver(self.receive):
            print(data, file=self.config.stream)


class Null(Sink, Actor):
    """Sink actor eating all incoming events."""

    async def main(self):
        async for _ in receiver(self.receive):
            pass


class Logger(Proc, Actor):
    """Sink/Interim actor sending events to `logging` infrastructure."""

    @dataclasses.dataclass
    class Options:
        logger: Optional[str] = None
        '''Logger name.'''

        level: int = logging.DEBUG
        '''Log level.'''

    async def main(self):
        logger = logging.getLogger(self.config.logger)
        async for data in receiver(self.receive):
            logger.log(self.config.level, data)
            await self.send(data, safe=True)
        await self.send(DATA_FINISH_MARKER)


class Applicator(Proc, Actor):
    """Interim actor applying specific function to events."""

    @dataclasses.dataclass
    class Options:
        thread: bool = False
        '''Execute function in seperate thread.

        This option is usefull for io-bound tasks to be offloaded from main
        asyncio thread to avoid blocking.
        '''

    @dataclasses.dataclass
    class Arguments(Options):
        func: Callable[[Any], Any] = None
        '''Function to be applied on events.'''

    async def main(self):
        async for data in receiver(self.receive):
            if self.config.thread:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(
                    None,
                    self.config.func,
                    data,
                )
            else:
                result = self.config.func(data)
                if asyncio.iscoroutine(result):
                    result = asyncio.ensure_future(result)
                if asyncio.isfuture(result):
                    result = await result
            if inspect.isasyncgen(result):
                async for item in result:
                    await self.send(item)
            elif inspect.isgenerator(result):
                for item in result:
                    await self.send(item)
            else:
                await self.send(result)
        await self.send(DATA_FINISH_MARKER)


class Filter(Proc, Actor):
    """Interim actor filtering events with predicate."""

    @dataclasses.dataclass
    class Arguments:
        func: Callable[[Any], bool]
        '''Function to be applied on events.'''

    async def main(self):
        async for data in receiver(self.receive):
            if self.config.func(data):
                await self.send(data)
        await self.send(DATA_FINISH_MARKER)


class Tee(Proc, Actor):
    """Interim actor feeding events to additional Sink."""

    @dataclasses.dataclass
    class Arguments:
        sink: Sink
        '''Function to be applied on events.'''

    queue: asyncio.Queue = None

    async def main(self):
        async def send(data):
            await asyncio.gather(
                self.queue.put(data),
                self.send(data),
            )
        async for data in receiver(self.receive):
            await send(data)
        await send(DATA_FINISH_MARKER)

    def start(self):
        self.queue = asyncio.Queue(maxsize=1)
        self.config.sink.getter = self.queue.get
        return asyncio.gather(
            self.config.sink.start(),
            super().start(),
        )

    def __repr__(self):
        return f'Tee({self.config.sink})'


class List(Source, Actor):
    """Source actor producing events from provided list."""

    @dataclasses.dataclass
    class Options:
        data: list = ()
        '''List of objects to be generated as events.'''

    async def main(self):
        for element in self.config.data:
            await self.send(element)
        await self.send(DATA_FINISH_MARKER)
