import asyncio
import logging
import sys

from .core import Actor, Proc, Sink, Source


class Ticker(Source, Actor):
    def __init__(self, timeout=1):
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
        self.logger = logging.getLogger(logger)
        self.level = level

    async def main(self):
        while True:
            data = await self.receive()
            self.logger.log(self.level, data)
            await self.send(data)


class Applicator(Proc, Actor):
    def __init__(self, func):
        self.func = func

    async def main(self):
        while True:
            await self.send(self.func(await self.receive()))


class Filter(Proc, Actor):
    def __init__(self, func):
        self.func = func

    async def main(self):
        while True:
            data = await self.receive()
            if self.func(data):
                await self.send(data)


class Tee(Proc, Actor):
    def __init__(self, other):
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
        self.data = list(data)

    async def main(self):
        while self.data:
            await self.send(self.data.pop(0))