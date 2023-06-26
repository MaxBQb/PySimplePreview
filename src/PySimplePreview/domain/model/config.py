from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    last_preview_key: str = None
    current_project: Path = None
    projects: tuple[Path, ...] = tuple()
    theme: str = None
    size: tuple[int, int] = None, None
    location: tuple[int, int] = None, None

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
