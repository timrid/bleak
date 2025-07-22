import asyncio

from bleak.backends.android.framework import defs, permissions
from bleak.exc import BleakPermissionsDeniedError


def _required_ble_permissions() -> list[str]:
    """
    Get the required BLE permissions.

    This depends on the Android API Version.
    """
    api_level = defs.Build.VERSION.SDK_INT
    if api_level >= 23 and api_level <= 30:
        return [
            defs.Manifest.permission.ACCESS_FINE_LOCATION,
            defs.Manifest.permission.ACCESS_BACKGROUND_LOCATION,  # optional: only if scanning BLE devices in background
        ]
    elif api_level > 30:
        return [
            defs.Manifest.permission.BLUETOOTH_SCAN,
            defs.Manifest.permission.BLUETOOTH_CONNECT,
        ]
    else:
        raise ValueError("unknown api level")


async def check_for_permissions(loop: asyncio.AbstractEventLoop):
    required_ble_permissions = _required_ble_permissions()

    # Check if permissions are already granted
    permissions_granted = all(
        permissions.has_permission(p) for p in required_ble_permissions
    )
    if permissions_granted:
        return

    permission_acknowledged = loop.create_future()

    def handle_permissions(permissions: list[str], grantResults: list[int]):
        grant_results = [
            granted_result == defs.PackageManager.PERMISSION_GRANTED
            for granted_result in grantResults
        ]
        if all(grant_results):
            loop.call_soon_threadsafe(
                permission_acknowledged.set_result,
                grant_results,
            )
        else:
            loop.call_soon_threadsafe(
                permission_acknowledged.set_exception,
                BleakPermissionsDeniedError(permissions),
            )

    # Request the permissions
    permissions.request_permissions(
        required_ble_permissions,
        handle_permissions,
    )
    await permission_acknowledged
