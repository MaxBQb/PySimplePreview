import sys
import time

import PySimpleGUI as sg

from .condition_import import preview


def preview2():
    sg.Window(
        "Example",
        get_layout(),
        size=(280, 280),
        keep_on_top=True,
        finalize=True).read()


class ExampleClass:
    def __init__(self, name: str = "from no param class"):
        self.name = name

    @preview
    @preview("default for class2", class_params=preview.class_params(name="from class 2"))
    @preview("default for class", class_params=preview.class_params(name="from class"))
    def get_layout(self):
        return [
            [sg.Text(f"Hello, {self.name}")],
            [sg.Text("H1") for _ in range(6)],
        ]

    @preview(class_params=preview.class_params("from property"))
    @property
    def layout(self):
        return [
            [sg.Text(f"Hello, {self.name}")],
            [sg.Text("H1") for _ in range(6)],
        ]

    @preview(name="from static")
    @staticmethod
    def static_layout(name):
        return [
            [sg.Text(f"Hello, {name}")],
            [sg.Text("H1") for _ in range(6)],
        ]


@preview("defaults1", "from preview defaults!!")
@preview
def get_layout(name="world!!"):
    return [
        [sg.Text(f"Hello, {name}")],
        [sg.Text("H1") for _ in range(6)],
    ]


@preview
def preview3():
    return get_layout("human")


def main():
    sg.theme("DarkGray13")
    window = sg.Window(
        "Example",
        get_layout(),
        size=(280, 280),
        finalize=True)
    window.read(timeout=3)
    time.sleep(3)


if __name__ == '__main__':
    if sys.argv[1] == 'preview':
        preview()
    else:
        main()
