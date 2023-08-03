import asyncio
import sys

import aiomqtt

from aioflows.mqtt import Subscriber
from aioflows.simple import Applicator, Null, Printer


async def start(output='0', server='test.mosquitto.org', topic='#'):
    output = int(output)
    async with aiomqtt.Client(server) as client:
        flow = (
            Subscriber(client=client, topic=topic)
            >> Applicator(func=lambda x: (x.topic, x.payload))
            >> (Printer() if output else Null())
        )
        await flow.start()


asyncio.run(start(*sys.argv[1:]))
