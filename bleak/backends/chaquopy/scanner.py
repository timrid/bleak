from typing import Literal

from android.bluetooth import BluetoothAdapter
from android.bluetooth.le import ScanCallback, ScanFilter, ScanResult, ScanSettings
from android.os import ParcelUuid
from java import Override, jint, jvoid, static_proxy
from java.util import ArrayList, HashMap
from org.beeware.android import MainActivity

from bleak.backends.chaquopy import check_for_permissions
from bleak.backends.scanner import (
    AdvertisementData,
    AdvertisementDataCallback,
    BaseBleakScanner,
)
from bleak.exc import BleakError


class _PythonScanCallback(static_proxy(ScanCallback)):
    """Callback class for LE Scan. PRIVATE.

    This class holds methods that receive and handle
    data from Android's BluetoothLeScanner methods.
    It is not intended to call this class directly.
    """

    def __init__(self, scanner: "BleakScannerChaquopy"):
        super(_PythonScanCallback, self).__init__()
        self.scanner = scanner

    @Override(jvoid, [jint, ScanResult])
    def onScanResult(self, callbackType: jint, scanResult: ScanResult):
        """Receive and handle the scan result for BLE devices.

        This is the callback method for BluetoothLeScanner.startScan().
        """
        native_device = scanResult.getDevice()
        record = scanResult.getScanRecord()

        service_uuids = record.getServiceUuids()
        if service_uuids is not None:
            service_uuids = [
                service_uuid.toString() for service_uuid in service_uuids.toArray()
            ]

        if not self.scanner.is_allowed_uuid(service_uuids):
            return

        manufacturer = record.getManufacturerSpecificData()
        manufacturer = {
            manufacturer.keyAt(index): bytes(manufacturer.valueAt(index))
            for index in range(manufacturer.size())
        }

        # Original code from Bleak:
        # service_data = {
        #     entry.getKey().toString(): bytes(entry.getValue())
        #     for entry in record.getServiceData().entrySet()
        # }
        # Need some workaround, as 'getServiceData().entrySet() is a Map
        # and is not iterable with Chaquopy. So we need to handle the
        # iteration by ourselves.
        # Also, MapCollection need to be converted to HashMap, otherwise
        # next() is not working.
        service_data = {}
        temp_map = HashMap(record.getServiceData())
        service_data_iterator = temp_map.entrySet().iterator()
        while service_data_iterator.hasNext():
            element = service_data_iterator.next()
            service_data[element.getKey().toString()] = bytes(element.getValue())

        tx_power = record.getTxPowerLevel()
        if tx_power == -2147483648:  # Integer#MIN_VALUE
            # change "not present" value to None to match other backends
            tx_power = None

        advertisement = AdvertisementData(
            local_name=record.getDeviceName(),
            manufacturer_data=manufacturer,
            service_data=service_data,
            service_uuids=service_uuids,
            tx_power=tx_power,
            rssi=scanResult.getRssi(),
            platform_data=(scanResult,),
        )

        device = self.scanner.create_or_update_device(
            native_device.getAddress(),
            native_device.getAddress(),
            native_device.getName(),
            native_device,
            advertisement,
        )

        self.scanner.call_detection_callbacks(device, advertisement)


class BleakScannerChaquopy(BaseBleakScanner):
    """Class to scan for free (un-connected) Bluetooth LE devices."""

    # TODO: Singleton is not good...
    scanner = None

    def __init__(
        self,
        detection_callback: AdvertisementDataCallback | None = None,
        service_uuids: list[str] | None = None,
        scanning_mode: Literal["active", "passive"] = "active",
        **kwargs,
    ):
        super(BleakScannerChaquopy, self).__init__(detection_callback, service_uuids)

        self.activity = self.context = MainActivity.singletonThis

        if scanning_mode == "passive":
            self.scan_mode = ScanSettings.SCAN_MODE_OPPORTUNISTIC
        else:
            self.scan_mode = ScanSettings.SCAN_MODE_LOW_LATENCY

    async def start(self):
        """Start a scan for BLE devices."""
        if BleakScannerChaquopy.scanner is not None:
            raise BleakError("A BleakScanner is already scanning on this adapter.")

        scan_settings_builder = ScanSettings.Builder()
        scan_settings_builder.setScanMode(self.scan_mode)
        scan_settings_builder.setReportDelay(0)
        scan_settings_builder.setPhy(ScanSettings.PHY_LE_ALL_SUPPORTED)
        scan_settings_builder.setNumOfMatches(ScanSettings.MATCH_NUM_MAX_ADVERTISEMENT)
        scan_settings_builder.setMatchMode(ScanSettings.MATCH_MODE_AGGRESSIVE)
        scan_settings_builder.setCallbackType(ScanSettings.CALLBACK_TYPE_ALL_MATCHES)
        scan_settings = scan_settings_builder.build()

        check_for_permissions(self.activity)

        self.adapter = BluetoothAdapter.getDefaultAdapter()
        if self.adapter is None:
            raise BleakError("Bluetooth is not supported on this hardware platform")
        if self.adapter.getState() != BluetoothAdapter.STATE_ON:
            raise BleakError("Bluetooth is not turned on")

        filters = ArrayList()
        if self._service_uuids:
            for uuid in self._service_uuids:
                filters.add(
                    ScanFilter.Builder()
                    .setServiceUuid(ParcelUuid.fromString(uuid))
                    .build()
                )

        self.seen_devices = {}

        try:
            self.leScanner = self.adapter.getBluetoothLeScanner()
            BleakScannerChaquopy.scanner = self

            self.callback = _PythonScanCallback(BleakScannerChaquopy.scanner)

            self.leScanner.startScan(filters, scan_settings, self.callback)
        except Exception as e:
            # 'startScan' can fail e.g. with an SecurityException if the app does not have
            # the required permissions.
            BleakScannerChaquopy.scanner = None
            self.leScanner = None
            raise BleakError(f"Failed to start scan: {e}") from e

    async def stop(self):
        """Stop a running scan."""
        if self.leScanner is not None:
            self.leScanner.stopScan(self.callback)
            BleakScannerChaquopy.scanner = None
            self.leScanner = None
