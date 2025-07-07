import asyncio

from android import Manifest
from android.content.pm import PackageManager
from android.os import Build

from bleak.backends.android.chaquopy.defs import activity


async def check_for_permissions(loop: asyncio.AbstractEventLoop):
    """Check for and request neccessary BLE permissions.

    This was a hard one. Hard to find which permissions are really
    neccessary and especially WHICH ONE ARE NOT ALLOWED TO ASK FOR
    AT THE SAME TIME.
    BLUETOOTH and BLUETOOTH_ADMIN don't require runtime permission,
    ACCESS_FINE_LOCATION does contain ACCESS_COARSE_LOCATION and
    ACCESS_BACKGROUND_LOCATION (?).
    """
    api_level = Build.VERSION.SDK_INT
    if api_level >= 23 and api_level <= 30:
        permissions = [
            Manifest.permission.ACCESS_FINE_LOCATION,
        ]
    elif api_level > 30:
        permissions = [
            Manifest.permission.BLUETOOTH_SCAN,
            Manifest.permission.BLUETOOTH_CONNECT,
        ]
    else:
        raise ValueError("unknown api level")
    permissions_granted = all(
        activity.checkSelfPermission(permission) == PackageManager.PERMISSION_GRANTED
        for permission in permissions
    )
    if not permissions_granted:
        activity.requestPermissions(permissions, 101)
