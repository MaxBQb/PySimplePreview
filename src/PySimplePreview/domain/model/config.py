from dataclasses import dataclass


@dataclass
class Config:
    last_preview_key: str = None
    theme: str = None
    size: tuple[int, int] = None, None
    location: tuple[int, int] = None, None
