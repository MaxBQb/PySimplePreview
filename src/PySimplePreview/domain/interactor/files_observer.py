import contextlib
import logging
import time
from pathlib import Path
from queue import Queue

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from PySimplePreview.data.config_storage import ConfigStorage
from PySimplePreview.domain.interactor.abc.files_observer import ProjectObserver
from PySimplePreview.domain.model.config import Config, is_package_project
from PySimplePreview.domain.model.event import InvokableEvent


class FilesObserver(FileSystemEventHandler):
    def __init__(self, root_path: str):
        self.last_event = 0
        self.events = {}
        self.cooldown = 50
        self.queue = Queue()
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
        self.queue.put_nowait(event.src_path)


class ProjectObserverImpl(ProjectObserver):
    def __init__(self, config: ConfigStorage):
        super().__init__()
        self.on_project_update = InvokableEvent.from_base(self.on_project_update)
        self._observer: FilesObserver = None
        self._config_storage = config
        self._last_project: Path = None
        self._is_package = False
        self._config_storage.on_update += self._on_update

    def _callback(self, path: str):
        if self._is_package or self._last_project.samefile(path):
            self.on_project_update.invoke(Path(path), False)

    def close(self):
        if self._observer:
            self._observer.stop()
            self._observer = None

    def _single_module_track(self, path: str):
        if self._last_project.samefile(path):
            self._callback(path)

    def start(self):
        if not self._last_project:
            return
        is_package = is_package_project(self._last_project)
        self._is_package = is_package
        if not self._observer:
            self._observer = FilesObserver(
                str(self._last_project.parent if self._last_project.is_file() else self._last_project)
            )
        self._observer.start()
        project_name = self._last_project.parent.name if is_package else self._last_project.stem
        logging.info("Start watching " + ("package" if is_package else "single module")
                     + f" '{project_name}'...")

    def _on_update(self, config: Config):
        if config.current_project and self._last_project != config.current_project:
            self._last_project = config.current_project
            self.close()
            self.on_project_update.invoke(config.current_project, True)
            self.start()

    def dispatch_events(self):
        if not self._observer:
            return
        while not self._observer.queue.empty():
            data = self._observer.queue.get_nowait()
            self._callback(data)

    @contextlib.contextmanager
    def track(self):
        try:
            self._on_update(self._config_storage.config)
            yield
        finally:
            self.close()
