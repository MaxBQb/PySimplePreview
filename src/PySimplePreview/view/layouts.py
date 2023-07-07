import logging
import traceback
import typing

import PySimpleGUI as sg

from PySimplePreview.domain.interactor.previews_manager import PreviewsManager
from PySimplePreview.domain.model.log_config import LogConfig
from PySimplePreview.domain.model.preview import LAYOUT_PROVIDER
from PySimplePreview.view.contracts import SettingsEvents
from PySimplePreview.view.models import ConfigViewDTO, ListItem, LogConfigViewDTO


def get_settings_layout(
        config: ConfigViewDTO,
        previews: tuple[ListItem, ...],
        groups: tuple[str, ...],
):
    return [[sg.Column(justification='center', p=(8, 2), s=(445, 116), layout=[[
        sg.Text("Theme:", s=6, p=0),
        sg.DropDown(
            sg.theme_list(),
            key=SettingsEvents.THEME,
            enable_events=True,
            default_value=config.theme,
        ),
        sg.Checkbox(
            "Reload all",
            config.reload_all,
            key=SettingsEvents.RELOAD_ALL,
            tooltip="On any change whole program will be reloaded (not recommended)"
                    "\nUse this only if your layout depends on other module that is"
                    "\nchanged at preview time",
            disabled=not config.is_package,
            enable_events=True,
        ),
        sg.Button(
            "Internal preview" if config.integrated_preview else "External preview",
            key=SettingsEvents.INTEGRATED_PREVIEW,
            disabled=config.integrated_preview_disabled,
            tooltip="Show preview below (Internal) or in separate window (External)",
            s=12,
        ),
    ], [
        sg.Text("Project:", s=6, p=0),
        sg.DropDown(
            config.projects,
            size=43,
            key=SettingsEvents.PROJECT, enable_events=True,
            default_value=config.current_project,
        ),
        sg.Button("New", key=SettingsEvents.NEW_PROJECT, s=4, p=((11, 0), 0)),
    ], [
        sg.Text("Group:", s=6, p=(0, 6)),
        sg.DropDown(
            groups,
            size=25,
            key=SettingsEvents.GROUP, enable_events=True,
            disabled=len(groups) <= 1,
            default_value=config.last_preview_group_key,
        ),
        sg.Checkbox(
            "Remember size and pos", config.remember_positions, key=SettingsEvents.REMEMBER_POSITIONS,
            tooltip="On any move or resize of an app's window, it's position and size "
                    "\nwill be persisted in config. Already stored values will be used "
                    "\nas default one, even with this setting turned off!",
            enable_events=True,
            p=((10, 0), 0),
        ),
    ], [
        sg.Text("Preview:", s=6, p=0),
        sg.DropDown(
            previews,
            size=25,
            key=SettingsEvents.PREVIEW,
            enable_events=True,
            default_value=config.preview_key or (previews[0] if previews else ""),
        ),
        sg.Button("Log", font=("Consolas", 8), p=(3, 3), key=SettingsEvents.TOGGLE_LOG),
        sg.Text(
            "From: " + ("Package" if config.is_package else "Single module"),
            visible=config.is_package is not None,
            justification='right',
            s=15, p=((21, 0), 0),
        ),
    ],
    ])]]


def get_preview_layout_frame(content: LAYOUT_PROVIDER, name=""):
    name = f"[{PreviewsManager.key_of(name)}]" if name else ""
    layout = get_unpacked_layout(content)
    return sg.Frame("Preview" + f' for {name}' if name else '', expand_x=True, expand_y=True, layout=layout)


def get_exception_layout(e: Exception):
    message = str(e) + "\n".join(traceback.format_tb(e.__traceback__))
    return [
        [sg.Text("Error:")],
        [sg.Multiline(
            default_text=message,
            disabled=True, font=('Consolas', 10),
            expand_y=True, expand_x=True,
            pad=(6, 6),
        )]
    ]


def get_nocontent_layout():
    return [[sg.Text("No content found")]]


def get_unpacked_layout(
    content: LAYOUT_PROVIDER,
    no_content: LAYOUT_PROVIDER = get_nocontent_layout,
    error_content: typing.Callable[[Exception], list[list]] = get_exception_layout,
):
    try:
        result = content()
        if not result:
            logging.warning("User defined layout have no content")
            return no_content()
        return result
    except Exception as e:
        logging.error(f"User defined layout can't be built: {e}")
        return error_content(e)


def get_log_layout(config: LogConfigViewDTO, log: str):
    show_file_selection = config.write_to == LogConfig.LoggingDestination.FILE.name
    return [[
        sg.Column(justification='center', p=(8, 0), s=(445, (55 if show_file_selection else 28)), layout=[[
            sg.Text("Level:", s=6, p=((0, 5), 4)),
            sg.DropDown(
                config.levels, config.level,
                enable_events=True, s=9, p=0,
                key=SettingsEvents.LOGGING_LEVEL,
            ),
            sg.Text(s=18, p=0),
            sg.Text("Write to:", p=((0, 2), 0)),
            sg.DropDown(
                config.write_to_options, config.write_to,
                enable_events=True, s=10, p=0,
                key=SettingsEvents.LOGGING_DESTINATION,
            ),
        ], [
            sg.Text(
                "Path:",
                tooltip="Path where log file should be saved",
                p=((0, 5), 4),
                s=6, visible=show_file_selection,
            ),
            sg.Input(
                config.file_path or "Not set",
                readonly=True, s=48, p=0,
                visible=show_file_selection,
                disabled_readonly_background_color=sg.theme_input_background_color(),
            ),
            sg.Button(
                "...", initial_folder="./logs",
                file_types=(("Log files", "*.log"),),
                font=("Tahoma", 8), p=((6, 0), 4), s=3,
                visible=show_file_selection,
                button_type=sg.BUTTON_TYPE_SAVEAS_FILE,
                key=SettingsEvents.LOG_FILE_PATH,
            ),
        ]]), ],
        [sg.Multiline(
            default_text=log, autoscroll=True,
            disabled=True, font=('Consolas', 8),
            expand_x=True, key=SettingsEvents.LOG,
            pad=(6, 6), s=(0, 10)
        )]
    ]
