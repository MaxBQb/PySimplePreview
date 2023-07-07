import logging

import PySimpleGUI as sg

from PySimplePreview.data.config_storage import ConfigStorage
from PySimplePreview.data.previews_storage import PreviewsStorage
from PySimplePreview.domain.model.preview import LAYOUT_PROVIDER, LAYOUT
from PySimplePreview.view.controller.base import BaseController
from PySimplePreview.view.layouts import get_preview_layout_frame, get_unpacked_layout, get_exception_layout


class ExternalPreviewWindowController(BaseController):
    def __init__(
        self,
        preview_key,
        config: ConfigStorage,
        previews: PreviewsStorage,
    ):
        super().__init__(config)
        self.__key = preview_key
        self._previews_storage = previews
        self._position_controller.other_key += "|" + preview_key
        self._window_provider = None

    @property
    def key(self):
        return self.__key

    def _get_layout(self):
        new_layout = self._previews.get(self.key)
        return new_layout.layout if new_layout else None

    @property
    def _previews(self):
        return self._previews_storage.previews

    def make_layout(self, layout: LAYOUT_PROVIDER):
        return [
            [get_preview_layout_frame(layout, self.key or "")],
        ]

    def _set_layout(self, layout: LAYOUT_PROVIDER):
        preview = self._previews.get(self.key)
        window: sg.Window | None = None
        self._position_controller.use_other = False
        if preview and preview.window:
            try:
                layout_instance = get_unpacked_layout(layout)
                self._position_controller.use_other = True
                self._window_provider = preview.window
                window = self.make_window(
                    layout_instance,
                    get_exception_layout
                )
            except Exception as e:
                self._position_controller.use_other = False
                self._window_provider = None
                logging.exception("Custom window creation failed. Fallback to default one.", exc_info=e)
        if not window:
            window = self.make_window(
                self.make_layout(layout),
                lambda e: self.make_layout(lambda: get_exception_layout(e))
            )
        super()._set_window(window)

    def _make_window(
        self,
        layout: LAYOUT,
        size: tuple[int, int] | tuple[None, None],
        location: tuple[int, int] | tuple[None, None],
    ) -> sg.Window:
        if self._window_provider:
            return self._window_provider(size, location, layout)

        return sg.Window(
            f"External Python Simple Preview for {self.key}",
            layout,
            keep_on_top=True,
            location=location,
            size=size,
            resizable=True,
            finalize=True,
            alpha_channel=0.0,
        )
