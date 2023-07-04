import traceback

import PySimpleGUI as sg

from PySimplePreview.domain.interactor.previews_manager import PreviewsManager
from PySimplePreview.domain.model.preview import LAYOUT_PROVIDER
from PySimplePreview.view.contracts import SettingsEvents
from PySimplePreview.view.models import ConfigViewDTO, ListItem


def get_settings_layout(
        config: ConfigViewDTO,
        previews: tuple[ListItem, ...],
        groups: tuple[str, ...],
):
    return [
        [sg.Text("Theme:"),
         sg.DropDown(sg.theme_list(), key=SettingsEvents.THEME, enable_events=True,
                     default_value=config.theme),
         sg.Checkbox("Reload all", config.reload_all, key=SettingsEvents.RELOAD_ALL,
                     tooltip="On any change whole program will be reloaded (not recommended)"
                             "\nUse this only if your layout depends on other module that is"
                             "\nchanged at preview time",
                     visible=config.is_package, enable_events=True),
         sg.Button(
             "Internal preview" if config.integrated_preview else "External preview",
             key=SettingsEvents.INTEGRATED_PREVIEW,
             disabled=config.integrated_preview_disabled,
             tooltip="Show preview below (Internal) or in separate window (External)",
         )],
        [sg.Text("Project:"),
         sg.DropDown(
             config.projects, key=SettingsEvents.PROJECT, enable_events=True,
             default_value=config.current_project),
         sg.Button("New", key=SettingsEvents.NEW_PROJECT),],
        [sg.Text("Group:"),
         sg.DropDown(groups, key=SettingsEvents.GROUP, enable_events=True,
                     disabled=len(groups) <= 1,
                     default_value=config.last_preview_group_key),
         sg.Checkbox("Remember size and pos", config.remember_positions, key=SettingsEvents.REMEMBER_POSITIONS,
                     tooltip="On any move or resize of an app's window, it's position and size "
                             "\nwill be persisted in config. Already stored values will be used "
                             "\nas default one, even with this setting turned off!",
                     enable_events=True)],
        [sg.Text("Preview:"),
         sg.DropDown(previews, key=SettingsEvents.PREVIEW, enable_events=True,
                     default_value=config.preview_key or (previews[0] if previews else "")),
         sg.Text("From: " + ("Whole package" if config.is_package else "Only selected module"),
                 visible=config.is_package is not None)],
    ]


def get_preview_layout_frame(content: LAYOUT_PROVIDER, name=""):
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
