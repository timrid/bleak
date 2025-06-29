
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.content
import android.os
import java.lang
import java.util.concurrent
import typing



class AppSetId:
    SCOPE_APP: typing.ClassVar[int] = ...
    SCOPE_DEVELOPER: typing.ClassVar[int] = ...
    def __init__(self, string: str, int: int): ...
    def equals(self, object: typing.Any) -> bool: ...
    def getId(self) -> str: ...
    def getScope(self) -> int: ...
    def hashCode(self) -> int: ...

class AppSetIdManager:
    @staticmethod
    def get(context: android.content.Context) -> 'AppSetIdManager': ...
    def getAppSetId(self, executor: typing.Union[java.util.concurrent.Executor, typing.Callable], outcomeReceiver: typing.Union[android.os.OutcomeReceiver[AppSetId, java.lang.Exception], typing.Callable[[AppSetId], None]]) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.adservices.appsetid")``.

    AppSetId: typing.Type[AppSetId]
    AppSetIdManager: typing.Type[AppSetIdManager]
