import os

from bleak.exc import BleakError

if os.environ.get("P4A_BOOTSTRAP") is not None:
    from bleak.backends.android.framework.p4android import (
        broadcast,  # noqa: F401
        client_callback,  # noqa: F401
        defs,  # noqa: F401
        permissions,  # noqa: F401
        scanner_callback,  # noqa: F401
    )
elif os.environ.get("CHAQUOPY_PROCESS_TYPE") is not None:
    from bleak.backends.android.framework.chaquopy import (
        broadcast,  # noqa: F401
        client_callback,  # noqa: F401
        defs,  # noqa: F401
        permissions,  # noqa: F401
        scanner_callback,  # noqa: F401
    )
else:
    raise BleakError("No supported Android framework detected.")
