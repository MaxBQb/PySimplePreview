import typing
from typing import Callable

from PySimplePreview.domain.model.preview import LAYOUT

if typing.TYPE_CHECKING:
    from PySimplePreview.view.api._utils import MethodPreview

T = typing.TypeVar('T')
Ts = typing.TypeVarTuple("Ts")
T2s = typing.TypeVarTuple("T2s")
INSTANCE_PROVIDER: typing.TypeAlias = Callable[[typing.Type[T]], T] | Callable[[], T]
LAYOUT_HOLDER: typing.TypeAlias = Callable[..., LAYOUT]
SUPPORTED_LAYOUT_HOLDERS: typing.TypeAlias = LAYOUT_HOLDER | 'MethodPreview' | property | staticmethod
PARAMS: typing.TypeAlias = tuple[tuple[*Ts], dict[str, *T2s]]
PARAMS_PROVIDER: typing.TypeAlias = Callable[[], PARAMS]
