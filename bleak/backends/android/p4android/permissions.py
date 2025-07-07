import asyncio

from android.permissions import Permission, request_permissions

from bleak.exc import BleakError


async def check_for_permissions(loop: asyncio.AbstractEventLoop):
    permission_acknowledged = loop.create_future()

    def handle_permissions(permissions, grantResults):
        if any(grantResults):
            loop.call_soon_threadsafe(permission_acknowledged.set_result, grantResults)
        else:
            loop.call_soon_threadsafe(
                permission_acknowledged.set_exception(
                    BleakError("User denied access to " + str(permissions))
                )
            )

    request_permissions(
        [
            Permission.ACCESS_FINE_LOCATION,
            Permission.ACCESS_COARSE_LOCATION,
            "android.permission.ACCESS_BACKGROUND_LOCATION",
        ],
        handle_permissions,
    )
    await permission_acknowledged
