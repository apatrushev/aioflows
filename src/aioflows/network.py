import asyncio
import dataclasses
from typing import Any, Dict

from .core import Actor, Proc


class Udp(Proc, Actor):
    queue: asyncio.Queue = None

    @dataclasses.dataclass
    class Options:
        options: Dict[str, Any] = None
        '''Socket options sended directly to `create_datagram_endpoint`.'''

    def connection_made(self, transport):
        pass

    def connection_lost(self, exc):
        self.main.cancel()

    def datagram_received(self, data, addr):
        self.queue.put_nowait((data, addr))

    async def main(self):
        loop = asyncio.get_running_loop()
        transport, _ = await loop.create_datagram_endpoint(
            lambda: self,
            **self.config.options,
        )
        try:
            tasks = []
            if self.getter is not None:
                tasks.append(self.mover(
                    self.receive,
                    lambda x: transport.sendto(*x),
                ))
            if self.putter is not None:
                tasks.append(self.mover(
                    self.queue.get,
                    self.send,
                ))
            await asyncio.gather(*tasks)
        finally:
            transport.close()

    def start(self):
        self.queue = asyncio.Queue(maxsize=1)
        return super().start()
