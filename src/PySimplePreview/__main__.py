from contextlib import suppress

from PySimplePreview.data.config_storage import ConfigStorage
from PySimplePreview.domain.interactor.files_observer import ProjectObserver
from PySimplePreview.domain.interactor.module_loader import ModuleLoader
from PySimplePreview.view.controllers import PreviewSettingsWindowController


def main():
    config_storage = ConfigStorage.get()
    runner = PreviewSettingsWindowController()
    module_loader = ModuleLoader.get()

    def on_modified(path: str):
        if config_storage.config.reload_all:
            project = config_storage.config.current_project
            if project:
                module_loader.reload_all(project)
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
