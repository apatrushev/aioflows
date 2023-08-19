# aioflows
[![Project Status: Concept – Minimal or no implementation has been done yet, or the repository is only intended to be a limited example, demo, or proof-of-concept.](https://www.repostatus.org/badges/latest/concept.svg)](https://www.repostatus.org/#concept)

This project aims to implement a helper library for building asynchronous applications in Python, based on the concept of structured data flows and actors. The current stage is pure proof-of-concept and basis for discussion with colleagues and community. It is not intended to be used in any production or even pet projects.

## Installation
 - local
```bash
pip install .
```

 - editable
```bash
pip install -e .
```

 - development
```bash
pip install -e .[dev]
```

 - examples dependencies
```bash
pip install -e .[examples]
```

 - all together
```bash
pip install -e .[dev,examples]
```

 - from github
```bash
pip install git+https://github.com/apatrushev/aioflows.git
```

## Minimal working example
```python
import asyncio

from aioflows.simple import Printer, Ticker


async def start():
    await (Ticker() >> Printer()).start()


asyncio.run(start())
```

## Udp echo example
```python
import asyncio

from aioflows.network import Udp
from aioflows.simple import Printer, Tee


async def start():
    udp = Udp(local_addr=('127.0.0.1', 5353), reuse_port=True)
    await (udp >> Tee(Printer()) >> udp).start()


asyncio.run(start())
```

You can test it with socat:
```bash
socat - UDP:localhost:5353
```

## Other examples
More examples can be found in [src/examples](https://github.com/apatrushev/aioflows/tree/master/src/examples).

## Usual development steps
Run checks and tests:
```bash
inv isort flake test
```

Run examples (all ERRORCODE's should be 0/OK or timeout at the moment):
```bash
inv examples | grep ERRORCODE
```

## Similar projects
I found existing solutions that are almost equal to this concept:
 - https://github.com/ReactiveX/RxPY
 - https://github.com/vxgmichel/aiostream
