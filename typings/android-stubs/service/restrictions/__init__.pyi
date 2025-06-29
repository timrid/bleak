
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.content
import android.os
import typing



class RestrictionsReceiver(android.content.BroadcastReceiver):
    def __init__(self): ...
    def onReceive(self, context: android.content.Context, intent: android.content.Intent) -> None: ...
    def onRequestPermission(self, context: android.content.Context, string: str, string2: str, string3: str, persistableBundle: android.os.PersistableBundle) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.service.restrictions")``.

    RestrictionsReceiver: typing.Type[RestrictionsReceiver]
