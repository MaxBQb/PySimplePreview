import datetime
import glob
import importlib.util
import time
from queue import Queue
from typing import Callable

import PySimpleGUI as sg
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class ModifiedTracker(FileSystemEventHandler):
    def __init__(self, callback, ignore_files=[]):
        self.last_event = 0
        self.cooldown = 1
        self.callback = callback
        self.ignore_files = ignore_files

    def on_modified(self, event):
        if not event.src_path.endswith(".py"):
            return
        if event.src_path in self.ignore_files:
            return
        time = datetime.datetime.now().timestamp()
        if self.last_event + self.cooldown >= time:
            return
        self.last_event = time
        super().on_modified(event)
        print(event)
        self.callback(event.src_path)


class WindowRunner:
    def __init__(self):
        self._window: sg.Window = None
        self._theme = sg.CURRENT_LOOK_AND_FEEL
        self._latest_layout = None
        self.queue = Queue()

    @property
    def window(self):
        return self._window

    @window.setter
    def window(self, value):
        if self._window:
            self._window.close()
            self._window = None
        self._window = value

    @property
    def location(self):
        if self._window:
            return self._window.current_location(True)
        else:
            return None, None

    @property
    def size(self):
        if self._window:
            return self._window.size
        else:
            return None, None

    def make_layout(self, layout: Callable[[], list[list]]):
        return [
            [sg.Text("Theme: "),
             sg.DropDown(sg.theme_list(), key="theme", enable_events=True,
                         default_value=self._theme)],
            [sg.Frame("Preview", expand_x=True, expand_y=True,
                      layout=layout(), key="content")],
        ]

    def from_layout(self, layout: Callable[[], list[list]]):
        self.queue.put_nowait(layout)

    def _from_layout(self, layout: Callable[[], list[list]]):
        if self._theme:
            sg.theme(self._theme)
        self._latest_layout = layout
        self.window = sg.Window(
            "Python Simple Preview",
            self.make_layout(layout),
            keep_on_top=True,
            location=self.location,
            size=self.size,
            resizable=True,
            disable_minimize=True,
        )

    def step(self):
        if not self.queue.empty():
            self._from_layout(self.queue.get_nowait())
        if self._window:
            try:
                event, values = self._window.read(1)
                if event is None:
                    self._window = None
                elif event == "theme":
                    self._theme = values[event]
                    self._from_layout(self._latest_layout)
            except Exception as e:
                print(e)
        else:
            time.sleep(1)


def get_layout(path):
    spec = importlib.util.spec_from_file_location("lol", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.get_layout


def main():
    path = "."
    runner = WindowRunner()
    event_handler = ModifiedTracker(
        lambda x: runner.from_layout(get_layout(x)),
        [path for path in glob.glob(".\\*.py") if path != ".\\example.py"]
    )
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            runner.step()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
