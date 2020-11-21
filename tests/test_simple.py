import asyncio
import io

import pytest

from aioflows.simple import List, Printer


@pytest.mark.asyncio
async def test_printer():
    stream = io.StringIO()
    await asyncio.wait(
        (
            (List([1, 2, 3]) >> Printer(stream)).start(),
            asyncio.sleep(0.002),
        ),
        return_when=asyncio.FIRST_COMPLETED,
    )

    # we need this magic because we do not have
    # proper cancellation of flows yet
    tasks = []
    for task in asyncio.tasks.all_tasks():
        if task is not asyncio.Task.current_task():
            task.cancel()
            tasks.append(task)
    await asyncio.wait(tasks)

    assert stream.getvalue() == '1\n2\n3\n'
