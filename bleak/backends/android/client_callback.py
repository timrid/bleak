import dataclasses

from bleak.backends.android.dispatcher import (
    CallbackApi,
    CallbackResult,
    EmptyCallbackResult,
)


@dataclasses.dataclass
class OnConnectionStateChangeResult(CallbackResult):
    new_state: int


@dataclasses.dataclass(frozen=True)
class OnConnectionStateChangeCallback(CallbackApi[OnConnectionStateChangeResult]):
    pass


@dataclasses.dataclass
class OnMtuChangedResult(CallbackResult):
    mtu: int


@dataclasses.dataclass(frozen=True)
class OnMtuChangedCallback(CallbackApi[OnMtuChangedResult]):
    pass


@dataclasses.dataclass(frozen=True)
class OnServicesDiscoveredCallback(CallbackApi[EmptyCallbackResult]):
    pass


@dataclasses.dataclass
class OnCharacteristicReadResult(CallbackResult):
    value: bytes


@dataclasses.dataclass(frozen=True)
class OnCharacteristicReadCallback(CallbackApi[OnCharacteristicReadResult]):
    handle: int


@dataclasses.dataclass(frozen=True)
class OnCharacteristicWriteCallback(CallbackApi[EmptyCallbackResult]):
    handle: int


@dataclasses.dataclass
class OnDescriptorReadResult(CallbackResult):
    value: bytes


@dataclasses.dataclass(frozen=True)
class OnDescriptorReadCallback(CallbackApi[OnDescriptorReadResult]):
    uuid: str


@dataclasses.dataclass(frozen=True)
class OnDescriptorWriteCallback(CallbackApi[EmptyCallbackResult]):
    uuid: str
