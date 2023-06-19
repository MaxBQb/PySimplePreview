import sys
import time

import PySimpleGUI as sg


def preview():
    sg.Window(
        "Example",
        get_layout(),
        size=(280, 280),
        keep_on_top=True,
        finalize=True).read()


def get_layout(name="world!!"):
    return [
        [sg.Text(f"Hello, {name}")],
        [sg.Text("H1") for _ in range(6)],
    ]


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
