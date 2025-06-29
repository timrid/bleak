
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.os
import android.view.autofill
import java.util
import typing



class FieldClassification(android.os.Parcelable):
    CREATOR: typing.ClassVar[android.os.Parcelable.Creator] = ...
    def __init__(self, autofillId: android.view.autofill.AutofillId, set: java.util.Set[str]): ...
    def describeContents(self) -> int: ...
    def getAutofillId(self) -> android.view.autofill.AutofillId: ...
    def getHints(self) -> java.util.Set[str]: ...
    def toString(self) -> str: ...
    def writeToParcel(self, parcel: android.os.Parcel, int: int) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.service.assist.classification")``.

    FieldClassification: typing.Type[FieldClassification]
