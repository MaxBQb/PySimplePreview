import time

import PySimpleGUI as sg

from condition_import import preview, group_previews, method_preview, params


def get_instance(name):
    return ExampleClass(name)


class ExampleClass:
    def __init__(self, name: str = "from no param class"):
        self.name = name

    @method_preview
    @method_preview("default for class2", instance_provider=lambda: get_instance(name="from singleton"))
    @method_preview("default for class1", instance_provider=lambda cls: cls(name="from class again"))
    @method_preview("default for class", instance_provider=lambda: ExampleClass(name="from class"))
    @group_previews("first group")
    def get_layout(self):
        return [
            [sg.Text(f"Hello, {self.name}")],
            [sg.Text("H1") for _ in range(6)],
        ]

    @method_preview(instance_provider=lambda cls: cls("from property"))
    @method_preview("property with default params")
    @property
    @group_previews("second group")
    def layout(self):
        return [
            [sg.Text(f"Hello, {self.name}")],
            [sg.Text("H1") for _ in range(6)],
        ]

    @staticmethod
    @preview(call_params=params(name="from static"))
    @group_previews("second group")
    def static_layout(name):
        return [
            [sg.Text(f"Hello, {name}")],
            [sg.Text("H1") for _ in range(6)],
        ]


@preview("defaults1", call_params=lambda: params("from preview defaults!!"), group_name="first group")
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
