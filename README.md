# aioflows
![Github Actions](https://github.com/apatrushev/aioflows/workflows/Spherical%20Python%20CI/badge.svg)
[![PyPI](https://img.shields.io/pypi/v/aioflows?logo=python&logoColor=%23cccccc)](https://pypi.org/project/aioflows)

<p>Asynchronous actors framework</p>

---

**Documentation**: <a href="https://aioflows.github.io" target="_blank">https://aioflows.github.io</a>

**Source**: <a href="https://github.com/apatrushev/aioflows" target="_blank">https://github.com/apatrushev/aioflows</a>

---
This project aims to create a support library for constructing asynchronous applications in Python, using the concept of structured data flows and actors. The current phase is purely a proof-of-concept and serves as a basis for discussion with colleagues and the community. It is not intended for use in any production or personal projects.


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
