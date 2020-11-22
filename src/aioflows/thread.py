import threading

import janus

from aioflows.core import Actor, Proc


class Thread(Proc, Actor):
    def __init__(self, func):
        super().__init__()
        self.func = func
        self.queue = janus.Queue(maxsize=1)

    def thread_main(self):
        self.func(None, self.queue.sync_q.put)

    async def main(self):
        threading.Thread(target=self.thread_main, daemon=True).start()
        while True:
            await self.send(await self.queue.async_q.get())
