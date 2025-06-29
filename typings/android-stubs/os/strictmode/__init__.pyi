
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.content
import java.lang
import jpype
import typing



class Violation(java.lang.Throwable):
    def fillInStackTrace(self) -> java.lang.Throwable: ...
    def hashCode(self) -> int: ...
    def initCause(self, throwable: java.lang.Throwable) -> java.lang.Throwable: ...
    def setStackTrace(self, stackTraceElementArray: typing.Union[typing.List[java.lang.StackTraceElement], jpype.JArray]) -> None: ...

class CleartextNetworkViolation(Violation): ...

class ContentUriWithoutPermissionViolation(Violation): ...

class CredentialProtectedWhileLockedViolation(Violation): ...

class CustomViolation(Violation): ...

class DiskReadViolation(Violation): ...

class DiskWriteViolation(Violation): ...

class ExplicitGcViolation(Violation): ...

class FileUriExposedViolation(Violation): ...

class ImplicitDirectBootViolation(Violation): ...

class IncorrectContextUseViolation(Violation):
    def __init__(self, string: str, throwable: java.lang.Throwable): ...

class InstanceCountViolation(Violation):
    def getNumberOfInstances(self) -> int: ...

class IntentReceiverLeakedViolation(Violation): ...

class LeakedClosableViolation(Violation): ...

class NetworkViolation(Violation): ...

class NonSdkApiUsedViolation(Violation): ...

class ResourceMismatchViolation(Violation): ...

class ServiceConnectionLeakedViolation(Violation): ...

class SqliteObjectLeakedViolation(Violation): ...

class UnbufferedIoViolation(Violation): ...

class UnsafeIntentLaunchViolation(Violation):
    def __init__(self, intent: android.content.Intent): ...
    def getIntent(self) -> android.content.Intent: ...

class UntaggedSocketViolation(Violation): ...

class WebViewMethodCalledOnWrongThreadViolation(Violation): ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.os.strictmode")``.

    CleartextNetworkViolation: typing.Type[CleartextNetworkViolation]
    ContentUriWithoutPermissionViolation: typing.Type[ContentUriWithoutPermissionViolation]
    CredentialProtectedWhileLockedViolation: typing.Type[CredentialProtectedWhileLockedViolation]
    CustomViolation: typing.Type[CustomViolation]
    DiskReadViolation: typing.Type[DiskReadViolation]
    DiskWriteViolation: typing.Type[DiskWriteViolation]
    ExplicitGcViolation: typing.Type[ExplicitGcViolation]
    FileUriExposedViolation: typing.Type[FileUriExposedViolation]
    ImplicitDirectBootViolation: typing.Type[ImplicitDirectBootViolation]
    IncorrectContextUseViolation: typing.Type[IncorrectContextUseViolation]
    InstanceCountViolation: typing.Type[InstanceCountViolation]
    IntentReceiverLeakedViolation: typing.Type[IntentReceiverLeakedViolation]
    LeakedClosableViolation: typing.Type[LeakedClosableViolation]
    NetworkViolation: typing.Type[NetworkViolation]
    NonSdkApiUsedViolation: typing.Type[NonSdkApiUsedViolation]
    ResourceMismatchViolation: typing.Type[ResourceMismatchViolation]
    ServiceConnectionLeakedViolation: typing.Type[ServiceConnectionLeakedViolation]
    SqliteObjectLeakedViolation: typing.Type[SqliteObjectLeakedViolation]
    UnbufferedIoViolation: typing.Type[UnbufferedIoViolation]
    UnsafeIntentLaunchViolation: typing.Type[UnsafeIntentLaunchViolation]
    UntaggedSocketViolation: typing.Type[UntaggedSocketViolation]
    Violation: typing.Type[Violation]
    WebViewMethodCalledOnWrongThreadViolation: typing.Type[WebViewMethodCalledOnWrongThreadViolation]
