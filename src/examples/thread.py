import asyncio
import functools
import subprocess

from aioflows.core import DATA_FINISH_MARKER
from aioflows.simple import Applicator, Printer
from aioflows.thread import Thread


def shell_command(command, _, putter):
    proc = subprocess.Popen(
        command.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        putter(line)
    putter(DATA_FINISH_MARKER)


async def start():
    flow = (
        Thread(func=functools.partial(shell_command, 'ls -l'))
        >> Applicator(func=lambda x: x.decode().rstrip())
        >> Printer()
    )
    await flow.start()


asyncio.run(start())
