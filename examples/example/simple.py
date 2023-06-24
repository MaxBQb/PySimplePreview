import time

import PySimpleGUI as sg

from src.PySimplePreview import preview


def get_instance(name):
    return ExampleClass(name)


class ExampleClass:
    def __init__(self, name: str = "from no param class"):
        self.name = name

    @preview
    @preview("default for class2", instance_provider=lambda: get_instance(name="from singleton"))
    @preview("default for class1", instance_provider=lambda cls: cls(name="from class again"))
    @preview("default for class", instance_provider=lambda: ExampleClass(name="from class"))
    def get_layout(self):
        return [
            [sg.Text(f"Hello, {self.name}")],
            [sg.Text("H1") for _ in range(6)],
        ]

    @preview(instance_provider=lambda cls: cls("from property"))
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
    main()
