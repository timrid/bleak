
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.net.wifi.hotspot2
import typing



class PpsMoParser:
    @staticmethod
    def parseMoText(string: str) -> android.net.wifi.hotspot2.PasspointConfiguration: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.net.wifi.hotspot2.omadm")``.

    PpsMoParser: typing.Type[PpsMoParser]
