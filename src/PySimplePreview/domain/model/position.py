from dataclasses import dataclass


@dataclass
class Position:
    size: tuple[int, int] = None
    location: tuple[int, int] = None
