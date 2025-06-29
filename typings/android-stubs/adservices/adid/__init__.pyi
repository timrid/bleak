
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.adservices.common
import android.content
import android.os
import java.lang
import java.util.concurrent
import typing



class AdId:
    ZERO_OUT: typing.ClassVar[str] = ...
    def __init__(self, string: str, boolean: bool): ...
    def equals(self, object: typing.Any) -> bool: ...
    def getAdId(self) -> str: ...
    def hashCode(self) -> int: ...
    def isLimitAdTrackingEnabled(self) -> bool: ...
    def toString(self) -> str: ...

class AdIdManager:
    @staticmethod
    def get(context: android.content.Context) -> 'AdIdManager': ...
    @typing.overload
    def getAdId(self, executor: typing.Union[java.util.concurrent.Executor, typing.Callable], adServicesOutcomeReceiver: typing.Union[android.adservices.common.AdServicesOutcomeReceiver[AdId, java.lang.Exception], typing.Callable[[AdId], None]]) -> None: ...
    @typing.overload
    def getAdId(self, executor: typing.Union[java.util.concurrent.Executor, typing.Callable], outcomeReceiver: typing.Union[android.os.OutcomeReceiver[AdId, java.lang.Exception], typing.Callable[[AdId], None]]) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.adservices.adid")``.

    AdId: typing.Type[AdId]
    AdIdManager: typing.Type[AdIdManager]
