
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.app
import android.content
import android.os
import typing



class VrListenerService(android.app.Service):
    SERVICE_INTERFACE: typing.ClassVar[str] = ...
    def __init__(self): ...
    @staticmethod
    def isVrModePackageEnabled(context: android.content.Context, componentName: android.content.ComponentName) -> bool: ...
    def onBind(self, intent: android.content.Intent) -> android.os.IBinder: ...
    def onCurrentVrActivityChanged(self, componentName: android.content.ComponentName) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.service.vr")``.

    VrListenerService: typing.Type[VrListenerService]
