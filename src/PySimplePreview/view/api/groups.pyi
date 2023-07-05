import typing
from typing import overload

from PySimplePreview.view.api.preview import LAYOUT_HOLDER

F = typing.TypeVar("F", bound=LAYOUT_HOLDER)

@overload
def group_previews(func: F) -> F:
    ...

@overload
def group_previews(group_name: str = None) -> typing.Callable[[F], F]:
    """
    | Set default value of **group_name** parameter for all **@[method_]preview**'s above it
    | Use this on functions with multiple previews applied
    | No-params form can be called without parentheses

    :param group_name: Custom previews group name, if nothing presented function name used
    :return: Returns wrapper, which will return same function as was consumed
    """
    ...
