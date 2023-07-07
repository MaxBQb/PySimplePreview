import logging
from contextlib import suppress

import punq

from PySimplePreview.data import config_storage
from PySimplePreview.data.config_storage import ConfigStorage
from PySimplePreview.domain.interactor.abc.files_observer import ProjectObserver
from PySimplePreview.domain.interactor.abc.module_loader import ModuleLoader
from PySimplePreview.view.controller.preview_settings import PreviewSettingsWindowController
from PySimplePreview.view.controller.system_args_handler import SystemArgsHandler
from PySimplePreview.view.log import LoggingConfigurator


class Application:
    current: 'Application' = None

    def __init__(
        self,
        config_storage: ConfigStorage,
        runner: PreviewSettingsWindowController,
        module_loader: ModuleLoader,
        project_observer: ProjectObserver,
        ars_handler: SystemArgsHandler,
        logger_configurator: LoggingConfigurator,
        container: punq.Container,
    ):
        self._config_storage = config_storage
        self._runner = runner
        self._ars_handler = ars_handler
        self._module_loader = module_loader
        self._project_observer = project_observer
        self._logger_configurator = logger_configurator
        self.__class__.current = self
        self.container = container

    def run(self):
        self._ars_handler.run()
        self._logger_configurator.setup()
        with self._project_observer.track():
            with suppress(KeyboardInterrupt):
                print("PySimplePreview started!")
                print("Press Ctrl + C to exit")
                self._module_loader.setup()
                self._runner.refresh_layout()
                while True:
                    self._project_observer.dispatch_events()
                    self._runner.step()
