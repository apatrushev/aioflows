import abc
import asyncio

from cached_property import cached_property


class ActorMeta(abc.ABCMeta):
    """Helper class to implement syntactic sugar for actors."""
    def __new__(cls, name, bases, dct):
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
        return Connector(self, other)


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
    pass


class Connector(Proc, Actor):
    """Connector class for actors.

    Main class implementing the libary idea of actors connection.
    During startup it creates asyncio.Queue and connects it to legs.
    Also it implements magic to connect getter nad putter to outside.
    asyncio.Queue instantiated with maxsize=1.
    If you need interim buffering between actors - you need to use
    buffering actor between them otherwise left actor will be locked
    if right one does not process data fast enough.
    """
    def __init__(self, left, right):
        self.left = left
        self.right = right

    @property
    def putter(self):
        """Connects outgoing queue of right to external world."""
        return self.right.putter

    @putter.setter
    def putter(self, value):
        self.right.putter = value

    @property
    def getter(self):
        """Connects incoming queue of left to external world."""
        return self.left.getter

    @getter.setter
    def getter(self, value):
        self.left.getter = value

    def start(self):
        """Overrides main Actor flow to connect legs."""
        queue = asyncio.Queue(1)
        self.left.putter = queue.put
        self.right.getter = queue.get
        return super().start()

    async def main(self):
        """Overrides main Actor flow to await both legs."""
        await asyncio.gather(
            self.left.start(),
            self.right.start(),
        )
