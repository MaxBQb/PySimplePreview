import traceback

import PySimpleGUI as sg

from PySimplePreview.domain.interactor.previews_manager import PreviewsManager
from PySimplePreview.domain.model.preview import LayoutProvider
from PySimplePreview.view.models import ConfigViewDTO, ListItem


def get_settings_layout(config: ConfigViewDTO, previews: tuple[ListItem, ...]):
    return [
        [sg.Text("Theme:"),
         sg.DropDown(sg.theme_list(), key="theme", enable_events=True,
                     default_value=config.theme)],
        [sg.Text("Project:"),
         sg.DropDown(
             config.projects, key="project", enable_events=True,
             default_value=config.current_project),
         sg.Button("New", key="new_project"),
         ],
        [sg.Text("Preview:"),
         sg.DropDown(previews, key="preview", enable_events=True,
                     default_value=config.preview_key or (previews[0] if previews else "")),
         sg.Text("From: "+("Whole package" if config.is_package else "Only selected module"),
                 visible=config.is_package is not None)],
    ]


def get_preview_layout_frame(content: LayoutProvider, name=""):
    try:
        name = f"[{PreviewsManager.key_of(name)}]" if name else ""
        layout = content() or get_nocontent_layout()
    except Exception as e:
        message = str(e) + "\n".join(traceback.format_tb(e.__traceback__))
        layout = [
            [sg.Text("Error:")],
            [sg.Multiline(
                default_text=message,
                disabled=True, font=('Consolas', 10),
                expand_y=True, expand_x=True,
                pad=(6, 6),
            )]
        ]
    return sg.Frame("Preview" + f' for {name}' if name else '', expand_x=True, expand_y=True, layout=layout)


def get_nocontent_layout():
    return [[sg.Text("No content found")]]
