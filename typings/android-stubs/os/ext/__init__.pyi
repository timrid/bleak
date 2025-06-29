
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.util
import typing



class SdkExtensions:
    AD_SERVICES: typing.ClassVar[int] = ...
    @staticmethod
    def getAllExtensionVersions() -> java.util.Map[int, int]: ...
    @staticmethod
    def getExtensionVersion(int: int) -> int: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.os.ext")``.

    SdkExtensions: typing.Type[SdkExtensions]
