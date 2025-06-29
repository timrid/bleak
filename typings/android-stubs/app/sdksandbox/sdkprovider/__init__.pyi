
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.app
import android.app.sdksandbox
import android.content
import android.os
import java.util
import java.util.concurrent
import typing



class SdkSandboxActivityHandler:
    def onActivityCreated(self, activity: android.app.Activity) -> None: ...

class SdkSandboxController:
    SDK_SANDBOX_CONTROLLER_SERVICE: typing.ClassVar[str] = ...
    def getAppOwnedSdkSandboxInterfaces(self) -> java.util.List[android.app.sdksandbox.AppOwnedSdkSandboxInterface]: ...
    def getClientPackageName(self) -> str: ...
    def getClientSharedPreferences(self) -> android.content.SharedPreferences: ...
    def getSandboxedSdks(self) -> java.util.List[android.app.sdksandbox.SandboxedSdk]: ...
    def loadSdk(self, string: str, bundle: android.os.Bundle, executor: typing.Union[java.util.concurrent.Executor, typing.Callable], outcomeReceiver: typing.Union[android.os.OutcomeReceiver[android.app.sdksandbox.SandboxedSdk, android.app.sdksandbox.LoadSdkException], typing.Callable[[android.app.sdksandbox.SandboxedSdk], None]]) -> None: ...
    def registerSdkSandboxActivityHandler(self, sdkSandboxActivityHandler: typing.Union[SdkSandboxActivityHandler, typing.Callable]) -> android.os.IBinder: ...
    def unregisterSdkSandboxActivityHandler(self, sdkSandboxActivityHandler: typing.Union[SdkSandboxActivityHandler, typing.Callable]) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.app.sdksandbox.sdkprovider")``.

    SdkSandboxActivityHandler: typing.Type[SdkSandboxActivityHandler]
    SdkSandboxController: typing.Type[SdkSandboxController]
