import asyncio

from aioflows.network import Udp
from aioflows.simple import Printer, Tee


async def start():
    udp = Udp(
        options=dict(
            local_addr=('127.0.0.1', 5353),
            reuse_port=True,
        ),
    )
    await (udp >> Tee(sink=Printer()) >> udp).start()


asyncio.run(start())
