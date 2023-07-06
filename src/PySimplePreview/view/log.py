import logging

from PySimplePreview.data.config_storage import ConfigStorage


class LoggingConfigurator:
    def __init__(self, config_storage: ConfigStorage):
        self._config_storage = config_storage
        self._config_storage.on_update += lambda _: self.setup()

    def setup(self):
        logging.basicConfig(
            format="[%(asctime)s][%(levelname)s] %(message)s",
            datefmt='%d.%m.%Y %H:%M:%S',
            level=logging.INFO,
        )
