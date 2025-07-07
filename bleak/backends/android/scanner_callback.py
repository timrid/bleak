import dataclasses

from bleak.backends.android.dispatcher import (
    CallbackApi,
    CallbackResult,
    EmptyCallbackResult,
)

None

# if os.environ.get("CHAQUOPY_PROCESS_TYPE") is not None:
from bleak.backends.android.chaquopy import defs

# elif os.environ.get("P4A_BOOTSTRAP") is not None:
#     from bleak.backends.android.p4android import defs
# else:
#     raise BleakError("No supported Android environment detected.")


@dataclasses.dataclass
class OnScanResult(CallbackResult):
    result: None | defs.ScanResult


@dataclasses.dataclass(frozen=True)
class OnScanCallback(CallbackApi[OnScanResult]):
    pass
