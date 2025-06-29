
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.app.appsearch
import typing



class DocumentIdUtil:
    @typing.overload
    @staticmethod
    def createQualifiedId(string: str, string2: str, genericDocument: android.app.appsearch.GenericDocument) -> str: ...
    @typing.overload
    @staticmethod
    def createQualifiedId(string: str, string2: str, string3: str, string4: str) -> str: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.app.appsearch.util")``.

    DocumentIdUtil: typing.Type[DocumentIdUtil]
