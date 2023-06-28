from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

from PySimplePreview.domain.model.position import Position


@dataclass
class Config:
    last_preview_key: str = None
    last_preview_group_key: str = None
    current_project: Path = None
    projects: tuple[Path, ...] = tuple()
    reload_all: bool = False
    integrated_preview: bool = True
    theme: str = None
    positions: Dict[str, Position] = field(default_factory=dict)

    def __post_init__(self):
        self.projects = tuple(
            project for project in self.projects if is_valid_project(project)
        )
        if self.current_project:
            if not is_valid_project(self.current_project) or self.current_project not in self.projects:
                self.current_project = None


def is_valid_project(path: Path):
    return path.exists() and path.is_file() and path.suffix == ".py"


def is_package_project(path: Path):
    return path.name == '__init__.py'
