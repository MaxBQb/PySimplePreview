import time
import typing
from dataclasses import dataclass, field
from pathlib import Path

import PySimpleGUI as sg

LAYOUT_PROVIDER: typing.TypeAlias = typing.Callable[[], list[list]]
WINDOW_PROVIDER: typing.TypeAlias = typing.Callable[[
    tuple[int, int] | tuple[None, None],
    tuple[int, int] | tuple[None, None],
    list[list]
], sg.Window]


@dataclass
class Preview:
    path: Path
    layout: LAYOUT_PROVIDER
    creation_time: int = field(default_factory=lambda: int(time.time()))
    window: WINDOW_PROVIDER = None

    @property
    def internal(self):
        return self.window is None
