import inspect
import typing
from pathlib import Path
from typing import Callable

from PySimplePreview.data.previews_storage import PreviewsStorage
from PySimplePreview.domain.interactor.previews_manager import get_qualified_name
from PySimplePreview.domain.model.preview import WINDOW_PROVIDER
from PySimplePreview.view.app import Application

T = typing.TypeVar('T')
Ts = typing.TypeVarTuple("Ts")
T2s = typing.TypeVarTuple("T2s")
INSTANCE_PROVIDER: typing.TypeAlias = Callable[[typing.Type[T]], T] | Callable[[], T]
LAYOUT_HOLDER: typing.TypeAlias = Callable[..., list[list]]
SUPPORTED_LAYOUT_HOLDERS: typing.TypeAlias = LAYOUT_HOLDER | '_MethodPreview' | property | staticmethod
PARAMS: typing.TypeAlias = tuple[tuple[*Ts], dict[str, *T2s]]
PARAMS_PROVIDER: typing.TypeAlias = Callable[[], PARAMS]


def params(*args, **kwargs):
    return args, kwargs


def _unpack(value: PARAMS_PROVIDER | PARAMS) -> PARAMS:
    if isinstance(value, tuple):
        return value
    return value()


def _wrap_method_params(self, method_params: PARAMS_PROVIDER | PARAMS):
    args, kwargs = _unpack(method_params)
    return params(self, *args, **kwargs)


def _call_with_params(func: Callable[[*Ts, *T2s], T], func_params: PARAMS_PROVIDER | PARAMS):
    args, kwargs = _unpack(func_params)
    return func(*args, **kwargs)


def _preview(
    name: str = None,
    group_name: str = None,
    window_provider: WINDOW_PROVIDER = None,
    call_params: PARAMS_PROVIDER | PARAMS = params
):
    def get_layout(f: LAYOUT_HOLDER):
        _group_name = getattr(f, "preview_group_name", None)
        _group_name = group_name or _group_name
        module_path = Path(inspect.getfile(f))
        qualname = get_qualified_name(f, module_path, name)
        Application.current.container.resolve(PreviewsStorage).previews.add_preview(
            name=qualname,
            layout_provider=lambda: _call_with_params(f, call_params),
            module_path=module_path,
            group_name=group_name,
            window_provider=window_provider,
        )
        return f
    return get_layout


def preview(*args, **kwargs):
    func = args[0] if len(args) else None
    if func is None or isinstance(func, str):
        return _preview(*args, **kwargs)
    return _preview(*args[1:], **kwargs)(func)


def _method_preview(
    name: str = None,
    group_name: str = None,
    window_provider: WINDOW_PROVIDER = None,
    instance_provider: INSTANCE_PROVIDER = None,
    call_params: PARAMS_PROVIDER | PARAMS = params,
):
    def get_layout(_instance_provider, _meth: SUPPORTED_LAYOUT_HOLDERS):
        _group_name = getattr(_meth, "preview_group_name", None)
        _meth = _MethodPreview.extract_function(_meth)
        _group_name = getattr(_meth, "preview_group_name", _group_name)
        _meth.preview_group_name = _group_name
        return preview(
            name=name,
            group_name=group_name,
            window_provider=window_provider,
            call_params=lambda: _wrap_method_params(_instance_provider(), call_params)
        )(_meth)

    return _MethodPreview(
        instance_provider=instance_provider,
        on_instance_received=get_layout
    )


def method_preview(*args, **kwargs):
    func = args[0] if len(args) else None
    if func is None or isinstance(func, str):
        return _method_preview(*args, **kwargs)
    return _method_preview(*args[1:], **kwargs)(func)


class _MethodPreview:
    def __init__(
        self,
        instance_provider: INSTANCE_PROVIDER = None,
        on_instance_received: Callable[[typing.Any, LAYOUT_HOLDER], LAYOUT_HOLDER] = None,
    ):
        self.function = None
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

    def __set_name__(self, owner, name):
        # replace self with the original method
        setattr(owner, name, self.function)
        try:
            self.function.__set_name__(owner, name)
        except AttributeError:
            self.function.class_name = owner.__name__
        self.function = self.extract_function(getattr(owner, name))
        self.function = self.on_instance_received(lambda: self._make_instance(owner), self.function)

    @staticmethod
    def extract_function(value: SUPPORTED_LAYOUT_HOLDERS):
        if value is None:
            return
        if isinstance(value, property):
            return value.fget
        if isinstance(value, staticmethod):
            return value.__func__
        return value
