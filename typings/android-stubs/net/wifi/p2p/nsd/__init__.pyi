
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import android.os
import java.util
import typing



class WifiP2pServiceInfo(android.os.Parcelable):
    SERVICE_TYPE_ALL: typing.ClassVar[int] = ...
    SERVICE_TYPE_BONJOUR: typing.ClassVar[int] = ...
    SERVICE_TYPE_UPNP: typing.ClassVar[int] = ...
    SERVICE_TYPE_VENDOR_SPECIFIC: typing.ClassVar[int] = ...
    def describeContents(self) -> int: ...
    def equals(self, object: typing.Any) -> bool: ...
    def hashCode(self) -> int: ...
    def writeToParcel(self, parcel: android.os.Parcel, int: int) -> None: ...

class WifiP2pServiceRequest(android.os.Parcelable):
    def describeContents(self) -> int: ...
    def equals(self, object: typing.Any) -> bool: ...
    def hashCode(self) -> int: ...
    @typing.overload
    @staticmethod
    def newInstance(int: int) -> 'WifiP2pServiceRequest': ...
    @typing.overload
    @staticmethod
    def newInstance(int: int, string: str) -> 'WifiP2pServiceRequest': ...
    def writeToParcel(self, parcel: android.os.Parcel, int: int) -> None: ...

class WifiP2pDnsSdServiceInfo(WifiP2pServiceInfo):
    @staticmethod
    def newInstance(string: str, string2: str, map: typing.Union[java.util.Map[str, str], typing.Mapping[str, str]]) -> 'WifiP2pDnsSdServiceInfo': ...

class WifiP2pDnsSdServiceRequest(WifiP2pServiceRequest):
    @typing.overload
    @staticmethod
    def newInstance() -> 'WifiP2pDnsSdServiceRequest': ...
    @typing.overload
    @staticmethod
    def newInstance(string: str) -> 'WifiP2pDnsSdServiceRequest': ...
    @typing.overload
    @staticmethod
    def newInstance(string: str, string2: str) -> 'WifiP2pDnsSdServiceRequest': ...
    @typing.overload
    @staticmethod
    def newInstance(int: int) -> WifiP2pServiceRequest: ...
    @typing.overload
    @staticmethod
    def newInstance(int: int, string: str) -> WifiP2pServiceRequest: ...

class WifiP2pUpnpServiceInfo(WifiP2pServiceInfo):
    @staticmethod
    def newInstance(string: str, string2: str, list: java.util.List[str]) -> 'WifiP2pUpnpServiceInfo': ...

class WifiP2pUpnpServiceRequest(WifiP2pServiceRequest):
    @typing.overload
    @staticmethod
    def newInstance(int: int) -> WifiP2pServiceRequest: ...
    @typing.overload
    @staticmethod
    def newInstance(int: int, string: str) -> WifiP2pServiceRequest: ...
    @typing.overload
    @staticmethod
    def newInstance() -> 'WifiP2pUpnpServiceRequest': ...
    @typing.overload
    @staticmethod
    def newInstance(string: str) -> 'WifiP2pUpnpServiceRequest': ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("android.net.wifi.p2p.nsd")``.

    WifiP2pDnsSdServiceInfo: typing.Type[WifiP2pDnsSdServiceInfo]
    WifiP2pDnsSdServiceRequest: typing.Type[WifiP2pDnsSdServiceRequest]
    WifiP2pServiceInfo: typing.Type[WifiP2pServiceInfo]
    WifiP2pServiceRequest: typing.Type[WifiP2pServiceRequest]
    WifiP2pUpnpServiceInfo: typing.Type[WifiP2pUpnpServiceInfo]
    WifiP2pUpnpServiceRequest: typing.Type[WifiP2pUpnpServiceRequest]
