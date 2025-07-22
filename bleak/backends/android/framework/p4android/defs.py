# caching constants avoids unnecessary extra use of the jni-python interface, which can be slow
from typing import TYPE_CHECKING

from jnius import autoclass, cast  # type: ignore

if TYPE_CHECKING:
    from android.bluetooth import (
        BluetoothAdapter,  # noqa: F401
        BluetoothDevice,  # noqa: F401
        BluetoothGatt,  # noqa: F401
        BluetoothGattCharacteristic,  # noqa: F401
        BluetoothGattDescriptor,  # noqa: F401
        BluetoothGattService,  # noqa: F401
        BluetoothProfile,  # noqa: F401
    )
    from android.bluetooth.le import (
        BluetoothLeScanner,  # noqa: F401
        ScanCallback,  # noqa: F401
        ScanFilter,  # noqa: F401
        ScanResult,  # noqa: F401
        ScanSettings,  # noqa: F401
    )

    ScanFilterBuilder = ScanFilter.Builder  # noqa: F401
    ScanSettingsBuilder = ScanSettings.Builder  # noqa: F401

    from android import Manifest  # noqa: F401, E402
    from android.app import Activity
    from android.content import Context, Intent  # noqa: F401, E402
    from android.content.pm import PackageManager
    from android.os import Build, ParcelUuid  # noqa: F401, E402
    from java.util import UUID, ArrayList, HashMap  # noqa: F401, E402
else:
    BluetoothAdapter = autoclass("android.bluetooth.BluetoothAdapter")
    BluetoothDevice = autoclass("android.bluetooth.BluetoothDevice")
    BluetoothGatt = autoclass("android.bluetooth.BluetoothGatt")
    BluetoothGattCharacteristic = autoclass(
        "android.bluetooth.BluetoothGattCharacteristic"
    )
    BluetoothGattDescriptor = autoclass("android.bluetooth.BluetoothGattDescriptor")
    BluetoothGattService = autoclass("android.bluetooth.BluetoothGattService")
    BluetoothProfile = autoclass("android.bluetooth.BluetoothProfile")

    BluetoothLeScanner = autoclass("android.bluetooth.le.BluetoothLeScanner")
    ScanCallback = autoclass("android.bluetooth.le.ScanCallback")
    ScanFilter = autoclass("android.bluetooth.le.ScanFilter")
    ScanResult = autoclass("android.bluetooth.le.ScanResult")
    ScanSettings = autoclass("android.bluetooth.le.ScanSettings")

    ScanFilterBuilder = autoclass("android.bluetooth.le.ScanFilter$Builder")
    ScanSettingsBuilder = autoclass("android.bluetooth.le.ScanSettings$Builder")

    Manifest = autoclass("android.content.Manifest")
    Intent = autoclass("android.content.Intent")
    PackageManager = autoclass("android.content.pm.PackageManager")
    Build = autoclass("android.os.Build")
    ParcelUuid = autoclass("android.os.ParcelUuid")

    ArrayList = autoclass("java.util.ArrayList")
    UUID = autoclass("java.util.UUID")
    HashMap = autoclass("java.util.HashMap")

PythonActivity = autoclass("org.kivy.android.PythonActivity")
activity: Activity = cast("android.app.Activity", PythonActivity.mActivity)
context: Context = cast("android.content.Context", activity.getApplicationContext())

BLEAK_JNI_NAMESPACE = "com.github.hbldh.bleak"
PythonScanCallback = autoclass(BLEAK_JNI_NAMESPACE + ".PythonScanCallback")
PythonBluetoothGattCallback = autoclass(
    BLEAK_JNI_NAMESPACE + ".PythonBluetoothGattCallback"
)
