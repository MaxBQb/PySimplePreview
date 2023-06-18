import datetime
import subprocess
import sys
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ModifiedTracker(FileSystemEventHandler):
    def __init__(self, callback):
        self.last_event = 0
        self.cooldown = 1
        self.callback = callback

    def on_modified(self, event):
        if not event.src_path.endswith(".py"):
            return
        time = datetime.datetime.now().timestamp()
        if self.last_event + self.cooldown >= time:
            return
        self.last_event = time
        super().on_modified(event)
        print(event)
        self.callback(event.src_path)


class Runner:
    def __init__(self):
        self._process: subprocess.Popen = None
        self._path = None

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value):
        if self._path:
            self._process.kill()
        self._path = value
        self._process = subprocess.Popen([sys.executable, value, "preview"])


def main():
    path = "."
    runner = Runner()

    def set_path(x):
        runner.path = x

    event_handler = ModifiedTracker(set_path)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
