#  Use this to not couple with develop-only dependency
try:  # Used when package installed
    # noinspection PyUnresolvedReferences
    from PySimplePreview import preview, group_previews
except ImportError:  # Used when no dependency found
    # noinspection PyUnusedLocal
    def preview(*args, **ignored):
        def dummy_wrapper(f):
            return f

        if args[0] is not None and not isinstance(args[0], str):
            return args[0]

        return dummy_wrapper

    group_previews = preview
