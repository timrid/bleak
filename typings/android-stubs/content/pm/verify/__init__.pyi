
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.content.pm.verify.domain
import typing


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.content.pm.verify")``.

    domain: android.content.pm.verify.domain.__module_protocol__
