import asyncio

from .core import Actor, Proc


class Udp(Proc, Actor):
    def __init__(self, **kwargs):
        super().__init__()
        self.options = kwargs
        self.queue = asyncio.Queue(maxsize=1)

    def connection_made(self, transport):
        pass

    def connection_lost(self, exc):
        self.main.cancel()

    def datagram_received(self, data, addr):
        self.queue.put_nowait((data, addr))

    async def main(self):
        transport, protocol = await (
            asyncio.get_running_loop().create_datagram_endpoint(
                lambda: self,
                **self.options,
            )
        )
        try:
            await asyncio.gather(
                self.mover(
                    self.getter,
                    lambda x: transport.sendto(*x),
                ),
                self.mover(
                    self.queue.get,
                    self.send,
                ),
            )
        finally:
            transport.close()
