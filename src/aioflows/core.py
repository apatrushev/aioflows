import abc
import asyncio
import dataclasses

import pydantic
from cached_property import cached_property


DATA_FINISH_MARKER = object()


async def receiver(receive):
    while True:
        data = receive()
        if asyncio.iscoroutine(data):
            data = asyncio.ensure_future(data)
        if asyncio.isfuture(data):
            data = await data
        if data == DATA_FINISH_MARKER:
            break
        yield data


class ActorSyntaxError(RuntimeError):
    def __init__(self, name):
        super().__init__(
            f'please do not use __init__ or config in actors: "{name}"',
        )


class ActorArgumentsError(RuntimeError):
    def __init__(self):
        super().__init__(
            "please do not use positional arguments in actor's init",
        )


class ActorConfigurationError(RuntimeError):
    def __init__(self, option):
        super().__init__(
            f'actor option "{option}" is not defined',
        )


class ActorMeta(abc.ABCMeta):
    """Helper class to implement syntactic sugar for actors."""
    def __new__(cls, name, bases, dct):
        if (
            '__init__' in dct and (
                dct['__init__'].__module__ != __name__ or
                name != 'Actor'
            )
        ) or 'config' in dct:
            raise ActorSyntaxError(name)
        if 'Options' in dct and 'Arguments' not in dct:
            dct['Arguments'] = (
                dataclasses.make_dataclass(
                    'Arguments',
                    (),
                    bases=(dct['Options'],),
                )
            )
        if 'main' in dct and not isinstance(dct['main'], cached_property):
            # automatically wraps actors main to cached property
            # to avoid multiple calls and use it in cancellation
            dct['main'] = cached_property(dct['main'])
        instance = super().__new__(cls, name, bases, dct)
        return instance


class Actor(abc.ABC, metaclass=ActorMeta):
    """Actors base class.

    Implements actors connection magic and flow control.
    """
    def __init__(self, *args, **kwargs):
        super().__init__()
        if args:
            raise ActorArgumentsError()
        self.config = (
            self.Arguments(**kwargs)
            if (
                hasattr(self, 'Arguments') and
                dataclasses.fields(self.Arguments)
            ) else
            None
        )

    def start(self):
        return self.main

    @cached_property
    @abc.abstractmethod
    async def main(self):
        """Main actor function.

        Should be implemented in actor to do its job. This method
        automatically wrapped to cached_property by ActorMeta to
        avoid multiple calls of actor main function.
        """
        pass

    def __rshift__(self, other):
        """Connect actors.

        Creates new Actor representing connection of arguments.

        Args:
            other: right hand side Actor to join

        Returns:
            A new Actor representing connected flow of join
            operation arguments. Can be used in further join
            operations or started alone if completed.
        """
        return Connector(left=self, right=other)

    @property
    def options(self):
        if hasattr(self, 'Options'):
            options = pydantic.tools.schema_of(self.Options)
            props = options['definitions']['Options']['properties']
            for k, v in props.items():
                v['default'] = getattr(self.config, k)
            return (options,)
        return ()

    @staticmethod
    async def mover(getter, putter):
        while True:
            data = getter()
            if asyncio.iscoroutine(data):
                data = asyncio.ensure_future(data)
            if asyncio.isfuture(data):
                data = await data
            result = putter(data)
            if asyncio.iscoroutine(result):
                result = asyncio.ensure_future(result)
            if asyncio.isfuture(result):
                result = await result
            if data is DATA_FINISH_MARKER:
                break

    def configure(self, options):
        """Configures actor with provided options."""
        options, = options
        for name, value in options.items():
            if not hasattr(self.Options, name):
                raise ActorConfigurationError(name)
            setattr(self.config, name, value)


class Sink:
    """Base class for Sinks."""

    getter: callable = None

    def receive(self):
        """Get incoming data from input queue.

        Helper method to be used in Actors to get incoming data.
        """
        return self.getter()


class Source:
    """Base class for Sources."""

    putter: callable = None

    def send(self, value):
        """Send data to output queue.

        Helper method to be used in Actors to send data to output queue.
        """
        return self.putter(value)


class Proc(Source, Sink):
    """Base class for Procs (both Sink and Source)."""

    def send(self, value, safe=False):
        async def stub():
            return None
        return (
            super().send(value)
            if self.putter is not None or not safe else
            stub()
        )


class Connector(Proc, Actor):
    """Connector class for actors.

    Main class implementing the libary idea of actors connection.
    During startup it creates asyncio.Queue and connects it to legs.
    Also it implements magic to connect getter and putter to outside.
    asyncio.Queue instantiated with maxsize=1.
    If you need interim buffering between actors - you need to use
    buffering actor between them otherwise left actor will be locked
    if right one does not process data fast enough.
    """

    @dataclasses.dataclass
    class Arguments:
        left: Source
        right: Sink

    @property
    def putter(self):
        """Connects outgoing queue of right to external world."""
        return self.config.right.putter

    @putter.setter
    def putter(self, value):
        self.config.right.putter = value

    @property
    def getter(self):
        """Connects incoming queue of left to external world."""
        return self.config.left.getter

    @getter.setter
    def getter(self, value):
        self.config.left.getter = value

    @property
    def options(self):
        options = (*self.config.left.options, *self.config.right.options)
        return options if options else ()

    def configure(self, options):
        """Configures legs with provided options."""
        left = len(self.config.left.options)
        if options[:left]:
            self.config.left.configure(options[:left])
        if options[left:]:
            self.config.right.configure(options[left:])

    def start(self):
        """Overrides main Actor flow to connect legs."""
        queue = asyncio.Queue(1)
        self.config.left.putter = queue.put
        self.config.right.getter = queue.get
        return super().start()

    async def main(self):
        """Overrides main Actor flow to await both legs."""
        await asyncio.gather(
            self.config.left.start(),
            self.config.right.start(),
        )

    def __repr__(self):
        return f'{self.config.left} >> {self.config.right}'
