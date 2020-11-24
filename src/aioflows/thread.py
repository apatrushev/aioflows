import asyncio
import threading

import janus

from aioflows.core import Actor, Proc


class Thread(Proc, Actor):
    def __init__(self, func):
        super().__init__()
        self.func = func
        self.q2t = janus.Queue(maxsize=1)
        self.t2q = janus.Queue(maxsize=1)

    def thread_main(self):
        self.func(self.q2t.sync_q.get, self.t2q.sync_q.put)

    async def main(self):
        threading.Thread(target=self.thread_main, daemon=True).start()
        tasks = []
        if self.getter is not None:
            tasks.append(
                self.mover(
                    self.receive,
                    self.q2t.async_q.put,
                )
            )
        if self.putter is not None:
            tasks.append(
                self.mover(
                    self.t2q.async_q.get,
                    self.send,
                )
            )
        await asyncio.gather(*tasks)
