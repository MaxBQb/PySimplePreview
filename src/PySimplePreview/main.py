import glob
import importlib.util
import inspect
import os.path
import sys
from contextlib import suppress

from src.PySimplePreview.domain.interactor.files_observer import FilesObserver
from src.PySimplePreview.view.controllers import PreviewWindowController


def load_module(path):
    is_package = os.path.isdir(path) or path.endswith("__init__.py")
    if path.endswith("__init__.py"):
        path = os.path.dirname(path)
    name = os.path.basename(path) if is_package else inspect.getmodulename(path)
    module_path = os.path.join(path, '__init__.py') if is_package else path
    print("Load", f"'{name}'", "package" if is_package else "module")
    spec = importlib.util.spec_from_file_location(
        name, module_path,
        submodule_search_locations=[os.path.dirname(path)]
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)


def main():
    root_path = "..\\..\\examples\\example"
    runner = PreviewWindowController()

    def on_modified(path: str):
        load_module(path)
        runner.refresh_layout()

    for module in glob.iglob(root_path + "\\**\\*.py", recursive=True):
        load_module(module)

    with FilesObserver.track(on_modified, root_path):
        print("Start watching..")
        with suppress(KeyboardInterrupt):
            print("Press Ctrl + C to exit")
            runner.refresh_layout()
            while True:
                runner.step()


if __name__ == '__main__':
    main()
