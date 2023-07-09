# Quick Overview
This is python tool which provide realtime/live/hot preview of [PySimpleGUI](https://pypi.org/project/PySimpleGUI/) layouts.
This tool assumes that developer writes layouts as separate method/function(-s).
> Note: Layout is simply list of lists of PySimpleGUI elements.
## Usage
### Prepare your project
This tool is development-only dependency, so before you start using it, lets help python resolve it as optional dependency:
1. First, if you store dependencies in `requirements.txt`, add separate file e.g. `requirements-dev.txt`
  (you will be able to install all requirement with `pip install -r requirements.txt -r requirements-dev.txt`).
2. Then I suggest create new module (you may also inline it's content in your code which is bad, but possible).
With this content:
```py
#  Use this to not couple with develop-only dependency
try:  # Used when package installed
    # noinspection PyUnresolvedReferences
    from PySimplePreview import *
except ImportError:  # Used when no dependency found
    # noinspection PyUnusedLocal
    def preview(*args, **ignored):
        def dummy_wrapper(f):
            return f

        if args[0] is not None and not isinstance(args[0], str):
            return args[0]

        return dummy_wrapper

    def params(*args, **kwargs):
        return args, kwargs

    group_previews = preview
    method_previews = preview
```

3. If you've created separate module, then you can simply import anything from it instead of PySimplePreview.
> Note: You can always use custom technique to manage optional python dependencies, this is just example.

Now your app can work with and without PySimplePreview!

### Examples
1. First you need to import `preview` decorator from PySimplePreview (or yours custom module which tries to import it).
```py
import PySimpleGUI as sg
import PySimplePreview as psp
# ... or custom module name, e.g. _PySimplePreview
import _PySimplePreview as psp
```
2. Then you can decorate any callable that returns layout with `preview`.
Example:
```py
@psp.preview
def get_layout():
    return [
        [sg.Text("Hello, world!")]
    ]
```
3. Now you can run PySimplePreview with `python -m PySimplePreview`.
4. Select path to your project's root and choose preview to be shown.
5. Edit your layout without closing PySimplePreview.
Example:
```py
@psp.preview
def get_layout():
    return [
        [sg.Text("Hello, world!")],
        [sg.Text("Previews are cool!")],
    ]
```
6. Remember to save your changes and *magic happens*: it's reflected in preview window.

For more complex cases see [examples](examples/).

## Features 
### PySimplePreview API
1. `@preview` without params for functions and static methods.
    1. `@preview()` for parameters:
    2. Custom name of preview.
    3. Parameters for function to be called with (can be evaluated lazily).
    4. Custom group name (use for ease of searching, and maybe for something special later on).
    5. Custom window (Use own PySimpleGUI windows to preview own layouts).
3. `@method_preview` same as `@preview` but for class methods and properties.
    1. Have same parameters as `@preview()`, additionally have optional `instance_provider` parameter to provide `self` for methods.
    2. `instance_provider` can use cls parameter to create class instance.
    3. `instance_provider` can have no parameters to provide class instance from some other place.
    4. `instance_provider` can be omitted, then no-args constructor of class will be used.
4. Multiple previews may be applied to same callable.
5. `@group_previews` can be used to set group_name for multiple previews of same callable.
    1. `@group_previews()` name can be set as parameter.
6. In case when preview_name omitted, fully-qualified callable name will be used (`package.module.function_name` or `module.function_name`).
7. Same goes for `group_previews` no-param form.

### PySimplePreview App
1. Preview Theme can be customised.
2. App remembers its position and size (toggleable).
3. App stays on top of other windows (toggleable).
4. Preview window can be separated from main app window.
5. Previews can be filtered by groups.
6. App supports execution params see `python -m PySimplePreview -h`.
7. See app logs for more info (it also contains handled user-defined events from layout previewed).
8. If you want to see update on any module edited (when layout depends on other module), you may toggle Reload All option.
9. App supports observing single module, package with `__init__.py` file and just flat-layout (folder with `.py` files).

# Docs
There is no readthedocs page for this project for now (it may be changed soon).
But public API well-documented in code and covered with typehints (supported by PyCharm).
All features using can be found in [examples](examples/).

# Compatability
## Python versions support
For now only Python 3.11 tested, but older versions support planned.

## PySimpleGUI versions support
Currently tested on PySimpleGUI 4.60.5, 
I'll think about adding support for older versions later,
better use latest releases anyway :)

## Different PySimpleGUI backends
Currently tested only with tkinter backend, 
I have plans for framework-agnostic version.

# Contribution
Feel free to [open issues](https://github.com/MaxBQb/PySimplePreview/issues/new), but be careful with PR's (small fixes are OK, but this is MVP project, 
it's implementation can be changed in any way).
Also note that I may have not enough free time, so have patience.
