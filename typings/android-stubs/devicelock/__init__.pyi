
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.os
import java.lang
import java.util
import java.util.concurrent
import typing



class DeviceId:
    DEVICE_ID_TYPE_IMEI: typing.ClassVar[int] = ...
    DEVICE_ID_TYPE_MEID: typing.ClassVar[int] = ...
    def getId(self) -> str: ...
    def getType(self) -> int: ...

class DeviceLockManager:
    DEVICE_LOCK_ROLE_FINANCING: typing.ClassVar[int] = ...
    def getDeviceId(self, executor: typing.Union[java.util.concurrent.Executor, typing.Callable], outcomeReceiver: typing.Union[android.os.OutcomeReceiver[DeviceId, java.lang.Exception], typing.Callable[[DeviceId], None]]) -> None: ...
    def getKioskApps(self, executor: typing.Union[java.util.concurrent.Executor, typing.Callable], outcomeReceiver: typing.Union[android.os.OutcomeReceiver[typing.Union[java.util.Map[int, str], typing.Mapping[int, str]], java.lang.Exception], typing.Callable[[typing.Union[java.util.Map[int, str], typing.Mapping[int, str]]], None]]) -> None: ...
    def isDeviceLocked(self, executor: typing.Union[java.util.concurrent.Executor, typing.Callable], outcomeReceiver: typing.Union[android.os.OutcomeReceiver[bool, java.lang.Exception], typing.Callable[[bool], None]]) -> None: ...
    def lockDevice(self, executor: typing.Union[java.util.concurrent.Executor, typing.Callable], outcomeReceiver: typing.Union[android.os.OutcomeReceiver[None, java.lang.Exception], typing.Callable[[None], None]]) -> None: ...
    def unlockDevice(self, executor: typing.Union[java.util.concurrent.Executor, typing.Callable], outcomeReceiver: typing.Union[android.os.OutcomeReceiver[None, java.lang.Exception], typing.Callable[[None], None]]) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.devicelock")``.

    DeviceId: typing.Type[DeviceId]
    DeviceLockManager: typing.Type[DeviceLockManager]
