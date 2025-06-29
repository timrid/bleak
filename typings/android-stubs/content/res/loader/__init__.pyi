
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.content
import android.content.om
import android.content.res
import android.os
import java.io
import java.lang
import java.util
import typing



class AssetsProvider:
    def loadAssetFd(self, string: str, int: int) -> android.content.res.AssetFileDescriptor: ...

class ResourcesLoader:
    def __init__(self): ...
    def addProvider(self, resourcesProvider: 'ResourcesProvider') -> None: ...
    def clearProviders(self) -> None: ...
    def getProviders(self) -> java.util.List['ResourcesProvider']: ...
    def removeProvider(self, resourcesProvider: 'ResourcesProvider') -> None: ...
    def setProviders(self, list: java.util.List['ResourcesProvider']) -> None: ...

class ResourcesProvider(java.lang.AutoCloseable, java.io.Closeable):
    def close(self) -> None: ...
    @staticmethod
    def empty(assetsProvider: AssetsProvider) -> 'ResourcesProvider': ...
    @typing.overload
    @staticmethod
    def loadFromApk(parcelFileDescriptor: android.os.ParcelFileDescriptor) -> 'ResourcesProvider': ...
    @typing.overload
    @staticmethod
    def loadFromApk(parcelFileDescriptor: android.os.ParcelFileDescriptor, assetsProvider: AssetsProvider) -> 'ResourcesProvider': ...
    @staticmethod
    def loadFromDirectory(string: str, assetsProvider: AssetsProvider) -> 'ResourcesProvider': ...
    @staticmethod
    def loadFromSplit(context: android.content.Context, string: str) -> 'ResourcesProvider': ...
    @staticmethod
    def loadFromTable(parcelFileDescriptor: android.os.ParcelFileDescriptor, assetsProvider: AssetsProvider) -> 'ResourcesProvider': ...
    @staticmethod
    def loadOverlay(overlayInfo: android.content.om.OverlayInfo) -> 'ResourcesProvider': ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.content.res.loader")``.

    AssetsProvider: typing.Type[AssetsProvider]
    ResourcesLoader: typing.Type[ResourcesLoader]
    ResourcesProvider: typing.Type[ResourcesProvider]
