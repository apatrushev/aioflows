import asyncio
import dataclasses
import threading
from typing import Any, Callable

import janus

from aioflows.core import Actor, Proc


class Thread(Proc, Actor):
    @dataclasses.dataclass
    class Arguments:
        func: Callable[
            [
                Callable[[], Any],
                Callable[[Any], None],
            ],
            None,
        ]

    q2t: janus.Queue
    t2q: janus.Queue

    def thread_main(self):
        try:
            self.config.func(self.q2t.sync_q.get, self.t2q.sync_q.put)
        finally:
            self.t2q.close()

    async def main(self):
        threading.Thread(target=self.thread_main, daemon=True).start()
        tasks = []
        if self.getter is not None:
            tasks.append(
                self.mover(
                    self.receive,
                    self.q2t.async_q.put,
                ),
            )
        if self.putter is not None:
            tasks.append(
                self.mover(
                    self.t2q.async_q.get,
                    self.send,
                ),
            )
        await asyncio.gather(*tasks)

    def start(self):
        self.q2t = janus.Queue(maxsize=1)
        self.t2q = janus.Queue(maxsize=1)
        return super().start()
