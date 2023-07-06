from enum import Enum, auto


class SettingsEvents(Enum):
    THEME = auto()
    GROUP = auto()
    PROJECT = auto()
    RELOAD_ALL = auto()
    REMEMBER_POSITIONS = auto()
    INTEGRATED_PREVIEW = auto()
    NEW_PROJECT = auto()
    PREVIEW = auto()
    TOGGLE_LOG = auto()
    LOGGING_LEVEL = auto()
    LOGGING_DESTINATION = auto()
    LOG_FILE_PATH = auto()
    LOG = auto()
