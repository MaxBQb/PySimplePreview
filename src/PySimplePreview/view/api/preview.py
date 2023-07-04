import inspect
import typing
from pathlib import Path
from typing import Callable

from PySimplePreview.data.previews_storage import PreviewsStorage
from PySimplePreview.domain.interactor.previews_manager import get_qualified_name
from PySimplePreview.domain.model.preview import WINDOW_PROVIDER
from PySimplePreview.view.app import Application

T = typing.TypeVar('T')
INSTANCE_PROVIDER: typing.TypeAlias = Callable[[typing.Type[T]], T] | Callable[[], T]
LAYOUT_HOLDER: typing.TypeAlias = Callable[[...], list[list]]
SUPPORTED_LAYOUT_HOLDERS: typing.TypeAlias = LAYOUT_HOLDER | '_MethodPreview' | property | staticmethod


def preview(
    preview_name: str = None,
    *args,
    is_method=False,
    instance_provider: INSTANCE_PROVIDER = None,
    preview_group_name: str = None,
    preview_window_provider: WINDOW_PROVIDER = None,
    **kwargs,
):
    """
    | Marks function/method/property as source of layout for live preview
    | No-params form can be called without parentheses

    :param preview_name: Custom preview name, shown instead of (sometimes with) regular function name
    :param args: Any positional arguments for source function to be called with on preview creation
    :param is_method: Determines if callable is a method.
        Automatically set to True, on applying to **property**, or when **class_params** set.
        Do not use this on **staticmethod**.
    :param instance_provider: Source of method's class instances, this function can accept optional class parameter
        if no instance_provider set, default no-args constructor of class will be used.
    :param preview_group_name: Set package-global group name (previews can be grouped by this parameter value)
    :param preview_window_provider: Custom `PySimpleGUI.Window` provider, callable that accept current size,
        position and layout of window to display and returns finalized window
    :param kwargs: Any keyword arguments for source function to be called with on preview creation
    :return: Wraps methods with special class (will be erased after class initialisation),
        when function presented returns wrapper, which will return same function
    """
    function_to_wrap: SUPPORTED_LAYOUT_HOLDERS = None
    if preview_name is not None and not isinstance(preview_name, str):
        function_to_wrap = preview_name
        preview_name = None
        is_method |= _MethodPreview.is_method(function_to_wrap)
    is_method |= instance_provider is not None

    if is_method and not getattr(instance_provider, '_instance_provided', False):
        return _MethodPreview(
            function=function_to_wrap,
            instance_provider=instance_provider,
            on_instance_received=lambda provider, _f: preview(
                preview_name, *args,
                is_method=is_method,
                instance_provider=provider,
                preview_group_name=preview_group_name,
                preview_window_provider=preview_window_provider,
                **kwargs
            )(_f)
        )

    def get_layout(func: SUPPORTED_LAYOUT_HOLDERS):
        group_name = getattr(func, "preview_group_name", None)
        func = _MethodPreview.extract_function(func)
        group_name = getattr(func, "preview_group_name", group_name)
        group_name = preview_group_name or group_name
        module_path = Path(inspect.getfile(func))
        qualname = get_qualified_name(func, module_path, preview_name)
        if instance_provider:
            layout_provider = lambda: func(instance_provider(), *args, **kwargs)
        else:
            layout_provider = lambda: func(*args, **kwargs)
        Application.current.container.resolve(PreviewsStorage).previews.add_preview(
            name=qualname,
            layout_provider=layout_provider,
            module_path=module_path,
            group_name=group_name,
            window_provider=preview_window_provider,
        )
        return func

    if function_to_wrap:
        return get_layout(function_to_wrap)
    return get_layout


class _MethodPreview:
    def __init__(
        self,
        function: SUPPORTED_LAYOUT_HOLDERS,
        instance_provider: INSTANCE_PROVIDER = None,
        on_instance_received: Callable[[typing.Any, LAYOUT_HOLDER], LAYOUT_HOLDER] = None,
    ):
        self.function = function
        self.instance_provider = instance_provider
        self.on_instance_received = on_instance_received

    def __call__(self, fn: SUPPORTED_LAYOUT_HOLDERS):
        self.function = fn
        return self

    def _make_instance(self, class_):
        if self.instance_provider is None:
            return class_()
        if len(inspect.getfullargspec(self.instance_provider).args) == 0:
            return self.instance_provider()
        return self.instance_provider(class_)

    @staticmethod
    def is_method(f: SUPPORTED_LAYOUT_HOLDERS):
        return f is not None and (
            isinstance(f, _MethodPreview)
            or isinstance(f, property)
        )

    def __set_name__(self, owner, name):
        # replace self with the original method
        setattr(owner, name, self.function)
        try:
            self.function.__set_name__(owner, name)
        except AttributeError:
            self.function.class_name = owner.__name__
        self.function = self.extract_function(getattr(owner, name))
        provider = lambda: self._make_instance(owner)
        provider._instance_provided = True
        self.function = self.on_instance_received(provider, self.function)

    @staticmethod
    def extract_function(value: SUPPORTED_LAYOUT_HOLDERS):
        if value is None:
            return
        if isinstance(value, property):
            return value.fget
        if isinstance(value, staticmethod):
            return value.__func__
        return value
