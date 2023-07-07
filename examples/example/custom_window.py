import PySimpleGUI as sg

from condition_import import preview, method_preview, params


def get_preview_window(
    size: tuple[int, int] | tuple[None, None],
    location: tuple[int, int] | tuple[None, None],
    layout: list[list]
):
    return sg.Window(
        f"Custom window title",
        layout=layout,
        location=location,
        size=size,
        resizable=True,
        alpha_channel=0.0,
        keep_on_top=True,
        disable_minimize=True,
        disable_close=True,
    )


class ExampleClass:
    def __init__(self, name: str = "from no param class"):
        self.name = name

    @method_preview(window_provider=get_preview_window)
    def get_layout(self):
        return [
            [sg.Text(f"Hello, {self.name}")],
            [sg.Text("H1") for _ in range(6)],
        ]

    @method_preview(window_provider=get_preview_window)
    @property
    def layout(self):
        return [
            [sg.Text(f"Hello, property {self.name}")],
            [sg.Text("H1") for _ in range(6)],
        ]

    @staticmethod
    @preview(call_params=params("from static"), window_provider=get_preview_window)
    def static_layout(name):
        return [
            [sg.Text(f"Hello, {name}")],
            [sg.Text("H1") for _ in range(6)],
        ]


@preview(window_provider=get_preview_window)
def get_layout(name="world!!"):
    return [
        [sg.Text(f"Hello, {name}")],
        [sg.Text("H1", font=("Tahoma", 8)) for _ in range(6)],
    ]
