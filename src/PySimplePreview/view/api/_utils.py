import inspect
from PySimplePreview.view.api._types import *


def params(*args, **kwargs):
    return args, kwargs


def unpack(value: PARAMS_PROVIDER | PARAMS) -> PARAMS:
    if isinstance(value, tuple):
        return value
    return value()


def wrap_method_params(self, method_params: PARAMS_PROVIDER | PARAMS):
    args, kwargs = unpack(method_params)
    return params(self, *args, **kwargs)


def call_with_params(func: Callable[[*Ts, *T2s], T], func_params: PARAMS_PROVIDER | PARAMS):
    args, kwargs = unpack(func_params)
    return func(*args, **kwargs)


class MethodPreview:
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
