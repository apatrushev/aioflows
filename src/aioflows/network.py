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
        loop = asyncio.get_running_loop()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: self,
            **self.options,
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
