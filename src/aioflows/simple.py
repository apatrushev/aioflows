import asyncio
import logging
import sys

from .core import DATA_FINISH_MARKER, Actor, Proc, Sink, Source, receiver


class Ticker(Source, Actor):
    def __init__(self, timeout=1, limit=None):
        super().__init__()
        self.timeout = timeout
        self.limit = limit

    async def main(self):
        while self.limit or self.limit is None:
            await self.send(None)
            await asyncio.sleep(self.timeout)
            if self.limit is not None:
                self.limit -= 1
        await self.send(DATA_FINISH_MARKER)


class Counter(Proc, Actor):
    async def main(self):
        counter = 0
        async for _ in receiver(self.receive):
            await self.send(counter)
            counter += 1
        await self.send(DATA_FINISH_MARKER)


class Printer(Sink, Actor):
    def __init__(self, stream=sys.stdout):
        super().__init__()
        self.stream = stream

    async def main(self):
        async for data in receiver(self.receive):
            print(data, file=self.stream)


class Null(Sink, Actor):
    async def main(self):
        async for _ in receiver(self.receive):
            pass


class Logger(Proc, Actor):
    def __init__(self, logger=None, level=logging.DEBUG):
        super().__init__()
        self.logger = logging.getLogger(logger)
        self.level = level

    async def main(self):
        async for data in receiver(self.receive):
            self.logger.log(self.level, data)
            await self.send(data)
        await self.send(DATA_FINISH_MARKER)


class Applicator(Proc, Actor):
    def __init__(self, func, thread=False):
        super().__init__()
        self.func = func
        self.thread = thread

    async def main(self):
        async for data in receiver(self.receive):
            if self.thread:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, self.func, data)
            else:
                result = self.func(data)
                if asyncio.iscoroutine(result):
                    result = asyncio.ensure_future(result)
                if asyncio.isfuture(result):
                    result = await result
            await self.send(result)
        await self.send(DATA_FINISH_MARKER)


class Filter(Proc, Actor):
    def __init__(self, func):
        super().__init__()
        self.func = func

    async def main(self):
        async for data in receiver(self.receive):
            if self.func(data):
                await self.send(data)
        await self.send(DATA_FINISH_MARKER)


class Tee(Proc, Actor):
    def __init__(self, other):
        super().__init__()
        self.other = other
        self.queue = asyncio.Queue(maxsize=1)

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
        self.other.getter = self.queue.get
        return asyncio.gather(
            self.other.start(),
            super().start(),
        )


class List(Source, Actor):
    def __init__(self, data):
        super().__init__()
        self.data = data

    async def main(self):
        for element in self.data:
            await self.send(element)
        await self.send(DATA_FINISH_MARKER)
