import typing
from dataclasses import dataclass


@dataclass
class Position:
    size: tuple[int, int] = None
    location: tuple[int, int] = None


class PositionWithFallback:
    def __init__(
        self,
        source: typing.Callable[[str], Position],
        update_source: typing.Callable[[str, Position], None],
        core_key: str,
        other_key: str,
        use_other: bool = False,
    ):
        self.source = source
        self.update_source = update_source
        self.core_key = core_key
        self.other_key = other_key
        self.use_other = use_other

    @property
    def position(self):
        core_pos = self.source(self.core_key) or Position()
        if not self.use_other:
            return core_pos
        other_pos = self.source(self.other_key) or Position()
        return Position(other_pos.size, other_pos.location or core_pos.location)

    @position.setter
    def position(self, value: Position):
        if not self.use_other:
            self.update_source(self.core_key, value)
            return
        core_pos = self.source(self.core_key) or value
        new_other_pos = Position(value.size)
        new_core_pos = Position(core_pos.size, value.location)
        if value.location == core_pos.location:
            self.update_source(self.other_key, new_other_pos)
        self.update_source(self.core_key, new_core_pos)
