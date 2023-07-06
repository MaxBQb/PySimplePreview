import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path


@dataclass
class LogConfig:
    class LoggingLevel(Enum):
        DEBUG = logging.DEBUG
        INFO = logging.INFO
        WARNING = logging.WARNING
        ERROR = logging.ERROR
        FATAL = logging.FATAL

    class LoggingDestination(Enum):
        CONSOLE = auto()
        FILE = auto()
        NOWHERE = auto()

    show_settings: bool = False
    level: LoggingLevel = LoggingLevel.INFO
    write_to: LoggingDestination = LoggingDestination.CONSOLE
    file_path: Path = field(default_factory=lambda: Path("./logs/latest.log"))

    def __post_init__(self):
        if self.write_to == self.LoggingDestination.FILE \
                and not self.file_path:
            self.write_to = self.LoggingDestination.CONSOLE
