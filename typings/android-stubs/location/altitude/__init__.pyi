
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.content
import android.location
import typing



class AltitudeConverter:
    def __init__(self): ...
    def addMslAltitudeToLocation(self, context: android.content.Context, location: android.location.Location) -> None: ...
    def tryAddMslAltitudeToLocation(self, location: android.location.Location) -> bool: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.location.altitude")``.

    AltitudeConverter: typing.Type[AltitudeConverter]
