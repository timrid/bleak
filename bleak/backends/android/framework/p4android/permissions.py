from typing import Callable

from android.permissions import check_permission as p4a_check_permission  # type: ignore
from android.permissions import (
    request_permissions as p4a_request_permissions,  # type: ignore
)


def has_permission(permission: str) -> bool:
    """Checks if an app holds the passed permission."""

    # This is a function from python-for-android
    return p4a_check_permission(permission)


def request_permissions(
    permissions: list[str], callback: Callable[[list[str], list[int]], None]
) -> None:
    """Requests Android permissions."""

    # This is a function from python-for-android
    p4a_request_permissions(permissions, callback)
