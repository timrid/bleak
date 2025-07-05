import asyncio
import dataclasses
import functools
import inspect
import logging
import uuid
from typing import Any, MutableSequence, Optional, Union, cast, override

from android.bluetooth import (
    BluetoothAdapter,
    BluetoothDevice,
    BluetoothGatt,
    BluetoothGattCallback,
    BluetoothGattCharacteristic,
    BluetoothGattDescriptor,
    BluetoothGattService,
    BluetoothProfile,
)
from android.os import Build
from java import Override, jarray, jbyte, jint, jvoid, static_proxy
from java.util import UUID
from org.beeware.android import MainActivity
from typing_extensions import Buffer

from bleak.backends.chaquopy import (
    BLEGattService,
)
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.client import BaseBleakClient, NotifyCallback
from bleak.backends.descriptor import BleakGATTDescriptor
from bleak.backends.device import BLEDevice
from bleak.backends.service import BleakGATTServiceCollection
from bleak.exc import BleakCharacteristicNotFoundError, BleakError

logger = logging.getLogger(__name__)

async_callbacks = set()

# Client Characteristic Configuration Descriptor
CCCD = "00002902-0000-1000-8000-00805f9b34fb"


@dataclasses.dataclass
class OnConnectionStateChangeData:
    status: jint


@dataclasses.dataclass
class OnMtuChangedData:
    status: jint
    mtu: jint


@dataclasses.dataclass
class OnServicesDiscoveredData:
    status: jint
    services: MutableSequence[BluetoothGattService]


@dataclasses.dataclass
class OnCharacteristicReadData:
    status: jint
    handle: int
    value: MutableSequence[int]


@dataclasses.dataclass
class OnCharacteristicWriteData:
    status: jint
    handle: int


@dataclasses.dataclass
class OnDescriptorReadData:
    status: jint
    uuid: str
    value: MutableSequence[int]


@dataclasses.dataclass
class OnDescriptorWriteData:
    status: jint
    uuid: str


class _PythonGattCallback(static_proxy(BluetoothGattCallback)):
    """Callback class for GattClient. PRIVATE."""

    def __init__(self, client: "BleakClientChaquopy"):
        super(_PythonGattCallback, self).__init__()
        self.client = client
        self.onConnectionStateChangeToConnectedQueue: asyncio.Queue[
            OnConnectionStateChangeData
        ] = asyncio.Queue()
        self.onConnectionStateChangeToDisconnectedQueue: asyncio.Queue[
            OnConnectionStateChangeData
        ] = asyncio.Queue()
        self.onMtuChangedQueue: asyncio.Queue[OnMtuChangedData] = asyncio.Queue()

        self.onServicesDiscoveredQueue: asyncio.Queue[OnServicesDiscoveredData] = (
            asyncio.Queue()
        )

        self.onCharacteristicReadQueue: asyncio.Queue[OnCharacteristicReadData] = (
            asyncio.Queue()
        )
        self.onCharacteristicWriteQueue: asyncio.Queue[OnCharacteristicWriteData] = (
            asyncio.Queue()
        )

        self.onDescriptorReadQueue: asyncio.Queue[OnDescriptorReadData] = (
            asyncio.Queue()
        )
        self.onDescriptorWriteQueue: asyncio.Queue[OnDescriptorWriteData] = (
            asyncio.Queue()
        )

    @Override(jvoid, [BluetoothGatt, jint, jint])
    def onConnectionStateChange(
        self, gatt: BluetoothGatt, status: jint, newState: jint
    ):
        """Register connect or disconnect events.

        This is the callback function for Android's 'device.ConnectGatt'.
        """
        if newState == BluetoothProfile.STATE_CONNECTED:
            self.onConnectionStateChangeToConnectedQueue.put_nowait(
                OnConnectionStateChangeData(status)
            )

        elif newState == BluetoothProfile.STATE_DISCONNECTED:
            self.onConnectionStateChangeToDisconnectedQueue.put_nowait(
                OnConnectionStateChangeData(status)
            )
            if self.client._disconnected_callback:
                self.client._disconnected_callback()

    @Override(jvoid, [BluetoothGatt, jint, jint])
    def onMtuChanged(self, gatt: BluetoothGatt, mtu: jint, status: jint):
        """Handle change in MTU size.

        This is the callback function for changes in MTU.
        """
        self.onMtuChangedQueue.put_nowait(OnMtuChangedData(mtu, status))

        # if status == BluetoothGatt.GATT_SUCCESS:
        #     self.client._mtu = int(mtu)

    @Override(jvoid, [BluetoothGatt, jint])
    def onServicesDiscovered(self, gatt: BluetoothGatt, status: jint):
        """Write services to list.

        This is the callback function for Android's 'gatt.discoverServices'.
        """
        # getServices returns an ArrayList, must be converted to Array to work
        # with Python
        services = gatt.getServices().toArray()
        self.onServicesDiscoveredQueue.put_nowait(
            OnServicesDiscoveredData(status, services)
        )

    @Override(jvoid, [BluetoothGatt, BluetoothGattCharacteristic, jarray(jbyte)])
    def onCharacteristicChanged(
        self,
        gatt: BluetoothGatt,
        characteristic: BluetoothGattCharacteristic,
        value: jarray,
    ):
        """Read the notification.

        This is the callback function for notifying services.
        """
        handle = characteristic.getInstanceId()
        asyncio.get_running_loop().call_soon_threadsafe(
            self.client._subscriptions[handle],
            bytearray(characteristic.getValue()),
        )

    @Override(
        jvoid,
        [BluetoothGatt, BluetoothGattCharacteristic, jarray(jbyte), jint],
    )
    @Override(jvoid, [BluetoothGatt, BluetoothGattCharacteristic, jint])
    def onCharacteristicRead(
        self, gatt: BluetoothGatt, characteristic: BluetoothGattCharacteristic, *args
    ):
        """Put characteristic's read value to a data list.

        This is the callback function for Android's 'gatt.readCharacteristic'.

        Covers the deprecated version (API level < 33 / Android 12 and older)
        and the actual version (API level 33 upwards  / Android 13 and newer).
        """
        handle = characteristic.getInstanceId()
        status = args[-1]
        # Android 12 and below:
        if len(args) == 1:
            value = characteristic.getValue()
        else:
            value = args[0]
        self.onCharacteristicReadQueue.put_nowait(
            OnCharacteristicReadData(status, handle, value)
        )

    @Override(jvoid, [BluetoothGatt, BluetoothGattCharacteristic, jint])
    def onCharacteristicWrite(
        self,
        gatt: BluetoothGatt,
        characteristic: BluetoothGattCharacteristic,
        status: jint,
    ):
        handle = characteristic.getInstanceId()
        self.onCharacteristicWriteQueue.put_nowait(
            OnCharacteristicWriteData(status, handle)
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
        self.onDescriptorReadQueue.put_nowait(OnDescriptorReadData(status, uuid, value))

    @Override(jvoid, [BluetoothGatt, BluetoothGattDescriptor, jint])
    def onDescriptorWrite(
        self,
        gatt: BluetoothGatt,
        descriptor: BluetoothGattDescriptor,
        status: jint,
    ):
        uuid = descriptor.getUuid().toString()
        self.onDescriptorWriteQueue.put_nowait(OnDescriptorWriteData(status, uuid))


class BleakClientChaquopy(BaseBleakClient):
    """Class to connect to a Bluetooth LE GATT server and communicate."""

    client = None

    def __init__(
        self,
        address_or_ble_device: Union[BLEDevice, str],
        services: Optional[set[str]] = None,
        **kwargs: Any,
    ):
        super(BleakClientChaquopy, self).__init__(address_or_ble_device, **kwargs)

        self.activity = self.context = MainActivity.singletonThis

        self._requested_services = (
            [uuid.UUID(s) for s in services] if services else None
        )  # TODO: This must be used somewhere...
        self._device: BluetoothDevice | None = None
        self._adapter: BluetoothAdapter | None = None
        self._gatt: BluetoothGatt | None = None
        self._gatt_callback: _PythonGattCallback | None = None
        self._subscriptions: dict[int, NotifyCallback] = {}
        self._mtu: int = 23

    async def connect(self, pair: bool, **kwargs: Any) -> None:
        """Connect to a GATT server."""
        if pair:
            logger.warning("Pairing during connect is not implemented on Android")

        self._adapter = BluetoothAdapter.getDefaultAdapter()
        if self._adapter is None:
            raise BleakError("Bluetooth is not supported on this hardware platform")
        if self._adapter.getState() != BluetoothAdapter.STATE_ON:
            raise BleakError("Bluetooth is not turned on")

        self._device = BluetoothAdapter.getDefaultAdapter().getRemoteDevice(
            self.address
        )

        try:
            # Create a GATT connection
            self._gatt_callback = _PythonGattCallback(self)
            self._gatt = self._device.connectGatt(
                self.activity, False, self._gatt_callback
            )
            data = (
                await self._gatt_callback.onConnectionStateChangeToConnectedQueue.get()
            )
            if data.status != BluetoothGatt.GATT_SUCCESS:
                raise BleakError(
                    f"Failed to connect to {self.address}. (Status: {data.status})"
                )

            # Discover services
            self._gatt.discoverServices()
            data = await self._gatt_callback.onServicesDiscoveredQueue.get()
            if data.status != BluetoothGatt.GATT_SUCCESS:
                raise BleakError(
                    f"Failed to discover services for {self.address}. (Status: {data.status})"
                )
            self.services = await self._get_services()

            # Unlike other backends, Android doesn't automatically negotiate
            # the MTU, so we request the largest size possible
            self._gatt.requestMtu(517)
            data = await self._gatt_callback.onMtuChangedQueue.get()
            if data.status != BluetoothGatt.GATT_SUCCESS:
                raise BleakError(
                    f"Failed to change MTU for {self.address}. (Status: {data.status})"
                )
            self._mtu = int(data.mtu)

        except BaseException:
            # if connecting is canceled or one of the above fails, we need to
            # disconnect
            try:
                await self.disconnect()
            except Exception:
                pass
            raise

    async def disconnect(self) -> None:
        """Disconnect from connected GATT server."""
        if self._gatt is None:
            return
        assert self._gatt_callback

        try:
            # Disconnect from the GATT server
            self._gatt.disconnect()
            data = await self._gatt_callback.onConnectionStateChangeToDisconnectedQueue.get()
            if data.status != BluetoothGatt.GATT_SUCCESS:
                raise BleakError(
                    f"Failed to disconnect from {self.address}. (Status: {data.status})"
                )

            # Close the GATT connection
            self._gatt.close()
        except Exception as e:
            logger.error(f"Attempt to disconnect device failed: {e}")

        self._gatt = None
        self._gatt_callback = None

        # Reset all stored services.
        self.services = None

    @override
    async def write_gatt_descriptor(
        self, descriptor: BleakGATTDescriptor, data: Buffer
    ) -> None:
        """Perform a write operation on the specified GATT descriptor.

        Args:
            desc_specifier (BleakGATTDescriptor, str or UUID): The descriptor to write
                to, specified by either UUID or directly by the
                BleakGATTDescriptor object representing it.
            data (bytes or bytearray): The data to send.

        """
        if not self.is_connected:
            raise BleakError("Client not connected")
        assert self._gatt

        assert isinstance(descriptor.obj, BluetoothGattDescriptor)
        descriptor.obj.setValue(data)

        self._gatt.writeDescriptor(descriptor.obj)
        data = await self._gatt_callback.onDescriptorWriteQueue.get()

        await self.__callbacks.perform_and_wait(
            dispatchApi=self.__gatt.writeDescriptor,
            dispatchParams=(descriptor.obj,),
            resultApi=("onDescriptorWrite", descriptor.uuid),
        )

        logger.debug(
            f"Write Descriptor {descriptor.uuid} | {descriptor.handle}: {data}"
        )

    async def start_notify(
        self,
        characteristic: BleakGATTCharacteristic,
        callback: NotifyCallback,
        **kwargs,
    ):
        """Start notification of a notifying characteristic.

        ``uuid`` (characteristic specifier) must be an UUID as string
        ``callback`` can be a usual or async callback method
        """
        if not self.is_connected:
            raise BleakError("Client not connected")
        assert self._gatt

        self.notification_callback = callback
        characteristic = self._find_characteristic(uuid)
        if characteristic:
            self._gatt.setCharacteristicNotification(characteristic, True)
            descriptor = characteristic.getDescriptor(UUID.fromString(CCCD))
            descriptor.setValue(BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE)
            self._gatt.writeDescriptor(descriptor)

            # Send received data to callback function
            while self.notification_callback:
                if received_data:
                    data = received_data.pop()
                    if inspect.iscoroutinefunction(callback):
                        task = asyncio.create_task(
                            callback(characteristic, bytearray(data))
                        )
                        # Make 'hard' reference to avoid GCing of the task
                        async_callbacks.add(task)
                        task.add_done_callback(async_callbacks.discard)
                    else:
                        callback(characteristic, bytearray(data))
                await asyncio.sleep(0.1)

    async def stop_notify(self, characteristic: BleakGATTCharacteristic):
        """Stop notification of a notifying characteristic."""
        if not self.is_connected:
            raise BleakError("Client not connected")
        assert self._gatt

        await self.write_gatt_descriptor(
            characteristic.notification_descriptor,
            BluetoothGattDescriptor.DISABLE_NOTIFICATION_VALUE,
        )

        if not self._gatt.setCharacteristicNotification(characteristic.obj, False):
            raise BleakError(
                f"Failed to disable notification for characteristic {characteristic.uuid}"
            )
        del self._subscriptions[characteristic.handle]

        # characteristic = self._find_characteristic(uuid)
        # if characteristic:
        #     self._gatt.setCharacteristicNotification(characteristic, False)
        #     descriptor = characteristic.getDescriptor(UUID.fromString(CCCD))
        #     descriptor.setValue(BluetoothGattDescriptor.DISABLE_NOTIFICATION_VALUE)
        #     self._gatt.writeDescriptor(descriptor)

        #     self.notification_callback = None

    async def read_gatt_char(self, uuid):
        """Read from a characteristic.

        For bleekWare, you must pass the characteristic's UUID
        as string.
        """
        if not self.is_connected:
            raise BleakError("Client not connected")
        assert self._gatt

        characteristic = self._find_characteristic(uuid)
        if characteristic:
            self._gatt.readCharacteristic(characteristic)
            while not received_data:
                await asyncio.sleep(0.1)
            return bytearray(received_data.pop())
        else:
            raise BleakCharacteristicNotFoundError(uuid)

    async def write_gatt_char(self, uuid, data, response=None):
        """Write to a characteristic.

        For bleekWare, you must pass the characteristic's UUID
        as string.
        """
        if not self.is_connected:
            raise BleakError("Client not connected")
        assert self._gatt

        characteristic = self._find_characteristic(uuid)
        if characteristic:
            if response is None:
                if (
                    characteristic.getProperties()
                    and BluetoothGattCharacteristic.PROPERTY_WRITE
                ):
                    write_type = BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT
                elif (
                    characteristic.getProperties()
                    and BluetoothGattCharacteristic.PROPERTY_WRITE_NO_RESPONSE
                ):
                    write_type = BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE
                else:
                    raise BleakError("unknown property")
            elif response:
                write_type = BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT
            else:
                write_type = BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE

            if Build.VERSION.SDK_INT < 33:  # Android 12 and older
                characteristic.setWriteType(write_type)
                characteristic.setValue(data)
                self._gatt.writeCharacteristic(characteristic)
            else:
                self._gatt.writeCharacteristic(characteristic, data, write_type)
        else:
            raise BleakCharacteristicNotFoundError(uuid)

    @property
    def is_connected(self):
        return False if self._gatt is None else True

    @property
    def mtu_size(self):
        return self._mtu

    async def _get_services(self) -> BleakGATTServiceCollection:
        """Read and store the announced services of a GATT server. PRIVAT.

        The characteristics of the services are also read. Both are
        stored in a list of BLEGattService objects.
        """
        if self.services is not None:
            return self.services

        for service in services:
            new_service = BLEGattService(service)
            characts = cast(
                list[BluetoothGattCharacteristic],
                service.getCharacteristics().toArray(),
            )
            for charact in characts:
                new_service.characteristics.append(str(charact.getUuid()))
            self._services.append(new_service)
        return self._services

    # def _find_characteristic(self, uuid):
    #     """Find and return characteristic object by UUID. PRIVATE."""
    #     if len(uuid) == 4:
    #         uuid = f"0000{uuid}-0000-1000-8000-00805f9b34fb"
    #     elif len(uuid) == 8:
    #         uuid = f"{uuid}-0000-1000-8000-00805f9b34fb"
    #     for service in self._services:
    #         if uuid in service.characteristics:
    #             return service.service.getCharacteristic(UUID.fromString(uuid))
    #     return None
