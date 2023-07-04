import enum
import typing
from abc import ABCMeta, abstractmethod
from pathlib import Path

from PySimplePreview.domain.model.event import Event


class ModuleLoader(metaclass=ABCMeta):
    class EventType(enum.Enum):
        ModuleLoaded = enum.auto()
        ModuleUnloaded = enum.auto()
        PackageReloadStarted = enum.auto()
        PackageReloadEnded = enum.auto()

    def __init__(self):
        self.on_event = Event[typing.Callable[[ModuleLoader.EventType, Path], None]]()

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def load_any(self, path):
        pass

    @abstractmethod
    def unload_all(self):
        pass

    @abstractmethod
    def reload_all(self, path):
        pass

    @abstractmethod
    def unload_module(self, path):
        pass

    @abstractmethod
    def load_module(self, path, reload):
        pass
