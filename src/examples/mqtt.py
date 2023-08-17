import asyncio
import sys

import aiomqtt

from aioflows.mqtt import Subscriber
from aioflows.simple import Applicator, Null


async def start(server='test.mosquitto.org', topic='#'):
    async with aiomqtt.Client(server) as client:
        flow = (
            Subscriber(client, topic=topic)
            >> Applicator(lambda x: (x.topic, x.payload))
            >> Null()
        )
        await flow.start()


asyncio.run(start(*sys.argv[1:]))
