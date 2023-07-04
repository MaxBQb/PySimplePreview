import punq

from PySimplePreview.view.controller.external_preview import ExternalPreviewWindowController
from PySimplePreview.view.controller.external_preview_factory import ExternalPreviewWindowControllerFactory
from PySimplePreview.view.controller.preview_settings import PreviewSettingsWindowController
from PySimplePreview.view.controller.system_args_handler import SystemArgsHandler


def register_view(container: punq.Container):
    container.register(PreviewSettingsWindowController, scope=punq.Scope.singleton)
    container.register(ExternalPreviewWindowController)
    container.register(ExternalPreviewWindowControllerFactory, scope=punq.Scope.singleton)
    container.register(SystemArgsHandler)
