import asyncio

import pytest


class Helpers:
    @staticmethod
    async def finalize():
        tasks = []
        for task in asyncio.tasks.all_tasks():
            if task is not asyncio.current_task():
                task.cancel()
                tasks.append(task)
        await asyncio.wait(tasks)

    @staticmethod
    async def execute(pipeline):
        pipeline = asyncio.create_task(pipeline.start())
        await asyncio.wait(
            (
                pipeline,
                asyncio.ensure_future(asyncio.sleep(1)),
            ),
            return_when=asyncio.FIRST_COMPLETED,
        )
        assert pipeline.done()
        await Helpers.finalize()
        return pipeline.result()


@pytest.fixture
def helpers():
    return Helpers
