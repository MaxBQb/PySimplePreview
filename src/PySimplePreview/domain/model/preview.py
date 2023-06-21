import time
import typing
from dataclasses import dataclass, field
from pathlib import Path


LayoutProvider: typing.TypeAlias = typing.Callable[[], list[list]]


@dataclass
class Preview:
    path: Path
    layout: LayoutProvider
    creation_time: int = field(default_factory=lambda: int(time.time()))
