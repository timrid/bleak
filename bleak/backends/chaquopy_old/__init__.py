"""
bleekWare, a limited replacement for Bleak to use BLE on Android
within the BeeWare framework.

The code is heavily inspired by Bleak (https://github.com/hbldh/bleak).
Some parts may virtually be identical for the sake of compatibility to
Bleak.

(c) 2024 by Markus Piotrowski

MIT license
"""

from android import Manifest
from android.app import Activity
from android.bluetooth import BluetoothGattService
from android.content.pm import PackageManager
from android.os import Build


class BLEGattService:

    def __init__(self, service: BluetoothGattService):
        self.service: BluetoothGattService = service
        self.characteristics: list[str] = []
        self.descriptors = []


def check_for_permissions(activity: Activity):
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
        activity.checkSelfPermission(permission)
        == PackageManager.PERMISSION_GRANTED
        for permission in permissions
    )
    if not permissions_granted:
        activity.requestPermissions(permissions, 101)
