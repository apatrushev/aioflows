import dataclasses

import aiomqtt

from aioflows.core import Actor, Source


class Subscriber(Source, Actor):
    @dataclasses.dataclass
    class Options:
        topic: str = '#'
        '''Execute function in seperate thread.

        This option is usefull for io-bound tasks to be offloaded from main
        asyncio thread to avoid blocking.
        '''

    @dataclasses.dataclass
    class Arguments(Options):
        client: aiomqtt.Client = None
        '''Client connection to broker.'''

    async def main(self):
        async with self.config.client.messages() as messages:
            await self.config.client.subscribe(self.config.topic)
            async for message in messages:
                await self.send(message)
