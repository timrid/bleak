import asyncio

from jnius import PythonJavaClass, java_method  # type: ignore

from bleak.backends.android.client import BleakClientAndroid
from bleak.backends.android.client_callback import (
    OnCharacteristicReadCallback,
    OnCharacteristicReadResult,
    OnCharacteristicWriteCallback,
    OnConnectionStateChangeCallback,
    OnConnectionStateChangeResult,
    OnDescriptorReadCallback,
    OnDescriptorReadResult,
    OnDescriptorWriteCallback,
    OnMtuChangedCallback,
    OnMtuChangedResult,
    OnServicesDiscoveredCallback,
)
from bleak.backends.android.dispatcher import (
    CallbackDispatcher,
    EmptyCallbackResult,
)
from bleak.backends.android.framework.p4android.defs import (
    BluetoothProfile,
    PythonBluetoothGattCallback,
)
from bleak.backends.android.status import gatt_status_to_string
from bleak.exc import BleakError


class _PythonBluetoothGattCallback(PythonJavaClass):
    __javacontext__ = "app"
    __javainterfaces__ = [
        "com.github.hbldh.bleak.PythonBluetoothGattCallback$Interface"
    ]

    def __init__(self, client: BleakClientAndroid, loop: asyncio.AbstractEventLoop):
        super().__init__(loop)
        self._loop = loop
        self._client = client
        self.java = PythonBluetoothGattCallback(self)
        self.dispatcher = CallbackDispatcher(loop)

    @java_method("(II)V")
    def onConnectionStateChange(self, status, new_state):
        try:
            self.dispatcher.result_state_threadsafe(
                gatt_status_to_string(status),
                OnConnectionStateChangeCallback(),
                OnConnectionStateChangeResult(new_state),
            )
        except BleakError:
            pass
        if (
            new_state == BluetoothProfile.STATE_DISCONNECTED
            and self._client._disconnected_callback is not None
        ):
            self._client._disconnected_callback()

    @java_method("(II)V")
    def onMtuChanged(self, mtu, status):
        self.dispatcher.result_state_threadsafe(
            gatt_status_to_string(status),
            OnMtuChangedCallback(),
            OnMtuChangedResult(mtu),
        )

    @java_method("(I)V")
    def onServicesDiscovered(self, status):
        self.dispatcher.result_state_threadsafe(
            gatt_status_to_string(status),
            OnServicesDiscoveredCallback(),
            EmptyCallbackResult(),
        )

    @java_method("(I[B)V")
    def onCharacteristicChanged(self, handle, value):
        self._loop.call_soon_threadsafe(
            self._client._subscriptions[handle], bytearray(value.tolist())
        )

    @java_method("(II[B)V")
    def onCharacteristicRead(self, handle, status, value):
        self.dispatcher.result_state_threadsafe(
            gatt_status_to_string(status),
            OnCharacteristicReadCallback(handle),
            OnCharacteristicReadResult(bytes(value.tolist())),
        )

    @java_method("(II)V")
    def onCharacteristicWrite(self, handle, status):
        self.dispatcher.result_state_threadsafe(
            gatt_status_to_string(status),
            OnCharacteristicWriteCallback(handle),
            EmptyCallbackResult(),
        )

    @java_method("(Ljava/lang/String;I[B)V")
    def onDescriptorRead(self, uuid, status, value):
        self.dispatcher.result_state_threadsafe(
            gatt_status_to_string(status),
            OnDescriptorReadCallback(uuid),
            OnDescriptorReadResult(bytes(value.tolist())),
        )

    @java_method("(Ljava/lang/String;I)V")
    def onDescriptorWrite(self, uuid, status):
        self.dispatcher.result_state_threadsafe(
            gatt_status_to_string(status),
            OnDescriptorWriteCallback(uuid),
            EmptyCallbackResult(),
        )
