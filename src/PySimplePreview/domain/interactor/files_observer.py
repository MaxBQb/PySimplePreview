import contextlib
import time
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from src.PySimplePreview.data.config_storage import ConfigStorage
from src.PySimplePreview.domain.model.config import Config, is_package_project


class FilesObserver(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str], ...], root_path: str):
        self.last_event = 0
        self.events = {}
        self.cooldown = 50
        self.callback = callback
        self.observer = Observer()
        self.observer.schedule(self, root_path, recursive=True)

    def start(self):
        if not self.observer.is_alive():
            self.observer.start()

    def stop(self):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()

    def on_modified(self, event):
        if not event.src_path.endswith(".py"):
            return
        timestamp = int(time.time() * 1000)
        if event.src_path in self.events:
            last_timestamp = self.events[event.src_path]
            if last_timestamp + self.cooldown >= timestamp:
                return
        self.events[event.src_path] = timestamp
        super().on_modified(event)
        self.callback(event.src_path)


class ProjectObserver:
    _instance = None

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._observer: FilesObserver = None
        self.callback = lambda x: None
        self._config_storage = ConfigStorage.get()
        self._last_project: Path = None
        self._config_storage.on_update(self._on_update)

    def close(self):
        if self._observer:
            self._observer.stop()
            self._observer = None

    def _single_module_track(self, path: str):
        if self._last_project.samefile(path):
            self.callback(path)

    def start(self):
        if not self._last_project:
            return
        is_package = is_package_project(self._last_project)
        if not self._observer:
            self._observer = FilesObserver(
                self.callback if is_package else self._single_module_track,
                str(self._last_project.parent if self._last_project.is_file() else self._last_project)
            )
        self._observer.start()
        project_name = self._last_project.parent.name if is_package else self._last_project.stem
        print("Start watching", "package" if is_package else "single module",
              f"'{project_name}'...")

    def _on_update(self, config: Config):
        if config.current_project and self._last_project != config.current_project:
            self._last_project = config.current_project
            self.close()
            self.start()

    @contextlib.contextmanager
    def track(self, callback: Callable[[str], ...]):
        try:
            self.callback = callback
            self._on_update(self._config_storage.config)
            yield
        finally:
            self.close()
