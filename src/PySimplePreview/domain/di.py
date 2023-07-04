import punq

from PySimplePreview.domain.interactor.abc.files_observer import ProjectObserver
from PySimplePreview.domain.interactor.abc.module_loader import ModuleLoader
from PySimplePreview.domain.interactor.files_observer import ProjectObserverImpl
from PySimplePreview.domain.interactor.module_loader import ModuleLoaderImpl
from PySimplePreview.domain.interactor.previews_manager import PreviewsManager


def register_domain(container: punq.Container):
    container.register(ModuleLoader, ModuleLoaderImpl, scope=punq.Scope.singleton)
    container.register(PreviewsManager, scope=punq.Scope.singleton)
    container.register(ProjectObserver, ProjectObserverImpl, scope=punq.Scope.singleton)
