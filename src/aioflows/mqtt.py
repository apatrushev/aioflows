import dataclasses

import aiomqtt

from aioflows.core import Actor, Source


class Subscriber(Source, Actor):
    @dataclasses.dataclass
    class Options:
        topic: str = '#'
        '''MQTT topic to be used by subscriber.'''

    @dataclasses.dataclass
    class Arguments(Options):
        client: aiomqtt.Client = None
        '''Client connection to broker.'''

    async def main(self):
        async with self.config.client.messages() as messages:
            await self.config.client.subscribe(self.config.topic)
            async for message in messages:
                await self.send(message)
