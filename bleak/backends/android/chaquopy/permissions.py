from typing import Callable

from toga.app import App as TogaCoreApp
from toga_android.app import App as TogaAndroidApp

from bleak.backends.android.chaquopy import defs
from bleak.exc import BleakError


def has_permission(permission: str) -> bool:
    """Check if a permission is granted"""
    result = defs.activity.checkSelfPermission(permission)
    return result == defs.PackageManager.PERMISSION_GRANTED


def _get_running_toga_android_app() -> TogaAndroidApp:
    """Get the currently running toga app"""
    app = TogaCoreApp.app
    if app is None:
        raise BleakError("No running toga app detected.")
    if not isinstance(app._impl, TogaAndroidApp):
        raise BleakError(f"'{app}' is an invalid app")
    return app._impl


def request_permissions(
    permissions: list[str], callback: Callable[[list[str], list[int]], None]
) -> None:
    android_app = _get_running_toga_android_app()
    android_app.request_permissions(
        permissions,
        on_complete=callback,
    )
