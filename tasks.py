import pathlib

import invoke
from spherical.dev.tasks import test  # noqa: F401
from spherical.dev.tasks import clean, flake, isort  # noqa: F401
from spherical.dev.tasks import pypi_release as release  # noqa: F401


@invoke.task
def examples(ctx: invoke.Context):
    folder = pathlib.Path() / 'src' / 'examples'
    for script in folder.iterdir():
        if script.is_dir():
            continue
        print(f'EXECUTE: {script}')
        try:
            result = ctx.run(f'python {script}', timeout=5)
            print(f'ERRORCODE: {result.exited}')
        except invoke.exceptions.CommandTimedOut:
            print('ERRORCODE: timeout')
        except invoke.exceptions.UnexpectedExit as exc:
            print(f'ERRORCODE: {exc.result.exited}')
