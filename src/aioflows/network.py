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
            inp, outp = None, None
            while True:
                if inp is None and self.getter is not None:
                    inp = asyncio.ensure_future(self.getter())
                if outp is None and self.putter is not None:
                    outp = asyncio.ensure_future(self.queue.get())
                done, pending = await asyncio.wait(
                    tuple(filter(None, (inp, outp))),
                    return_when=asyncio.FIRST_COMPLETED,
                )
                if inp in done:
                    transport.sendto(*inp.result())
                    inp = None
                if outp in done:
                    await self.send(outp.result())
                    outp = None
        finally:
            transport.close()
