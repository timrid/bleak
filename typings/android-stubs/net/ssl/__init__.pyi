
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import javax.net.ssl
import jpype
import typing



class SSLEngines:
    @staticmethod
    def exportKeyingMaterial(sSLEngine: javax.net.ssl.SSLEngine, string: str, byteArray: typing.Union[typing.List[int], jpype.JArray, bytes], int: int) -> typing.MutableSequence[int]: ...
    @staticmethod
    def isSupportedEngine(sSLEngine: javax.net.ssl.SSLEngine) -> bool: ...
    @staticmethod
    def setUseSessionTickets(sSLEngine: javax.net.ssl.SSLEngine, boolean: bool) -> None: ...

class SSLSockets:
    @staticmethod
    def exportKeyingMaterial(sSLSocket: javax.net.ssl.SSLSocket, string: str, byteArray: typing.Union[typing.List[int], jpype.JArray, bytes], int: int) -> typing.MutableSequence[int]: ...
    @staticmethod
    def isSupportedSocket(sSLSocket: javax.net.ssl.SSLSocket) -> bool: ...
    @staticmethod
    def setUseSessionTickets(sSLSocket: javax.net.ssl.SSLSocket, boolean: bool) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.net.ssl")``.

    SSLEngines: typing.Type[SSLEngines]
    SSLSockets: typing.Type[SSLSockets]
