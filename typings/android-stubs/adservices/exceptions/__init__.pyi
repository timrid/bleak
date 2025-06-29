
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.lang
import typing



class AdServicesException(java.lang.Exception):
    @typing.overload
    def __init__(self, string: str): ...
    @typing.overload
    def __init__(self, string: str, throwable: java.lang.Throwable): ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.adservices.exceptions")``.

    AdServicesException: typing.Type[AdServicesException]
