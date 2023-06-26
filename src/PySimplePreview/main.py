from contextlib import suppress

from src.PySimplePreview.domain.interactor.files_observer import ProjectObserver
from src.PySimplePreview.domain.interactor.module_loader import ModuleLoader
from src.PySimplePreview.view.controllers import PreviewWindowController


def main():
    runner = PreviewWindowController()
    module_loader = ModuleLoader.get()

    def on_modified(path: str):
        module_loader.load_module(path)
        runner.refresh_layout()

    with ProjectObserver.get().track(on_modified):
        with suppress(KeyboardInterrupt):
            print("Press Ctrl + C to exit")
            runner.refresh_layout()
            while True:
                runner.step()


if __name__ == '__main__':
    main()
