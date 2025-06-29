
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import typing



class ImsRegistrationImplBase:
    REGISTRATION_TECH_3G: typing.ClassVar[int] = ...
    REGISTRATION_TECH_CROSS_SIM: typing.ClassVar[int] = ...
    REGISTRATION_TECH_IWLAN: typing.ClassVar[int] = ...
    REGISTRATION_TECH_LTE: typing.ClassVar[int] = ...
    REGISTRATION_TECH_NONE: typing.ClassVar[int] = ...
    REGISTRATION_TECH_NR: typing.ClassVar[int] = ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.telephony.ims.stub")``.

    ImsRegistrationImplBase: typing.Type[ImsRegistrationImplBase]
