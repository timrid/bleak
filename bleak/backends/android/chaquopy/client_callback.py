import asyncio

from android.bluetooth import (
    BluetoothGatt,
    BluetoothGattCallback,
    BluetoothGattCharacteristic,
    BluetoothGattDescriptor,
    BluetoothProfile,
)
from java import Override, jarray, jbyte, jint, jvoid, static_proxy

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
from bleak.backends.android.dispatcher import CallbackDispatcher, EmptyCallbackResult
from bleak.backends.android.status import gatt_status_to_string
from bleak.exc import BleakError


class _PythonBluetoothGattCallback(static_proxy(BluetoothGattCallback)):
    """Callback class for GattClient. PRIVATE."""

    def __init__(self, client: BleakClientAndroid, loop: asyncio.AbstractEventLoop):
        super(_PythonBluetoothGattCallback, self).__init__()
        self.java = self
        self._loop = loop
        self._client = client
        self.dispatcher = CallbackDispatcher(loop)

    @Override(jvoid, [BluetoothGatt, jint, jint])
    def onConnectionStateChange(
        self, gatt: BluetoothGatt, status: jint, newState: jint
    ):
        try:
            self.dispatcher.result_state_threadsafe(
                gatt_status_to_string(int(status)),
                OnConnectionStateChangeCallback(),
                OnConnectionStateChangeResult(int(newState)),
            )
        except BleakError:
            pass
        if (
            newState == BluetoothProfile.STATE_DISCONNECTED
            and self._client._disconnected_callback is not None
        ):
            self._client._disconnected_callback()

    @Override(jvoid, [BluetoothGatt, jint, jint])
    def onMtuChanged(self, gatt: BluetoothGatt, mtu: jint, status: jint):
        self.dispatcher.result_state_threadsafe(
            gatt_status_to_string(int(status)),
            OnMtuChangedCallback(),
            OnMtuChangedResult(int(mtu)),
        )

    @Override(jvoid, [BluetoothGatt, jint])
    def onServicesDiscovered(self, gatt: BluetoothGatt, status: jint):
        self.dispatcher.result_state_threadsafe(
            gatt_status_to_string(int(status)),
            OnServicesDiscoveredCallback(),
            EmptyCallbackResult(),
        )

    @Override(
        jvoid,
        [BluetoothGatt, BluetoothGattCharacteristic, jarray(jbyte)],
    )
    @Override(jvoid, [BluetoothGatt, BluetoothGattCharacteristic])
    def onCharacteristicChanged(
        self, gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic, *args
    ):
        handle = characteristic.getInstanceId()
        if len(args) == 0:
            value = characteristic.getValue()
        else:
            value = args[0]
        self._loop.call_soon_threadsafe(
            self._client._subscriptions[handle], bytearray(value)
        )

    @Override(
        jvoid,
        [BluetoothGatt, BluetoothGattCharacteristic, jarray(jbyte), jint],
    )
    @Override(jvoid, [BluetoothGatt, BluetoothGattCharacteristic, jint])
    def onCharacteristicRead(
        self, gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic, *args
    ):
        handle = characteristic.getInstanceId()
        status = args[-1]
        # Android 12 and below:
        if len(args) == 1:
            value = characteristic.getValue()
        else:
            value = args[0]
        self.dispatcher.result_state_threadsafe(
            gatt_status_to_string(int(status)),
            OnCharacteristicReadCallback(handle),
            OnCharacteristicReadResult(bytes(value)),
        )

    @Override(jvoid, [BluetoothGatt, BluetoothGattCharacteristic, jint])
    def onCharacteristicWrite(
        self,
        gatt: BluetoothGatt,
        characteristic: BluetoothGattCharacteristic,
        status: jint,
    ):
        handle = characteristic.getInstanceId()
        self.dispatcher.result_state_threadsafe(
            gatt_status_to_string(int(status)),
            OnCharacteristicWriteCallback(handle),
            EmptyCallbackResult(),
        )

    @Override(
        jvoid,
        [BluetoothGatt, BluetoothGattDescriptor, jint, jarray(jbyte)],
    )
    @Override(jvoid, [BluetoothGatt, BluetoothGattDescriptor, jint])
    def onDescriptorRead(
        self,
        gatt: BluetoothGatt,
        descriptor: BluetoothGattDescriptor,
        status: jint,
        *args,
    ):
        uuid = descriptor.getUuid().toString()
        value = descriptor.getValue()
        self.dispatcher.result_state_threadsafe(
            gatt_status_to_string(int(status)),
            OnDescriptorReadCallback(uuid),
            OnDescriptorReadResult(bytes(value)),
        )

    @Override(jvoid, [BluetoothGatt, BluetoothGattDescriptor, jint])
    def onDescriptorWrite(
        self,
        gatt: BluetoothGatt,
        descriptor: BluetoothGattDescriptor,
        status: jint,
    ):
        uuid = descriptor.getUuid().toString()
        self.dispatcher.result_state_threadsafe(
            gatt_status_to_string(int(status)),
            OnDescriptorWriteCallback(uuid),
            EmptyCallbackResult(),
        )
