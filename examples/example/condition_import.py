#  Use this to not couple with develop-only dependency
try:
    from src.PySimplePreview import preview
except:
    def preview(*args, **kwargs):
        def dummy_wrapper(f):
            return f

        if args[0] is not None and not isinstance(args[0], str):
            return args[0]

        return dummy_wrapper
