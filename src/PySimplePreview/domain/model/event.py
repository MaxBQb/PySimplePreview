import enum
import typing

F = typing.TypeVar("F", bound=typing.Callable[..., typing.Any])


class Listener(typing.Generic[F]):
    class Priority(enum.IntEnum):
        Highest = enum.auto()
        High = enum.auto()
        AboveNormal = enum.auto()
        Normal = enum.auto()
        BelowNormal = enum.auto()
        Low = enum.auto()
        Lowest = enum.auto()

    def __init__(self, function: F, priority: int = Priority.Normal):
        self.listener = function
        self.priority = priority


class Event(typing.Generic[F]):
    def __init__(self):
        self._listeners = dict[int, Listener[F]]()

    def subscribe(self, listener: F | Listener[F]):
        if not isinstance(listener, Listener):
            listener = Listener(listener)
        self._listeners[id(listener.listener)] = listener
        return self

    def unsubscribe(self, listener: F | Listener[F]):
        if isinstance(listener, Listener):
            listener = listener.listener
        del self._listeners[id(listener)]
        return self

    def __bool__(self):
        return bool(self._listeners)

    def __len__(self):
        return len(self._listeners)

    __iadd__ = subscribe
    __isub__ = unsubscribe


class InvokableEvent(Event[F]):
    @property
    def base(self: 'InvokableEvent[F]') -> Event[F]:
        return self

    @property
    def invoke(self) -> F:
        return self  # type: ignore

    def __call__(self, *args, **kwargs):
        for listener in sorted(self._listeners.values(), key=lambda x: x.priority):
            listener.listener(*args, **kwargs)

    @staticmethod
    def from_base(base: Event[F]) -> 'InvokableEvent[F]':
        event = InvokableEvent[F]()
        event._listeners = base._listeners
        return event
