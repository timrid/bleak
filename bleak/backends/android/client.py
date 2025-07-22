# -*- coding: utf-8 -*-
"""
BLE Client for python-for-android
"""

import asyncio
import logging
import sys
import uuid
import warnings
from typing import Any, Optional, Union

if sys.version_info < (3, 12):
    from typing_extensions import Buffer, override
else:
    from collections.abc import Buffer
    from typing import override

from bleak.assigned_numbers import gatt_char_props_to_strs
from bleak.backends.android.client_callback import (
    OnCharacteristicReadCallback,
    OnCharacteristicWriteCallback,
    OnConnectionStateChangeCallback,
    OnConnectionStateChangeResult,
    OnDescriptorReadCallback,
    OnDescriptorWriteCallback,
    OnMtuChangedCallback,
    OnServicesDiscoveredCallback,
)
from bleak.backends.android.dispatcher import dispatch_func
from bleak.backends.android.framework import (
    broadcast,
    client_callback,
    defs,
)
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.client import BaseBleakClient, NotifyCallback
from bleak.backends.descriptor import BleakGATTDescriptor
from bleak.backends.device import BLEDevice
from bleak.backends.service import BleakGATTService, BleakGATTServiceCollection
from bleak.exc import BleakError

logger = logging.getLogger(__name__)


class BleakClientAndroid(BaseBleakClient):
    """A python-for-android Bleak Client

    Args:
        address_or_ble_device:
            The Bluetooth address of the BLE peripheral to connect to or the
            :class:`BLEDevice` object representing it.
        services:
            Optional set of services UUIDs to filter.
    """

    def __init__(
        self,
        address_or_ble_device: Union[BLEDevice, str],
        services: Optional[set[uuid.UUID]],
        **kwargs,
    ):
        super(BleakClientAndroid, self).__init__(address_or_ble_device, **kwargs)
        self._requested_services = (
            set(map(defs.UUID.fromString, str(services))) if services else None
        )
        # kwarg "device" is for backwards compatibility
        self.__adapter = kwargs.get("adapter", kwargs.get("device", None))
        self.__gatt: defs.BluetoothGatt | None = None
        self.__mtu: int = 23

        self.__callbacks: client_callback._PythonBluetoothGattCallback | None = None

    # Connectivity methods

    @override
    async def connect(self, pair: bool, **kwargs) -> None:
        """Connect to the specified GATT server."""
        if pair:
            logger.warning("Pairing during connect is not implemented on Android")

        loop = asyncio.get_running_loop()

        self.__adapter = defs.BluetoothAdapter.getDefaultAdapter()
        if self.__adapter is None:
            raise BleakError("Bluetooth is not supported on this hardware platform")
        if self.__adapter.getState() != defs.BluetoothAdapter.STATE_ON:
            raise BleakError("Bluetooth is not turned on")

        self.__device = self.__adapter.getRemoteDevice(self.address)

        self.__callbacks = client_callback._PythonBluetoothGattCallback(self, loop)

        self._subscriptions: dict[int, NotifyCallback] = {}

        logger.debug(f"Connecting to BLE device @ {self.address}")

        self.__gatt, _ = await self.__callbacks.dispatcher.perform_and_wait(
            dispatch_api=dispatch_func(
                self.__device.connectGatt,
                defs.context,
                False,
                self.__callbacks.java,
                defs.BluetoothDevice.TRANSPORT_LE,
            ),
            callback_api=OnConnectionStateChangeCallback(),
            callback_expected_result=OnConnectionStateChangeResult(
                new_state=defs.BluetoothProfile.STATE_CONNECTED
            ),
            dispatch_result_indicates_status=False,
        )

        try:
            logger.debug("Connection successful.")

            # unlike other backends, Android doesn't automatically negotiate
            # the MTU, so we request the largest size possible like BlueZ
            logger.debug("requesting mtu...")
            result = await self.__callbacks.dispatcher.perform_and_wait(
                dispatch_api=dispatch_func(self.__gatt.requestMtu, 517),
                callback_api=OnMtuChangedCallback(),
            )
            self.__mtu = result.mtu

            logger.debug("discovering services...")
            await self.__callbacks.dispatcher.perform_and_wait(
                dispatch_api=dispatch_func(self.__gatt.discoverServices),
                callback_api=OnServicesDiscoveredCallback(),
            )

            await self._get_services()
        except BaseException:
            # if connecting is canceled or one of the above fails, we need to
            # disconnect
            try:
                await self.disconnect()
            except Exception:
                pass
            raise

    @override
    async def disconnect(self) -> None:
        """Disconnect from the specified GATT server."""
        logger.debug("Disconnecting from BLE device...")
        if self.__gatt is None:
            # No connection exists. Either one hasn't been created or
            # we have already called disconnect and closed the gatt
            # connection.
            logger.debug("already disconnected")
            return
        assert self.__callbacks

        # Try to disconnect the actual device/peripheral
        try:
            await self.__callbacks.dispatcher.perform_and_wait(
                dispatch_api=dispatch_func(self.__gatt.disconnect),
                callback_api=OnConnectionStateChangeCallback(),
                callback_expected_result=OnConnectionStateChangeResult(
                    defs.BluetoothProfile.STATE_DISCONNECTED
                ),
                unless_already=True,
                dispatch_result_indicates_status=False,
            )
            self.__gatt.close()
        except Exception as e:
            logger.error(f"Attempt to disconnect device failed: {e}")

        self.__gatt = None
        self.__callbacks = None

        # Reset all stored services.
        self.services = None

    @override
    async def pair(self, *args, **kwargs) -> None:
        """Pair with the peripheral.

        You can use ConnectDevice method if you already know the MAC address of the device.
        Else you need to StartDiscovery, Trust, Pair and Connect in sequence.
        """
        loop = asyncio.get_running_loop()

        bonded_future = loop.create_future()

        def handle_bond_state_changed(context: defs.Context, intent: defs.Intent):
            bond_state = intent.getIntExtra(defs.BluetoothDevice.EXTRA_BOND_STATE, -1)
            if bond_state == -1:
                loop.call_soon_threadsafe(
                    bonded_future.set_exception,
                    BleakError(f"Unexpected bond state {bond_state}"),
                )
            elif bond_state == defs.BluetoothDevice.BOND_NONE:
                loop.call_soon_threadsafe(
                    bonded_future.set_exception,
                    BleakError(
                        f"Device with address {self.address} could not be paired with."
                    ),
                )
            elif bond_state == defs.BluetoothDevice.BOND_BONDED:
                loop.call_soon_threadsafe(bonded_future.set_result, True)

        receiver = broadcast.BroadcastReceiver(
            handle_bond_state_changed,
            actions=[defs.BluetoothDevice.ACTION_BOND_STATE_CHANGED],
        )
        receiver.start()
        try:
            # See if it is already paired.
            bond_state = self.__device.getBondState()
            if bond_state == defs.BluetoothDevice.BOND_BONDED:
                return
            elif bond_state == defs.BluetoothDevice.BOND_NONE:
                logger.debug(f"Pairing to BLE device @ {self.address}")
                if not self.__device.createBond():
                    raise BleakError(
                        f"Could not initiate bonding with device @ {self.address}"
                    )
            await bonded_future
        finally:
            receiver.stop()

    @override
    async def unpair(self) -> None:
        """Unpair with the peripheral."""
        warnings.warn(
            "Unpairing is seemingly unavailable in the Android API at the moment."
        )

    @property
    @override
    def is_connected(self) -> bool:
        """Check connection status between this client and the server.

        Returns:
            Boolean representing connection status.

        """
        if self.__callbacks is None:
            return False

        callback_state = self.__callbacks.dispatcher.states.get(
            OnConnectionStateChangeCallback()
        )
        if callback_state is None:
            return False

        callback_result = callback_state.callback_result
        assert isinstance(callback_result, OnConnectionStateChangeResult)

        if callback_result.new_state != defs.BluetoothProfile.STATE_CONNECTED:
            return False

        return True

    @property
    @override
    def mtu_size(self) -> int:
        return self.__mtu

    # GATT services methods

    async def _get_services(self) -> BleakGATTServiceCollection:
        """Get all services registered for this GATT server.

        Returns:
           A :py:class:`bleak.backends.service.BleakGATTServiceCollection` with this device's services tree.

        """
        if self.services is not None:
            return self.services

        assert self.__gatt

        services = BleakGATTServiceCollection()

        logger.debug("Get Services...")
        for java_service in self.__gatt.getServices().toArray():
            assert isinstance(java_service, defs.BluetoothGattService)
            if (
                self._requested_services is not None
                and java_service.getUuid() not in self._requested_services
            ):
                continue

            service = BleakGATTService(
                java_service,
                java_service.getInstanceId(),
                java_service.getUuid().toString(),
            )
            services.add_service(service)

            for java_characteristic in java_service.getCharacteristics().toArray():
                assert isinstance(java_characteristic, defs.BluetoothGattCharacteristic)
                characteristic = BleakGATTCharacteristic(
                    java_characteristic,
                    java_characteristic.getInstanceId(),
                    java_characteristic.getUuid().toString(),
                    gatt_char_props_to_strs((java_characteristic.getProperties())),
                    lambda: self.__mtu - 3,
                    service,
                )
                services.add_characteristic(characteristic)

                for descriptor_index, java_descriptor in enumerate(
                    java_characteristic.getDescriptors().toArray()
                ):
                    assert isinstance(java_descriptor, defs.BluetoothGattDescriptor)
                    descriptor = BleakGATTDescriptor(
                        java_descriptor,
                        characteristic.handle + 1 + descriptor_index,
                        java_descriptor.getUuid().toString(),
                        characteristic,
                    )
                    services.add_descriptor(descriptor)

        self.services = services
        return self.services

    # IO methods

    @override
    async def read_gatt_char(
        self, characteristic: BleakGATTCharacteristic, **kwargs: Any
    ) -> bytearray:
        """Perform read operation on the specified GATT characteristic.

        Args:
            characteristic (BleakGATTCharacteristic): The characteristic to read from.

        Returns:
            (bytearray) The read data.

        """
        assert self.__callbacks
        assert self.__gatt

        callback_result = await self.__callbacks.dispatcher.perform_and_wait(
            dispatch_api=dispatch_func(
                self.__gatt.readCharacteristic, characteristic.obj
            ),
            callback_api=OnCharacteristicReadCallback(characteristic.handle),
        )
        value = bytearray(callback_result.value)
        logger.debug(
            f"Read Characteristic {characteristic.uuid} | {characteristic.handle}: {value}"
        )
        return value

    @override
    async def read_gatt_descriptor(
        self, descriptor: BleakGATTDescriptor, **kwargs: Any
    ) -> bytearray:
        """Perform read operation on the specified GATT descriptor.

        Args:
            descriptor: The descriptor to read from.

        Returns:
            The read data.
        """
        assert self.__callbacks
        assert self.__gatt

        callback_result = await self.__callbacks.dispatcher.perform_and_wait(
            dispatch_api=dispatch_func(self.__gatt.readDescriptor, descriptor.obj),
            callback_api=OnDescriptorReadCallback(uuid=descriptor.uuid),
        )
        value = bytearray(callback_result.value)

        logger.debug(
            f"Read Descriptor {descriptor.uuid} | {descriptor.handle}: {value}"
        )

        return value

    @override
    async def write_gatt_char(
        self, characteristic: BleakGATTCharacteristic, data: Buffer, response: bool
    ) -> None:
        assert self.__callbacks
        assert self.__gatt
        assert isinstance(characteristic.obj, defs.BluetoothGattCharacteristic)

        if response:
            characteristic.obj.setWriteType(
                defs.BluetoothGattCharacteristic.WRITE_TYPE_DEFAULT
            )
        else:
            characteristic.obj.setWriteType(
                defs.BluetoothGattCharacteristic.WRITE_TYPE_NO_RESPONSE
            )

        characteristic.obj.setValue(data)

        await self.__callbacks.dispatcher.perform_and_wait(
            dispatch_api=dispatch_func(
                self.__gatt.writeCharacteristic, characteristic.obj
            ),
            callback_api=OnCharacteristicWriteCallback(
                handle=characteristic.handle,
            ),
        )

        logger.debug(
            f"Write Characteristic {characteristic.uuid} | {characteristic.handle}: {data}"
        )

    @override
    async def write_gatt_descriptor(
        self, descriptor: BleakGATTDescriptor, data: Buffer
    ) -> None:
        """Perform a write operation on the specified GATT descriptor.

        Args:
            data (bytes or bytearray): The data to send.

        """
        assert self.__callbacks
        assert self.__gatt
        assert self.services
        assert isinstance(descriptor.obj, defs.BluetoothGattDescriptor)

        descriptor.obj.setValue(data)

        await self.__callbacks.dispatcher.perform_and_wait(
            dispatch_api=dispatch_func(self.__gatt.writeDescriptor, descriptor.obj),
            callback_api=OnDescriptorWriteCallback(uuid=descriptor.uuid),
        )

        logger.debug(
            f"Write Descriptor {descriptor.uuid} | {descriptor.handle}: {data}"
        )

    @override
    async def start_notify(
        self,
        characteristic: BleakGATTCharacteristic,
        callback: NotifyCallback,
        **kwargs,
    ) -> None:
        """
        Activate notifications/indications on a characteristic.
        """
        self._subscriptions[characteristic.handle] = callback

        assert self.__gatt is not None

        if not self.__gatt.setCharacteristicNotification(characteristic.obj, True):
            raise BleakError(
                f"Failed to enable notification for characteristic {characteristic.uuid}"
            )

        await self.write_gatt_descriptor(
            characteristic.notification_descriptor,
            bytes(defs.BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE),
        )

    @override
    async def stop_notify(self, characteristic: BleakGATTCharacteristic) -> None:
        """Deactivate notification/indication on a specified characteristic.

        Args:
            characteristic (BleakGATTCharacteristic): The characteristic to deactivate
                notification/indication on,.

        """
        assert self.__gatt

        await self.write_gatt_descriptor(
            characteristic.notification_descriptor,
            bytes(defs.BluetoothGattDescriptor.DISABLE_NOTIFICATION_VALUE),
        )

        if not self.__gatt.setCharacteristicNotification(characteristic.obj, False):
            raise BleakError(
                f"Failed to disable notification for characteristic {characteristic.uuid}"
            )
        del self._subscriptions[characteristic.handle]
