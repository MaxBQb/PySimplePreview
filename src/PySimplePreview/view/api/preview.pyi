import typing
from typing import Callable, overload

from PySimplePreview.domain.model.preview import WINDOW_PROVIDER

T = typing.TypeVar('T')
Ts = typing.TypeVarTuple("Ts")
T2s = typing.TypeVarTuple("T2s")
INSTANCE_PROVIDER: typing.TypeAlias = Callable[[typing.Type[T]], T] | Callable[[], T]
LAYOUT_HOLDER: typing.TypeAlias = Callable[[...], list[list]]
SUPPORTED_LAYOUT_HOLDERS: typing.TypeAlias = LAYOUT_HOLDER | '_MethodPreview' | property | staticmethod
PARAMS: typing.TypeAlias = tuple[tuple[*Ts], dict[str, *T2s]]
PARAMS_PROVIDER: typing.TypeAlias = Callable[[], tuple[tuple[*Ts], dict[str, *T2s]]]



def params(*args: Ts, **kwargs: T2s) -> tuple[tuple[*Ts], dict[str, *T2s]]:
    """
    | Simply supply interface to inner *args, **kwargs used in any function.
    | Usage:
    | >>> some_func(inner_params=params(arg1, args, *args, kwarg1=kwarg1, kwarg2=kwarg2, **kwargs))

    :param args: Any positional arguments
    :param kwargs: Any keyword arguments
    :return: All values received packed as one value
    """
    ...


F = typing.TypeVar("F", bound=LAYOUT_HOLDER)


@overload
def preview(func: F) -> F: ...

@overload
def preview(
    name: str = None,
    group_name: str = None,
    window_provider: WINDOW_PROVIDER = None,
    call_params: PARAMS_PROVIDER | PARAMS  = params
) -> Callable[[F], F]:
    """
    | Marks function/staticmethod as source of layout for live preview
    | No-params form can be called without parentheses

    :param name: Custom preview name, shown instead of (sometimes with) regular function name
    :param group_name: Set package-global group name (previews can be grouped by this parameter value)
    :param window_provider: Custom `PySimpleGUI.Window` provider, callable that accept current size,
        position and layout of window to display and returns finalized window
    :param call_params: Any positional and keyword arguments for source function to be called with on preview creation.
        Suggest to use params function:
        @preview(..., call_params=params(arg1, args, *args, kwarg1=kwarg1, kwarg2=kwarg2, **kwargs))
        For lazy evaluation wrap same code with `lambda:`
        @preview(..., call_params=lambda: params(arg1, args, *args, kwarg1=kwarg1, kwarg2=kwarg2, **kwargs))
    :return: Wraps methods with special class (will be erased after class initialisation),
        when function presented returns wrapper, which will return same function
    """
    ...


M = typing.TypeVar("M", LAYOUT_HOLDER, _MethodPreview, property, staticmethod)


@overload
def method_preview(meth: M) -> M: ...

@overload
def method_preview(
    name: str = None,
    group_name: str = None,
    window_provider: WINDOW_PROVIDER = None,
    instance_provider: INSTANCE_PROVIDER = None,
    call_params: PARAMS_PROVIDER | PARAMS = params,
) -> Callable[[M], M]:
    """
    | Marks method/property as source of layout for live preview
    | No-params form can be called without parentheses

    :param name: Custom preview name, shown instead of (sometimes with) regular function name
    :param group_name: Set package-global group name (previews can be grouped by this parameter value)
    :param window_provider: Custom `PySimpleGUI.Window` provider, callable that accept current size,
        position and layout of window to display and returns finalized window
    :param instance_provider: Source of method's class instances, this function can accept optional class parameter
        if no instance_provider set, default no-args constructor of class will be used.
    :param call_params: Any positional and keyword arguments for source function to be called with on preview creation.
        Note: self param adds via **instance_provider**
        Suggest to use params function:
        @method_preview(..., call_params=params(arg1, args, *args, kwarg1=kwarg1, kwarg2=kwarg2, **kwargs))
        For lazy evaluation wrap same code with `lambda:`
        @method_preview(..., call_params=lambda: params(arg1, args, *args, kwarg1=kwarg1, kwarg2=kwarg2, **kwargs))
    :return: Wraps method with special class (will be replaced back to `M` after owner class initialisation)
    """
    ...

class _MethodPreview: ...