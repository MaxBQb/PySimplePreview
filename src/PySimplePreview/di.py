import punq

from PySimplePreview.data.di import register_data
from PySimplePreview.domain.di import register_domain
from PySimplePreview.view.app import Application
from PySimplePreview.view.di import register_view


def configure_di(container: punq.Container):
    container.register(Application, scope=punq.Scope.singleton)
    register_domain(container)
    register_data(container)
    register_view(container)
