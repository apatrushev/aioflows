import asyncio
import os
import socket
import struct

from aioflows.network import Udp
from aioflows.simple import Applicator, Printer


def parser(data):
    data, address = data
    return os.linesep.join((
        str(address),
        '-' * 40,
        data.decode(),
        '=' * 40,
    ))


async def start():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('239.255.255.250', 1900))
    mreq = struct.pack('=4sl', socket.inet_aton('239.255.255.250'), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    flow = (
        Udp(options=dict(sock=sock))
        >> Applicator(func=parser)
        >> Printer()
    )
    await flow.start()


asyncio.run(start())
