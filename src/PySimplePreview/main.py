import glob
import importlib.util
import inspect
from contextlib import suppress

from src.PySimplePreview.domain.interactor.files_observer import FilesObserver
from src.PySimplePreview.view.controllers import PreviewWindowController


def load_module(path):
    spec = importlib.util.spec_from_file_location(inspect.getmodulename(path), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def main():
    root_path = "..\\..\\examples"
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
