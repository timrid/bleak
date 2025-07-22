import dataclasses
from typing import TYPE_CHECKING

from bleak.backends.android.dispatcher import (
    CallbackApi,
    CallbackResult,
)

if TYPE_CHECKING:
    # Only for type checking. At runtime this results in an error.
    from bleak.backends.android.framework.framework import defs


@dataclasses.dataclass
class OnScanResult(CallbackResult):
    result: "None | defs.ScanResult"


@dataclasses.dataclass(frozen=True)
class OnScanCallback(CallbackApi[OnScanResult]):
    pass
