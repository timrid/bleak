
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.service.assist.classification
import typing


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.service.assist")``.

    classification: android.service.assist.classification.__module_protocol__
