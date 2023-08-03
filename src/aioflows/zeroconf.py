import dataclasses
from typing import Optional

import zeroconf

from .core import Source
from .thread import Thread


class Listener(Source):
    def __init__(self, putter):
        super().__init__()
        self.putter = putter

    def remove_service(self, zeroconf, type, name):
        self.send(('remove', (zeroconf, type, name)))

    def add_service(self, zeroconf, type, name):
        self.send(('add', (zeroconf, type, name)))


class Zeroconf(Thread):

    @dataclasses.dataclass
    class Options:
        logger: Optional[str] = None
        '''Logger name.'''

    def __init__(self, service_type):
        super().__init__(self)
        self.service_type = service_type

    def __call__(self, getter, putter):
        zc = zeroconf.Zeroconf()
        try:
            browser = zeroconf.ServiceBrowser(
                zc,
                self.service_type,
                Listener(putter),
            )
            browser.join()
        finally:
            zc.close()
