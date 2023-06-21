import sys
import time

import PySimpleGUI as sg

from src.PySimplePreview import preview


def preview2():
    sg.Window(
        "Example",
        get_layout(),
        size=(280, 280),
        keep_on_top=True,
        finalize=True).read()


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
