import typing
from abc import ABCMeta, abstractmethod
from pathlib import Path

from PySimplePreview.domain.model.event import Event


class ProjectObserver(metaclass=ABCMeta):
    def __init__(self):
        self.on_project_update = Event[typing.Callable[[Path, bool], None]]()

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def track(self):
        pass

    @abstractmethod
    def dispatch_events(self):
        pass
