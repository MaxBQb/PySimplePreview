import PySimpleGUI as sg


#  Use this to not couple with develop-only dependency
try:
    try:  # Used when package installed
        # noinspection PyUnresolvedReferences
        from PySimplePreview import preview
    except ImportError:  # Developer-only
        # noinspection PyUnresolvedReferences
        from PySimplePreview import preview
except ImportError:  # Used when no dependency found
    # noinspection PyUnusedLocal
    def preview(*args, **ignored):
        def dummy_wrapper(f):
            return f

        if args[0] is not None and not isinstance(args[0], str):
            return args[0]

        return dummy_wrapper


@preview
def get_layout(name="world!!"):
    return [
        [sg.Text(f"Hello, independent {name}")],
        [sg.Text("H1") for _ in range(6)],
    ]


@preview
def preview3():
    return get_layout("independent human")

