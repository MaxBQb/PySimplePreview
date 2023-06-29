from typing import Callable

import PySimpleGUI as sg

from PySimplePreview.data.previews_storage import PreviewsStorage
from PySimplePreview.domain.model.preview import LayoutProvider
from PySimplePreview.view.controller.base import BaseController
from PySimplePreview.view.layouts import get_preview_layout_frame


class ExternalPreviewWindowController(BaseController):
    def __init__(self, preview_key):
        super().__init__()
        self.__key = preview_key
        self._previews_storage = PreviewsStorage.get()

    @property
    def key(self):
        return self.__key

    def _get_layout(self):
        new_layout = self._previews.get(self.key)
        return new_layout.layout if new_layout else None

    @property
    def _previews(self):
        return self._previews_storage.previews

    def make_layout(self, layout: Callable[[], list[list]]):
        return [
            [get_preview_layout_frame(layout, self.key or "")],
        ]

    def _set_layout(self, layout: LayoutProvider):
        window = sg.Window(
            f"External Python Simple Preview for {self.key}",
            self.make_layout(layout),
            keep_on_top=True,
            location=self._position.location,
            size=self._position.size,
            resizable=True,
            finalize=True,
            alpha_channel=0.0,
        )
        super()._set_window(window)
