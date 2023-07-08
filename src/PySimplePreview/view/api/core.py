from pathlib import Path

from PySimplePreview.data.previews_storage import PreviewsStorage
from PySimplePreview.domain.interactor.previews_manager import get_qualified_name
from PySimplePreview.domain.model.preview import WINDOW_PROVIDER
from PySimplePreview.view.api._types import *
from PySimplePreview.view.api._utils import *
from PySimplePreview.view.app import Application


def _group_previews(group_name: str = None):
    def wrapper(f):
        f.preview_group_name = group_name or get_qualified_name(f, Path(inspect.getfile(f)))
        return f
    return wrapper


def group_previews(group_name: str = None):
    if group_name is None or isinstance(group_name, str):
        return _group_previews(group_name)
    return _group_previews()(group_name)


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
        app = Application.current
        if not app:
            return f  # Do nothing, when user app started
        # Go next only when own app is running
        previews = app.container.resolve(PreviewsStorage).previews
        previews.add_preview(
            name=qualname,
            layout_provider=lambda: call_with_params(f, call_params),
            module_path=module_path,
            group_name=_group_name,
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
        _meth = MethodPreview.extract_function(_meth)
        _group_name = getattr(_meth, "preview_group_name", _group_name)
        _meth.preview_group_name = _group_name
        return preview(
            name=name,
            group_name=group_name,
            window_provider=window_provider,
            call_params=lambda: wrap_method_params(_instance_provider(), call_params)
        )(_meth)

    return MethodPreview(
        instance_provider=instance_provider,
        on_instance_received=get_layout
    )


def method_preview(*args, **kwargs):
    func = args[0] if len(args) else None
    if func is None or isinstance(func, str):
        return _method_preview(*args, **kwargs)
    return _method_preview(*args[1:], **kwargs)(func)
