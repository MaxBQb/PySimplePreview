import glob
import importlib.util
import inspect
import logging
import os
import sys
from pathlib import Path

from PySimplePreview.data.config_storage import ConfigStorage
from PySimplePreview.domain.interactor.abc.files_observer import ProjectObserver
from PySimplePreview.domain.interactor.abc.module_loader import ModuleLoader
from PySimplePreview.domain.interactor.previews_manager import get_longest_module_name
from PySimplePreview.domain.model.config import is_package_project, Config, get_package_root
from PySimplePreview.domain.model.event import InvokableEvent


class ModuleLoaderImpl(ModuleLoader):
    def __init__(self, config: ConfigStorage, project_observer: ProjectObserver):
        super().__init__()
        self.on_event = InvokableEvent.from_base(self.on_event)
        self._imported = dict()
        self._extra_imported = set()
        self._last_imported = None
        self._config_storage = config
        self._config_storage.on_update += self._on_update
        project_observer.on_project_update += self._on_module_update

    def setup(self):
        self._on_update(self._config_storage.config)

    def _on_update(self, config: Config):
        if config.current_project and self._last_imported != config.current_project:
            self.reload_all(Path(config.current_project))
            self._last_imported = config.current_project

    def _on_module_update(self, path: Path, is_project: bool):
        if is_project and path and self._last_imported != path:
            self.reload_all(path)
            self._last_imported = path
            return
        if self._config_storage.config.reload_all:
            project = self._config_storage.config.current_project
            if project:
                self.reload_all(project)
        else:
            self.load_module(path, True)

    def load_any(self, path: str | Path):
        path = Path(path)
        if is_package_project(path):
            root = get_package_root(path)
            if not root:
                raise ValueError("No python package root found, can't import anything")
            self.load_module(root)
            root_dir = root if root.is_dir() else root.parent
            mask = str(root_dir.joinpath("**", "*.py"))
            for module in glob.iglob(mask, recursive=True):
                if not root.samefile(module):
                    self.load_module(module)
        else:
            self.load_module(path)

    def unload_all(self):
        for path in list(self._imported):
            self.unload_module(path)
        for module in self._extra_imported:
            if module in sys.modules:
                del sys.modules[module]
        self._extra_imported.clear()
        importlib.invalidate_caches()

    def reload_all(self, path):
        self.on_event.invoke(ModuleLoader.EventType.PackageReloadStarted, path)
        if self._config_storage.config.reload_all and self._last_imported:
            self._hard_reload()
            return
        self.unload_all()
        self.load_any(path)
        self.on_event.invoke(ModuleLoader.EventType.PackageReloadEnded, path)

    def load_module(self, path: str | Path, reload=False):
        path = Path(path)
        is_package = path.is_dir() or is_package_project(path)
        if is_package_project(path):
            path = path.parent
        name = path.stem if is_package else inspect.getmodulename(str(path))
        module_path = path.joinpath('__init__.py') if is_package else path
        if not module_path.exists():
            logging.info(f"Package '{name}' resolved as flat (no __init__ found)")
            return
        old_modules = set(sys.modules.keys())
        root_path = str(path if path.is_dir() else path.parent)
        if root_path not in sys.path:
            sys.path.append(root_path)
        spec = importlib.util.spec_from_file_location(
            name, module_path,
            submodule_search_locations=[root_path]
        )
        if path in self._imported:
            self._imported[module_path] = name
            if reload:
                self.unload_module(module_path)
            else:
                return
        module_naming = "package" if is_package else "module"
        logging.info(f"Loading {module_naming} '{name}'")
        module = importlib.util.module_from_spec(spec)
        if '.'.join(get_longest_module_name(module_path)) in self._extra_imported and not reload:
            logging.info(f"{module_naming.title()} '{name}' is already loaded, skipping...")
            self._imported[module_path] = spec.name
            return
        sys.modules[spec.name] = module
        self._imported[module_path] = spec.name
        try:
            spec.loader.exec_module(module)
            new_modules = set(sys.modules.keys())
            diff_modules = new_modules.difference(old_modules)
            self._extra_imported |= diff_modules
            self.on_event.invoke(ModuleLoader.EventType.ModuleLoaded, module_path)
        except Exception as e:
            logging.exception(
                f"Can't import '{name}' {module_naming}",
                exc_info=e
            )
            self.unload_module(module_path)

    def unload_module(self, path: Path):
        if path in self._imported:
            name = self._imported[path]
            if name in sys.modules:
                del sys.modules[name]
            del self._imported[path]
            is_package = path.is_dir() or is_package_project(path)
            logging.info(("Package" if is_package else "Module") + f" '{name}' unloaded")
        self.on_event.invoke(ModuleLoader.EventType.ModuleUnloaded, path)

    def _hard_reload(self):
        python = sys.executable
        os.execl(python, python, "\"{}\"".format(sys.argv[0]))
        exit()
