import asyncio
import contextlib
from typing import Any, Callable

import toga
from toga import Button, DetailedList
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData
from bleak_example.ble_device_box import BLEDeviceBox
from bleak_example.custom_list_view import CustomListRow, CustomListView


class BLEDeviceRow(CustomListRow):
    def __init__(
        self,
        device: BLEDevice,
        adv_data: AdvertisementData,
        on_click: Callable[[BLEDevice, AdvertisementData], None],
    ):
        super().__init__()
        self.device = device
        self.adv_data = adv_data
        self.on_click = on_click

        box = toga.Box(style=Pack(direction=COLUMN, margin=5))

        row_box = toga.Box(style=Pack(direction=ROW, flex=1))
        row_box.add(
            toga.Label(
                f"RSSI={adv_data.rssi}",
                style=Pack(font_size=18, horizontal_align_content="center"),
            ),
        )
        row_box.add(
            toga.Label(
                device.name or f"No name ({device.address})",
                style=Pack(
                    font_weight="bold",
                    font_size=24,
                    margin_left=5,
                ),
            )
        )
        row_box.add(toga.Label("", style=Pack(flex=1)))  # spacer
        row_box.add(toga.Button("Show", on_press=self.on_show_press))

        box.add(row_box)

        self.add(box)

    def on_show_press(self, widget):
        self.on_click(self.device, self.adv_data)


class ExceptionRow(CustomListRow):
    def __init__(self, ex: Exception):
        super().__init__()
        box = toga.Box(style=Pack(direction=COLUMN, margin=5, flex=1))

        self.ex = ex
        label = toga.Label("Error:", style=Pack(font_weight="bold"))
        box.add(label)
        label = toga.MultilineTextInput(
            readonly=True,
            value=f"{ex}",
            style=Pack(flex=1),
        )
        box.add(label)

        self.add(box)


class InfoRow(CustomListRow):
    def __init__(self, info: str):
        super().__init__()
        box = toga.Box(style=Pack(direction=COLUMN, margin=5))

        self.info = info
        label = toga.Label(f"{info}", style=Pack(font_weight="bold"))
        box.add(label)

        self.add(box)


class BLEScanResultsListView(CustomListView):
    def append_device(
        self,
        device: BLEDevice,
        adv_data: AdvertisementData,
        on_click: Callable[[BLEDevice, AdvertisementData], None],
    ):
        self.add_row(BLEDeviceRow(device, adv_data, on_click))

    def append_exception(self, ex: Exception):
        self.add_row(ExceptionRow(ex))

    def append_info(self, info: str):
        self.add_row(InfoRow(info))


class BLEScanBox(toga.Box):
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
        self.scan_results_view = BLEScanResultsListView(
            style=Pack(direction=COLUMN, flex=1),
            horizontal=False,
        )

        self.scan_running = False

        self.add(self.scan_button)
        self.add(self.scan_results_view)

    async def start_scan(self, widget):
        """Use scanner with 'with' container.

        The scan result in scanner.discovered_devices and
        scanner.discovered_devices_and_advertisement_data
        contains each discovered device only once.
        """
        if self.scan_running is True:
            return

        self.scan_button.enabled = False
        orig_btn_text = self.scan_button.text
        self.scan_button.text = "Scanning..."
        self.scan_results_view.clear()
        # self.scan_results_view.append_info("Scanning...")
        try:
            async with BleakScanner() as scanner:
                await asyncio.sleep(5)
                self.show_scan_results(
                    scanner.discovered_devices_and_advertisement_data
                )

        except Exception as e:
            self.scan_results_view.append_exception(e)
        finally:
            self.scan_button.enabled = True
            self.scan_button.text = orig_btn_text

    def show_scan_results(self, data: dict[str, tuple[BLEDevice, AdvertisementData]]):
        """Show names of found devices and attached advertisment data.

        'data' is a dictionary, where the keys are the BLE addresses
        and the values are tuples of BLE device, advertisement data.
        """
        self.scan_results_view.clear()
        values = list(data.values())
        values = sorted(values, key=lambda value: value[1].rssi, reverse=True)
        for value in values:
            device, adv_data = value
            self.scan_results_view.append_device(
                device, adv_data, self.show_device_data
            )

    def show_device_data(self, device: BLEDevice, adv_data: AdvertisementData):
        self.main_window.content = BLEDeviceBox(
            self.main_window, self, device, adv_data
        )
