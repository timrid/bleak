import dataclasses

from bleak.backends.android.dispatcher import (
    CallbackApi,
    CallbackResult,
)
from bleak.backends.android.framework.p4android import defs


@dataclasses.dataclass
class OnScanResult(CallbackResult):
    result: None | defs.ScanResult


@dataclasses.dataclass(frozen=True)
class OnScanCallback(CallbackApi[OnScanResult]):
    pass
