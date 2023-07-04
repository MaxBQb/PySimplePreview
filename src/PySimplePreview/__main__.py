import punq

from PySimplePreview import di
from PySimplePreview.view.app import Application


def main():
    container = punq.Container()
    di.configure_di(container)
    app: Application = container.resolve(Application)
    app.run()


if __name__ == '__main__':
    main()
