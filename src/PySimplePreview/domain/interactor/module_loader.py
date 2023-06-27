import glob
import importlib.util
import inspect
import os
import sys
from pathlib import Path

from PySimplePreview.data.config_storage import ConfigStorage
from PySimplePreview.data.previews_storage import PreviewsStorage
from PySimplePreview.domain.model.config import is_package_project, Config


class ModuleLoader:
    _instance = None

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._imported = dict()
        self._last_imported = None
        self._config_storage = ConfigStorage.get()
        self._previews = PreviewsStorage.get().previews
        self._config_storage.on_update(self._on_update)
        self._on_update(self._config_storage.config)

    def _on_update(self, config: Config):
        if config.current_project and self._last_imported != config.current_project:
            self.reload_all(Path(config.current_project))
            self._last_imported = config.current_project

    def load_any(self, path: str | Path):
        path = Path(path)
        if is_package_project(path) or path.is_dir():
            root_path = str(path.parent)
            for module in glob.iglob(root_path + "\\**\\*.py", recursive=True):
                self.load_module(module)
        else:
            self.load_module(path)

    def unload_all(self):
        for path in list(self._imported):
            self.unload_module(path)

    def reload_all(self, path):
        if self._config_storage.config.reload_all and self._last_imported:
            self.hard_reload()
        self.unload_all()
        self.load_any(path)

    def load_module(self, path: str | Path):
        path = Path(path)
        is_package = path.is_dir() or is_package_project(path)
        if is_package_project(path):
            path = path.parent
        name = path.stem if is_package else inspect.getmodulename(str(path))
        module_path = path.joinpath('__init__.py') if is_package else path
        spec = importlib.util.spec_from_file_location(
            name, module_path,
            submodule_search_locations=[os.path.dirname(path)]
        )
        if path in self._imported:
            self.unload_module(path)
        print("Load", f"'{name}'", "package" if is_package else "module")
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        self._imported[module_path] = spec.name
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            print("Error on import", f"'{name}'", "package" if is_package else "module")
            print(e)
            self.unload_module(path)

    def unload_module(self, path: Path):
        self._previews.remove_module(path)
        if path in self._imported:
            name = self._imported[path]
            del sys.modules[name]
            del self._imported[path]
            is_package = path.is_dir() or is_package_project(path)
            print("Package" if is_package else "Module", f"'{name}' unloaded")

    def hard_reload(self):
        python = sys.executable
        os.execl(python, python, "\"{}\"".format(sys.argv[0]))
        exit()
