from aioflows.core import Actor, Source


class Subscriber(Source, Actor):
    def __init__(self, client, topic):
        super().__init__()
        self.client = client
        self.topic = topic

    async def main(self):
        async with self.client.messages() as messages:
            await self.client.subscribe(self.topic)
            async for message in messages:
                await self.send(message)
