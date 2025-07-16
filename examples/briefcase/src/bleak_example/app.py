"""
Run Bluetooth LE on Android
"""

import asyncio
from typing import Any, Iterable

import toga
from toga import Button, DetailedList, MultilineTextInput
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from bleak import BleakClient
from bleak import BleakScanner as Scanner
from bleak.backends.characteristic import BleakGATTCharacteristic
from bleak.backends.descriptor import BleakGATTDescriptor
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from bleak.backends.service import BleakGATTService, BleakGATTServiceCollection


class ScanBox(toga.Box):
    def __init__(
        self,
        main_window: toga.Window,
    ):
        super().__init__(style=Pack(direction=COLUMN))
        self.main_window = main_window

        self.scan_button = Button(
            "Scan for BLE devices",
            on_press=self.start_scan,
        )
        self.scan_data = toga.DetailedList(
            style=Pack(margin=(10, 5), height=400),
            on_secondary_action=self.show_device_data,
        )

        self.add(self.scan_button)
        self.add(self.scan_data)

    async def start_scan(self, widget):
        """Use scanner with 'with' container.

        The scan result in scanner.discovered_devices and
        scanner.discovered_devices_and_advertisement_data
        contains each discovered device only once.
        """
        self.scan_data.data.clear()
        self.scan_data.data.append({"title": "Scanning..."})

        async with Scanner() as scanner:
            await asyncio.sleep(5)
            self.show_scan_results(scanner.discovered_devices_and_advertisement_data)

    def show_scan_results(self, data: dict[str, tuple[BLEDevice, AdvertisementData]]):
        """Show names of found devices and attached advertisment data.

        'data' is a dictionary, where the keys are the BLE addresses
        and the values are tuples of BLE device, advertisement data.
        """
        self.scan_data.data.clear()
        values = list(data.values())
        values = sorted(values, key=lambda value: value[1].rssi, reverse=True)
        for value in values:
            device, adv_data = value
            self.scan_data.data.append(
                {
                    "title": device.name or f"No name ({device.address})",
                    "subtitle": f"RSSI={adv_data.rssi}",
                    "device": device,
                    "adv_data": adv_data,
                }
            )

    def show_device_data(self, widget: DetailedList, row: Any, **kwargs: Any):
        self.main_window.content = BLEDeviceBox(
            self.main_window, self, row.device, row.adv_data
        )


# class CustomListView(toga.Box):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.container = toga.Box(style=Pack(direction=COLUMN))
#         self.scrolled = toga.ScrollContainer(content=self.container)
#         self.add(self.scrolled)


class CustomListView(toga.ScrollContainer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.container = toga.Box(style=Pack(direction=COLUMN))
        self.content = self.container

    def clear(self) -> None:
        self.container.children.clear()

    def add_row(self, row: "CustomListRow"):
        self.container.add(row)
        self.container.add(toga.Divider())


class CustomListRow(toga.Box):
    def __init__(self):
        super().__init__(style=Pack(direction=ROW, margin=5))


class ServiceRow(CustomListRow):
    def __init__(self, service: BleakGATTService):
        super().__init__()
        box = toga.Box(style=Pack(direction=COLUMN, margin=5))

        self.service = service
        label = toga.Label("Service:", style=Pack(font_weight="bold"))
        box.add(label)
        label = toga.Label(f"{service.uuid}")
        box.add(label)

        self.add(box)


class CharacteristicRow(CustomListRow):
    def __init__(self, characteristic: BleakGATTCharacteristic):
        super().__init__()
        box = toga.Box(style=Pack(direction=COLUMN, margin=5))

        self.characteristic = characteristic
        label = toga.Label("Characteristic", style=Pack(font_weight="bold"))
        box.add(label)

        label = toga.Label(f"{characteristic.uuid}")
        box.add(label)

        button_box = toga.Box(style=Pack(direction=ROW, margin=5))
        for prop in characteristic.properties:
            btn = toga.Button(text=prop)
            button_box.add(btn)
        box.add(button_box)

        self.add(box)


class DescriptorRow(CustomListRow):
    def __init__(self, descriptor: BleakGATTDescriptor):
        super().__init__()
        box = toga.Box(style=Pack(direction=COLUMN, margin=5))

        self.descriptor = descriptor
        label = toga.Label("Descriptor", style=Pack(font_weight="bold"))
        box.add(label)
        label = toga.Label(f"{descriptor.uuid}")
        box.add(label)

        self.add(box)


class BLEServiceListView(CustomListView):
    def set_services(self, services: BleakGATTServiceCollection):
        self.clear()
        for service in services:
            self.add_row(ServiceRow(service))
            for characteristic in service.characteristics:
                self.add_row(CharacteristicRow(characteristic))
                for descriptor in characteristic.descriptors:
                    self.add_row(DescriptorRow(descriptor))


class BLEDeviceBox(toga.Box):
    def __init__(
        self,
        main_window: toga.Window,
        parent_box: toga.Box,
        device: BLEDevice,
        adv_data: AdvertisementData,
    ):
        super().__init__(style=Pack(direction=COLUMN, flex=1))
        self.main_window = main_window
        self.parent_box = parent_box
        self.device = device
        self.adv_data = adv_data

        back_button = toga.Button("Back", on_press=self.show_main_box)

        title = toga.Label(
            device.name or f"No name ({device.address})",
            style=Pack(font_weight="bold", font_size=20, align_items="center"),
        )

        self.adv_data_txt = toga.MultilineTextInput()

        connect_button = toga.Button("Connect", on_press=self.connect_client)

        self.services_view = BLEServiceListView(style=Pack(direction=COLUMN, flex=1))

        self.add(back_button)
        self.add(title)
        self.add(self.adv_data_txt)
        self.add(connect_button)
        self.add(self.services_view)

        self.show_adv_data()

    def show_adv_data(self):
        s = ""
        for company_id, data in self.adv_data.manufacturer_data.items():
            s += f"Manufacturer Data ({company_id}): {data.hex(' ')}\n"
        for key, data in self.adv_data.service_data.items():
            s += f"Service Data ({key}): {data.hex(' ')}\n"
        s += f"RSSI: {self.adv_data.rssi}\n"
        if self.adv_data.tx_power:
            s += f"TX-Power: {self.adv_data.tx_power}\n"
        for service_uuid in self.adv_data.service_uuids:
            s += f"Service UUID: {service_uuid}\n"
        self.adv_data_txt.value = s

    async def connect_client(self, widget):
        async with BleakClient(self.device) as client:
            self.services_view.set_services(client.services)

    def show_main_box(self, widget):
        self.main_window.content = self.parent_box


class BleScannerApp(toga.App):
    """A small App to demonstrate Bluetooth LE functionality with bleekWare.

    bleekWare replaces Bleak on the Android platform when working with
    Toga and BeeWare (see the conditional import above).

    This app demonstrates several possibilities to perform a scan and
    read the advertised data.
    """

    def startup(self):
        """Set up the GUI."""
        main_window = toga.MainWindow(title="BLE Scanner Demo App")

        main_box = ScanBox(main_window)

        main_window.content = main_box

        self.main_window = main_window
        self.main_window.show()


def main():
    return BleScannerApp()
