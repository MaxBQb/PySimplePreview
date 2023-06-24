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


T = typing.TypeVar('T')
INSTANCE_PROVIDER: typing.TypeAlias = Callable[[typing.Type[T]], T] | Callable[[], T]
SUPPORTED_LAYOUT_HOLDERS: typing.TypeAlias = Callable[[...], list[list]] | '_MethodPreview' | property


def preview(
    preview_name: str = None,
    *args,
    is_method=False,
    instance_provider: INSTANCE_PROVIDER = None,
    **kwargs,
):
    f = None
    if preview_name is not None and not isinstance(preview_name, str):
        f = preview_name
        preview_name = None
        is_method |= _MethodPreview.is_method(f)
    is_method |= instance_provider is not None

    if is_method and not getattr(instance_provider, '_instance_provided', False):
        return _MethodPreview(
            fn=f,
            instance_provider=instance_provider,
            on_instance_received=lambda provider, _f: preview(
                preview_name, *args,
                instance_provider=provider,
                **kwargs
            )(_f)
        )

    def get_layout(func: Callable[[...], list[list]] | staticmethod):
        func = _MethodPreview.extract_function(func)
        module_path = Path(inspect.getfile(func))
        module_parents = get_longest_module_name(Path(module_path))
        qualname = f"{'.'.join(module_parents)}.{func.__qualname__}"
        if instance_provider:
            layout_provider = lambda: func(instance_provider(), *args, **kwargs)
        else:
            layout_provider = lambda: func(*args, **kwargs)
        PreviewsStorage.get().previews.add_preview(
            name=f"{qualname}:{preview_name}" if preview_name else qualname,
            layout_provider=layout_provider,
            module_path=module_path
        )
        return func

    if f:
        return get_layout(f)
    return get_layout


class _MethodPreview:
    def __init__(
        self,
        fn: SUPPORTED_LAYOUT_HOLDERS,
        instance_provider: INSTANCE_PROVIDER = None,
        on_instance_received: Callable[
            [typing.Any, Callable[[...], list[list]]], Callable[[...], list[list]]] = None,
    ):
        self.fn = fn
        self.instance_provider = instance_provider
        self.on_instance_received = on_instance_received

    def __call__(self, fn: SUPPORTED_LAYOUT_HOLDERS):
        self.fn = fn
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
        setattr(owner, name, self.fn)
        try:
            self.fn.__set_name__(owner, name)
        except AttributeError:
            self.fn.class_name = owner.__name__
        self.fn = self.extract_function(getattr(owner, name))
        provider = lambda: self._make_instance(owner)
        provider._instance_provided = True
        self.fn = self.on_instance_received(provider, self.fn)

    @staticmethod
    def extract_function(value: SUPPORTED_LAYOUT_HOLDERS):
        if value is None:
            return
        if isinstance(value, property):
            return value.fget
        if isinstance(value, staticmethod):
            return value.__func__
        return value
