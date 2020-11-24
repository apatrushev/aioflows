import asyncio
import logging
import sys

from .core import Actor, Proc, Sink, Source


class Ticker(Source, Actor):
    def __init__(self, timeout=1):
        super().__init__()
        self.timeout = timeout

    async def main(self):
        while True:
            await self.send(None)
            await asyncio.sleep(self.timeout)


class Counter(Proc, Actor):
    async def main(self):
        counter = 0
        while True:
            await self.receive()
            await self.send(counter)
            counter += 1


class Printer(Sink, Actor):
    def __init__(self, stream=sys.stdout):
        super().__init__()
        self.stream = stream

    async def main(self):
        while True:
            print(await self.receive(), file=self.stream)


class Null(Sink, Actor):
    async def main(self):
        while True:
            await self.receive()


class Logger(Proc, Actor):
    def __init__(self, logger=None, level=logging.DEBUG):
        super().__init__()
        self.logger = logging.getLogger(logger)
        self.level = level

    async def main(self):
        while True:
            data = await self.receive()
            self.logger.log(self.level, data)
            await self.send(data)


class Applicator(Proc, Actor):
    def __init__(self, func, thread=False):
        super().__init__()
        self.func = func
        self.thread = thread

    async def main(self):
        while True:
            data = await self.receive()
            if self.thread:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, self.func, data)
            else:
                result = self.func(data)
            if asyncio.iscoroutine(result):
                result = await result
            await self.send(result)


class Filter(Proc, Actor):
    def __init__(self, func):
        super().__init__()
        self.func = func

    async def main(self):
        while True:
            data = await self.receive()
            if self.func(data):
                await self.send(data)


class Tee(Proc, Actor):
    def __init__(self, other):
        super().__init__()
        self.other = other
        self.queue = asyncio.Queue(maxsize=1)

    async def main(self):
        while True:
            data = await self.receive()
            await self.queue.put(data)
            await self.send(data)

    def start(self):
        self.other.getter = self.queue.get
        return asyncio.gather(
            self.other.start(),
            super().start()
        )


class List(Source, Actor):
    def __init__(self, data):
        super().__init__()
        self.data = list(data)

    async def main(self):
        while self.data:
            await self.send(self.data.pop(0))
