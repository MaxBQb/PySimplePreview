import contextlib
import time
from typing import Callable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class FilesObserver(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str], ...], root_path: str):
        self.last_event = 0
        self.events = {}
        self.cooldown = 50
        self.callback = callback
        self.observer = Observer()
        self.observer.schedule(self, root_path, recursive=True)

    def start(self):
        self.observer.start()

    def stop(self):
        self.observer.stop()
        self.observer.join()

    def on_modified(self, event):
        if not event.src_path.endswith(".py"):
            return
        timestamp = int(time.time()*1000)
        if event.src_path in self.events:
            last_timestamp = self.events[event.src_path]
            if last_timestamp + self.cooldown >= timestamp:
                return
        self.events[event.src_path] = timestamp
        super().on_modified(event)
        self.callback(event.src_path)

    @classmethod
    @contextlib.contextmanager
    def track(cls, callback: Callable[[str], ...], root_path: str):
        self = cls(callback, root_path)
        try:
            self.start()
            yield self
        finally:
            self.stop()
