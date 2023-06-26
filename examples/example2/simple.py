import time

import PySimpleGUI as sg

from src.PySimplePreview import preview


@preview(name="from preview defaults!!")
def get_layout(name="world!!"):
    return [
        [sg.Text(f"Hello, {name}")],
        [sg.Text("H1") for _ in range(6)],
    ]


@preview
def preview3():
    return get_layout("human")
