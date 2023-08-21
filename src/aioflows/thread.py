import asyncio
import dataclasses
import threading
from typing import Any, Callable, Optional

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
        name: Optional[str] = None

    q2t: janus.Queue
    t2q: janus.Queue

    def thread_main(self):
        self.config.func(self.q2t.sync_q.get, self.t2q.sync_q.put)

    async def main(self):
        thread = threading.Thread(
            target=self.thread_main,
            daemon=True,
            name=self.config.name,
        )
        thread.start()
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
        self.q2t.close()
        self.t2q.close()
        thread.join()

    def start(self):
        self.q2t = janus.Queue(maxsize=1)
        self.t2q = janus.Queue(maxsize=1)
        return super().start()
