import asyncio
import socket
import sys
import time
import uuid

import aiohttp
import requests
from aioconsole.stream import ainput

from aioflows.core import Actor, mover
from aioflows.simple import Applicator, Printer, Sink, Tee
from aioflows.zeroconf import Zeroconf


def zc_station_info(data):
    action, (zc, type, name) = data
    info = zc.get_service_info(type, name)
    return (
        tuple(
            (host, info.port)
            for host in map(socket.inet_ntoa, info.addresses)
        ),

        {
            k.decode(): v.decode()
            for k, v in info.properties.items()
        },
    )


def device_token(local_token, data):
    try:
        addresses, properties = data
        response = requests.get(
            'https://quasar.yandex.net/glagol/token',
            headers={
                'Authorization': f'Oauth {local_token}',
            },
            params={
                'device_id': properties['deviceId'],
                'platform': properties['platform'],
            },
        )
        response.raise_for_status()
        return (addresses, properties, response.json()['token'])
    except BaseException:
        print('token receive error')


async def station_connect(data):
    ((host, port), *_), properties, token = data
    session = aiohttp.ClientSession()
    ws = await session.ws_connect(f'wss://{host}:{port}', ssl=False)
    request_id = str(uuid.uuid4())
    await ws.send_json({
        'conversationToken': token,
        'id': request_id,
        'payload': {'command': 'ping'},
        'sentTime': int(round(time.time() * 1000)),
    })
    while True:
        msg = (await ws.receive()).json()
        if msg.get('requestId', None) == request_id:
            if msg['status'] != 'SUCCESS':
                return None
            break
    return token, ws


async def say(ws, token, msg):
    await ws.send_json({
        'conversationToken': token,
        'id': str(uuid.uuid4()),
        'payload': {
            'command': 'sendText',
            'text': f"Повтори за мной '{msg}'",
        },
        'sentTime': int(round(time.time() * 1000)),
    })


class Alice(Sink, Actor):
    def __init__(self, next_message):
        super().__init__()
        self.ws = None
        self.next_message = next_message

    async def main(self):
        token, ws = await self.receive()
        await asyncio.gather(
            mover(
                ws.receive,
                lambda x: (__import__('pdb').set_trace()),
            ),
            mover(
                self.next_message,
                lambda x: say(ws, token, x),
            ),
        )


async def start(local_token=None):
    if local_token is None:
        raise RuntimeError('please provide yandex token')
    flow = (
        Zeroconf('_yandexio._tcp.local.')
        >> Tee(Printer())
        >> Applicator(zc_station_info)
        >> Applicator(lambda x: device_token(local_token, x), thread=True)
        >> Applicator(station_connect)
        >> Tee(Printer())
        >> Alice(lambda: ainput())
    )
    await flow.start()


asyncio.run(start(*sys.argv[1:]))
