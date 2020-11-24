from aioconsole.stream import ainput

from .core import Actor, Source


class Stdin(Source, Actor):
    async def main(self):
        while True:
            await self.send(await ainput())
