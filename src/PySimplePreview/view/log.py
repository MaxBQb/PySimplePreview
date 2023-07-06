import io
import logging
import sys
import typing
from pathlib import Path

from PySimplePreview.data.config_storage import ConfigStorage
from PySimplePreview.domain.model.event import InvokableEvent
from PySimplePreview.domain.model.log_config import LogConfig


class _InfoOrLesser(logging.Filter):
    def filter(self, record):
        return record.levelno <= logging.INFO


class ObservableStream(io.StringIO):
    def __init__(self):
        super().__init__()
        self._on_write = InvokableEvent[typing.Callable[[str], None]]()
        self.on_write = self._on_write.base

    def write(self, __s: str) -> int:
        result = super().write(__s)
        self._on_write.invoke(__s)
        return result


class _Steams:
    def __init__(self):
        self._observable_stream = ObservableStream()
        self._stream = logging.StreamHandler(self._observable_stream)
        self._stream.setLevel(logging.NOTSET)
        self._stream.setFormatter(logging.Formatter(
            "[%(asctime)s][%(levelname)s] %(message)s",
            datefmt="%H:%M:%S"
        ))

        self._console_stream = logging.StreamHandler(sys.stdout)
        self._console_stream.setLevel(logging.NOTSET)
        self._console_stream.addFilter(_InfoOrLesser())

        self._console_err_stream = logging.StreamHandler(sys.stderr)
        self._console_err_stream.setLevel(logging.WARNING)
        self._file = None
        self._file_name = None

    def _close_file(self):
        if self._file:
            self._file.close()
            self._file = None
            self._file_name = None

    @property
    def independent(self):
        return self._observable_stream

    @property
    def console(self):
        self._close_file()
        return self._stream, self._console_stream, self._console_err_stream

    @property
    def nowhere(self):
        self._close_file()
        return (self._stream,)

    def file(self, path: Path):
        if not self._file_name or not path.samefile(self._file_name):
            self._close_file()
            self._file_name = path
            if not path.exists() or not path.is_file():
                path.parent.mkdir(exist_ok=True)
                path.open("a").close()
            self._file = logging.FileHandler(path, encoding="utf-8")
        return self._stream, self._file


class LoggingConfigurator:
    def __init__(self, config_storage: ConfigStorage):
        self._config_storage = config_storage
        self._streams = _Steams()
        self._config_storage.on_update += lambda _: self.setup()
        self.on_write = self._streams.independent.on_write

    @property
    def current_log(self):
        return self._streams.independent.getvalue()

    def setup(self):
        config = self._config_storage.config.logging
        handlers = tuple()
        if config.write_to == LogConfig.LoggingDestination.CONSOLE:
            handlers = self._streams.console
        elif config.write_to == LogConfig.LoggingDestination.NOWHERE:
            handlers = self._streams.nowhere
        elif config.write_to == LogConfig.LoggingDestination.FILE:
            handlers = self._streams.file(config.file_path)

        logging.basicConfig(
            format="[%(asctime)s][%(levelname)s] %(message)s",
            datefmt='%d.%m.%Y %H:%M:%S',
            level=config.level.value,
            handlers=handlers,
            force=True,
        )
