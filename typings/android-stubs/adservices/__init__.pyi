
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.adservices.adid
import android.adservices.adselection
import android.adservices.appsetid
import android.adservices.common
import android.adservices.customaudience
import android.adservices.exceptions
import android.adservices.measurement
import android.adservices.ondevicepersonalization
import android.adservices.signals
import android.adservices.topics
import typing



class AdServicesState:
    @staticmethod
    def isAdServicesStateEnabled() -> bool: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.adservices")``.

    AdServicesState: typing.Type[AdServicesState]
    adid: android.adservices.adid.__module_protocol__
    adselection: android.adservices.adselection.__module_protocol__
    appsetid: android.adservices.appsetid.__module_protocol__
    common: android.adservices.common.__module_protocol__
    customaudience: android.adservices.customaudience.__module_protocol__
    exceptions: android.adservices.exceptions.__module_protocol__
    measurement: android.adservices.measurement.__module_protocol__
    ondevicepersonalization: android.adservices.ondevicepersonalization.__module_protocol__
    signals: android.adservices.signals.__module_protocol__
    topics: android.adservices.topics.__module_protocol__
