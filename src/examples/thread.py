import asyncio
import functools
import subprocess

from aioflows.simple import Applicator, Printer
from aioflows.thread import Thread


def shell_command(command, getter, putter):
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


async def start():
    flow = (
        Thread(functools.partial(shell_command, 'ls -l'))
        >> Applicator(lambda x: x.decode().rstrip())
        >> Printer()
    )
    await flow.start()


asyncio.run(start())
