
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.app.appsearch
import java.lang
import typing



class AppSearchException(java.lang.Exception):
    @typing.overload
    def __init__(self, int: int): ...
    @typing.overload
    def __init__(self, int: int, string: str): ...
    @typing.overload
    def __init__(self, int: int, string: str, throwable: java.lang.Throwable): ...
    def getResultCode(self) -> int: ...
    _toAppSearchResult__T = typing.TypeVar('_toAppSearchResult__T')  # <T>
    def toAppSearchResult(self) -> android.app.appsearch.AppSearchResult[_toAppSearchResult__T]: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.app.appsearch.exceptions")``.

    AppSearchException: typing.Type[AppSearchException]
