import asyncio
import logging
import sys
import warnings
from typing import Literal, Optional

from bleak.backends.android.dispatcher import dispatch_func
from bleak.backends.android.scanner_callback import OnScanCallback

if sys.version_info < (3, 11):
    from async_timeout import timeout as async_timeout
else:
    from asyncio import timeout as async_timeout

if sys.version_info < (3, 12):
    from typing_extensions import override
else:
    from typing import override

from bleak.backends.scanner import (
    AdvertisementData,
    AdvertisementDataCallback,
    BaseBleakScanner,
)
from bleak.exc import BleakError

logger = logging.getLogger(__name__)

# if os.environ.get("CHAQUOPY_PROCESS_TYPE") is not None:
from bleak.backends.android.chaquopy import defs
from bleak.backends.android.chaquopy.broadcast import (
    _PythonBroadcastReceiver as BroadcastReceiver,
)
from bleak.backends.android.chaquopy.permissions import check_for_permissions
from bleak.backends.android.chaquopy.scanner_callback import _PythonScanCallback

# elif os.environ.get("P4A_BOOTSTRAP") is not None:
#     from bleak.backends.android.p4android import defs
#     from bleak.backends.android.p4android.permissions import check_for_permissions
#     from bleak.backends.android.p4android.client_cascanner_callbackllback import _PythonScanCallback
# else:
#     raise BleakError("No supported Android environment detected.")


class BleakScannerAndroid(BaseBleakScanner):
    """
    The python-for-android Bleak BLE Scanner.

    Args:
        detection_callback:
            Optional function that will be called each time a device is
            discovered or advertising data has changed.
        service_uuids:
            Optional list of service UUIDs to filter on. Only advertisements
            containing this advertising data will be received. Specifying this
            also enables scanning while the screen is off on Android.
        scanning_mode:
            Set to ``"passive"`` to avoid the ``"active"`` scanning mode.
    """

    __scanner = None

    def __init__(
        self,
        detection_callback: Optional[AdvertisementDataCallback],
        service_uuids: Optional[list[str]],
        scanning_mode: Literal["active", "passive"],
        **kwargs,
    ):
        super(BleakScannerAndroid, self).__init__(detection_callback, service_uuids)

        if scanning_mode == "passive":
            self.__scan_mode = defs.ScanSettings.SCAN_MODE_OPPORTUNISTIC
        else:
            self.__scan_mode = defs.ScanSettings.SCAN_MODE_LOW_LATENCY

        self.__adapter: defs.BluetoothAdapter | None = None
        self.__javascanner: defs.BluetoothLeScanner | None = None
        self.__callback = None

    @override
    async def start(self) -> None:
        if BleakScannerAndroid.__scanner is not None:
            raise BleakError("A BleakScanner is already scanning on this adapter.")

        logger.debug("Starting BTLE scan")

        loop = asyncio.get_running_loop()

        if self.__callback is None:
            self.__callback = _PythonScanCallback(self, loop)
        if self.__javascanner is None:
            await check_for_permissions(loop)
            self.__adapter = defs.BluetoothAdapter.getDefaultAdapter()
            if self.__adapter is None:
                raise BleakError("Bluetooth is not supported on this hardware platform")
            if self.__adapter.getState() != defs.BluetoothAdapter.STATE_ON:
                raise BleakError("Bluetooth is not turned on")

            self.__javascanner = self.__adapter.getBluetoothLeScanner()

        assert self.__adapter

        BleakScannerAndroid.__scanner = self

        filters = defs.ArrayList()
        if self._service_uuids:
            for uuid in self._service_uuids:
                filters.add(
                    defs.ScanFilterBuilder()
                    .setServiceUuid(defs.ParcelUuid.fromString(uuid))
                    .build()
                )

        scan_settings = (
            defs.ScanSettingsBuilder()
            .setScanMode(self.__scan_mode)
            .setReportDelay(0)
            .setPhy(defs.ScanSettings.PHY_LE_ALL_SUPPORTED)
            .setNumOfMatches(defs.ScanSettings.MATCH_NUM_MAX_ADVERTISEMENT)
            .setMatchMode(defs.ScanSettings.MATCH_MODE_AGGRESSIVE)
            .setCallbackType(defs.ScanSettings.CALLBACK_TYPE_ALL_MATCHES)
            .build()
        )
        scanfuture = self.__callback.dispatcher.perform_and_wait(
            dispatch_api=dispatch_func(
                self.__javascanner.startScan,
                filters,
                scan_settings,
                self.__callback.java,
            ),
            callback_api=OnScanCallback(),
            dispatch_result_indicates_status=False,
        )
        self.__javascanner.flushPendingScanResults(self.__callback.java)

        try:
            async with async_timeout(0.2):
                await scanfuture
        except asyncio.exceptions.TimeoutError:
            pass
        except BleakError as bleakerror:
            await self.stop()
            if bleakerror.args != (
                "onScan",
                "SCAN_FAILED_APPLICATION_REGISTRATION_FAILED",
            ):
                raise bleakerror
            else:
                # there might be a clearer solution to this if android source and vendor
                # documentation are reviewed for the meaning of the error
                # https://stackoverflow.com/questions/27516399/solution-for-ble-scans-scan-failed-application-registration-failed
                warnings.warn(
                    "BT API gave SCAN_FAILED_APPLICATION_REGISTRATION_FAILED.  Resetting adapter."
                )

                logger.info(
                    "reset bluetooth adapter to handle SCAN_FAILED_APPLICATION_REGSTRATION_FAILED ..."
                )
                await reset_bluetooth_adapter(self.__adapter, loop)

                logger.debug("restarting scan ...")
                return await self.start()

    @override
    async def stop(self) -> None:
        assert self.__callback

        if self.__javascanner is not None:
            logger.debug("Stopping BTLE scan")
            self.__javascanner.stopScan(self.__callback.java)
            BleakScannerAndroid.__scanner = None
            self.__javascanner = None
        else:
            logger.debug("BTLE scan already stopped")

    def _handle_scan_result(self, result: defs.ScanResult) -> None:
        native_device = result.getDevice()
        record = result.getScanRecord()

        service_uuids = record.getServiceUuids()
        if service_uuids is None:
            service_uuids = []
        else:
            service_uuids = [service_uuid.toString() for service_uuid in service_uuids]

        if not self.is_allowed_uuid(service_uuids):
            return

        manufacturer_data = record.getManufacturerSpecificData()
        manufacturer_data = {
            manufacturer_data.keyAt(index): bytes(manufacturer_data.valueAt(index))
            for index in range(manufacturer_data.size())
        }

        service_data = {}
        temp_map = defs.HashMap(record.getServiceData())
        service_data_iterator = temp_map.entrySet().iterator()
        while service_data_iterator.hasNext():
            element = service_data_iterator.next()
            service_data[element.getKey().toString()] = bytes(element.getValue())

        tx_power = record.getTxPowerLevel()

        # change "not present" value to None to match other backends
        if tx_power == -2147483648:  # Integer#MIN_VALUE
            tx_power = None

        advertisement = AdvertisementData(
            local_name=record.getDeviceName(),
            manufacturer_data=manufacturer_data,
            service_data=service_data,
            service_uuids=service_uuids,
            tx_power=tx_power,
            rssi=result.getRssi(),
            platform_data=(result,),
        )

        device = self.create_or_update_device(
            native_device.getAddress(),
            native_device.getAddress(),
            native_device.getName(),
            native_device,
            advertisement,
        )

        self.call_detection_callbacks(device, advertisement)


async def reset_bluetooth_adapter(
    adapter: defs.BluetoothAdapter, loop: asyncio.AbstractEventLoop
):
    def handler_waiting_for_state(state: int, stateFuture: asyncio.Future):
        def handle_adapter_state_changed(context, intent: defs.Intent):
            adapter_state = intent.getIntExtra(
                defs.BluetoothAdapter.EXTRA_STATE,
                defs.BluetoothAdapter.ERROR,
            )
            if adapter_state == defs.BluetoothAdapter.ERROR:
                loop.call_soon_threadsafe(
                    stateFuture.set_exception,
                    BleakError(f"Unexpected adapter state {adapter_state}"),
                )
            elif adapter_state == state:
                loop.call_soon_threadsafe(stateFuture.set_result, adapter_state)

        return handle_adapter_state_changed

    logger.info("disabling bluetooth adapter ...")
    state_off_future: asyncio.Future = loop.create_future()
    receiver = BroadcastReceiver(
        handler_waiting_for_state(defs.BluetoothAdapter.STATE_OFF, state_off_future),
        actions=[defs.BluetoothAdapter.ACTION_STATE_CHANGED],
    )
    receiver.start()
    try:
        adapter.disable()
        await state_off_future
    finally:
        receiver.stop()

    logger.info("re-enabling bluetooth adapter ...")
    state_on_future: asyncio.Future = loop.create_future()
    receiver = BroadcastReceiver(
        handler_waiting_for_state(defs.BluetoothAdapter.STATE_ON, state_on_future),
        actions=[defs.BluetoothAdapter.ACTION_STATE_CHANGED],
    )
    receiver.start()
    try:
        adapter.enable()
        await state_on_future
    finally:
        receiver.stop()
