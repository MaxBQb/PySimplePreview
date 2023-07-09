import PySimpleGUI as sg

from condition_import import preview, params


@preview(call_params=params(name="from preview defaults!!"))
def get_layout(name="world!!"):
    return [
        [sg.Text(f"Hello, {name}")],
        [sg.Text("H1") for _ in range(6)],
    ]


@preview
def preview3():
    return get_layout("human")
