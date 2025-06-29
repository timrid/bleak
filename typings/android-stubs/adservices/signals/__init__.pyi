
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.content
import android.net
import android.os
import java.lang
import java.util.concurrent
import typing



class ProtectedSignalsManager:
    @staticmethod
    def get(context: android.content.Context) -> 'ProtectedSignalsManager': ...
    def updateSignals(self, updateSignalsRequest: 'UpdateSignalsRequest', executor: typing.Union[java.util.concurrent.Executor, typing.Callable], outcomeReceiver: typing.Union[android.os.OutcomeReceiver[typing.Any, java.lang.Exception], typing.Callable[[typing.Any], None]]) -> None: ...

class UpdateSignalsRequest:
    def equals(self, object: typing.Any) -> bool: ...
    def getUpdateUri(self) -> android.net.Uri: ...
    def hashCode(self) -> int: ...
    def toString(self) -> str: ...
    class Builder:
        def __init__(self, uri: android.net.Uri): ...
        def build(self) -> 'UpdateSignalsRequest': ...
        def setUpdateUri(self, uri: android.net.Uri) -> 'UpdateSignalsRequest.Builder': ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.adservices.signals")``.

    ProtectedSignalsManager: typing.Type[ProtectedSignalsManager]
    UpdateSignalsRequest: typing.Type[UpdateSignalsRequest]
