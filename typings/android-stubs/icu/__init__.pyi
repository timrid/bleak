
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.icu.lang
import android.icu.math
import android.icu.number
import android.icu.text
import android.icu.util
import typing


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.icu")``.

    lang: android.icu.lang.__module_protocol__
    math: android.icu.math.__module_protocol__
    number: android.icu.number.__module_protocol__
    text: android.icu.text.__module_protocol__
    util: android.icu.util.__module_protocol__
