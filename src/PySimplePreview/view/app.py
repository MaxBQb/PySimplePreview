from contextlib import suppress

import punq

from PySimplePreview.data.config_storage import ConfigStorage
from PySimplePreview.domain.interactor.abc.files_observer import ProjectObserver
from PySimplePreview.domain.interactor.abc.module_loader import ModuleLoader
from PySimplePreview.view.controller.preview_settings import PreviewSettingsWindowController


class Application:
    current: 'Application' = None

    def __init__(
        self,
        config_storage: ConfigStorage,
        runner: PreviewSettingsWindowController,
        module_loader: ModuleLoader,
        project_observer: ProjectObserver,
        container: punq.Container,
    ):
        self._config_storage = config_storage
        self._runner = runner
        self._module_loader = module_loader
        self._project_observer = project_observer
        self.__class__.current = self
        self.container = container

    def run(self):
        with self._project_observer.track():
            with suppress(KeyboardInterrupt):
                print("Press Ctrl + C to exit")
                self._module_loader.setup()
                self._runner.refresh_layout()
                while True:
                    self._runner.step()
