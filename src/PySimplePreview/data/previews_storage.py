import inspect
import typing
from pathlib import Path
from typing import Callable

from src.PySimplePreview.domain.interactor.previews_manager import PreviewsManager, get_longest_module_name


class PreviewsStorage:
    _instance = None

    def __init__(self):
        self.previews = PreviewsManager()

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance


def preview(preview_name: str = None, *args, is_method=False, class_params: tuple[tuple, dict[str]] = None, **kwargs):
    f = None
    if preview_name is not None and not isinstance(preview_name, str):
        f = preview_name
        preview_name = None
    is_method |= class_params is not None
    is_method |= _MethodPreview.is_method(f)
    if is_method:
        return _MethodPreview(
            f,
            class_params=class_params,
            on_instance_received=lambda instance, _f: preview(
                preview_name, instance, *args, **kwargs
            )(_f)
        )

    def get_layout(func: Callable[[...], list[list]] | staticmethod):
        if isinstance(func, staticmethod):
            func = func.__func__
        module_path = Path(inspect.getfile(func))
        module_parents = get_longest_module_name(Path(module_path))
        qualname = f"{'.'.join(module_parents)}.{func.__qualname__}"
        PreviewsStorage.get().previews.add_preview(
            name=f"{qualname}:{preview_name}" if preview_name else qualname,
            layout_provider= lambda: func(*args, **kwargs),
            module_path=module_path
        )
        return func

    if f:
        return get_layout(f)
    return get_layout


preview.class_params = lambda *args, **kwargs: (args, kwargs)


class _MethodPreview:
    SUPPORTED_LAYOUT_HOLDERS: typing.TypeAlias = Callable[[...], list[list]] | '_MethodPreview' | property

    def __init__(
        self,
        fn: SUPPORTED_LAYOUT_HOLDERS,
        class_params: tuple[tuple, dict[str]] = None,
        on_instance_received: Callable[[typing.Any, Callable[[...], list[list]]], Callable[[...], list[list]]] = None,
    ):
        self.fn = fn
        self.class_params = class_params
        self.on_instance_received = on_instance_received

    def __call__(self, fn: SUPPORTED_LAYOUT_HOLDERS):
        self.fn = fn
        return self

    def _make_instance(self, class_):
        class_args, class_kwargs = self.class_params or preview.class_params()
        return class_(*class_args, **class_kwargs)

    @staticmethod
    def is_method(f: SUPPORTED_LAYOUT_HOLDERS):
        return f is not None and (
            isinstance(f, _MethodPreview)
            or isinstance(f, property)
        )

    def __set_name__(self, owner, name):
        # replace self with the original method
        setattr(owner, name, self.fn)
        try:
            self.fn.__set_name__(owner, name)
        except AttributeError:
            self.fn.class_name = owner.__name__
        self.fn = self._extract_function(getattr(owner, name))
        self.fn = self.on_instance_received(self._make_instance(owner), self.fn)

    @staticmethod
    def _extract_function(value: SUPPORTED_LAYOUT_HOLDERS):
        if value is None:
            return
        if isinstance(value, property):
            return value.fget
        return value