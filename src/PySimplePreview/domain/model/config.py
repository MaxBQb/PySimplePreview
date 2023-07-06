import glob
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

from PySimplePreview.domain.model.log_config import LogConfig
from PySimplePreview.domain.model.position import Position


@dataclass
class Config:
    last_preview_key: str = None
    last_preview_group_key: str = None
    current_project: Path = None
    projects: tuple[Path, ...] = tuple()
    reload_all: bool = False
    remember_positions: bool = True
    integrated_preview: bool = True
    theme: str = None
    logging: LogConfig = field(default_factory=LogConfig)
    positions: Dict[str, Position] = field(default_factory=dict)

    def __post_init__(self):
        self.projects = tuple(
            project for project in self.projects if is_valid_project(project)
        )
        if self.current_project:
            if not is_valid_project(self.current_project) or self.current_project not in self.projects:
                self.current_project = None

    def add_project(self, path: Path):
        new_project = path.absolute()
        for project in self.projects:
            if project.samefile(new_project):
                self.current_project = project
                return
        self.projects += (new_project,)
        self.current_project = new_project


def is_valid_project(path: Path):
    return path.exists() and (
        path.is_file() and path.suffix == ".py" or
        path.is_dir() and next(glob.iglob(str(path.joinpath("*.py"))), False)
    )


def get_package_root(path: Path):
    if path.is_file():
        path = path.parent
    init = path.joinpath('__init__.py')
    if init.exists():
        return init
    if next(glob.iglob(str(path.joinpath("*.py"))), False):
        return path
    return None


def is_package_project(path: Path):
    return path.name == '__init__.py' or \
        path.is_dir() and next(glob.iglob(str(path.joinpath("*.py"))), False)
