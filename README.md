# aioflow
[![Project Status: Concept – Minimal or no implementation has been done yet, or the repository is only intended to be a limited example, demo, or proof-of-concept.](https://www.repostatus.org/badges/latest/concept.svg)](https://www.repostatus.org/#concept)

This project aimed to implement helper library for building async applications in python based on concept of structured data flows and actors. The current stage is pure proof-of-concept and basement for discussion with colleagues and community. It is not inteded to be used in any production or even pet projects.

## Minimal working example
```python
import asyncio

from aioflows.samples import Printer, Ticker


async def start():
    await (Ticker() >> Printer()).start()


asyncio.run(start())
```

## Other examples
More examples can be found in [src/examples](src/examples).
