# caching constants avoids unnecessary extra use of the jni-python interface, which can be slow
from jnius import autoclass, cast  # type: ignore

BluetoothAdapter = autoclass("android.bluetooth.BluetoothAdapter")
BluetoothDevice = autoclass("android.bluetooth.BluetoothDevice")
BluetoothGatt = autoclass("android.bluetooth.BluetoothGatt")
BluetoothGattCharacteristic = autoclass("android.bluetooth.BluetoothGattCharacteristic")
BluetoothGattDescriptor = autoclass("android.bluetooth.BluetoothGattDescriptor")
BluetoothGattService = autoclass("android.bluetooth.BluetoothGattService")
BluetoothProfile = autoclass("android.bluetooth.BluetoothProfile")

BluetoothLeScanner = autoclass("android.bluetooth.le.BluetoothLeScanner")
ScanCallback = autoclass("android.bluetooth.le.ScanCallback")
ScanFilter = autoclass("android.bluetooth.le.ScanFilter")
ScanFilterBuilder = autoclass("android.bluetooth.le.ScanFilter$Builder")
ScanResult = autoclass("android.bluetooth.le.ScanResult")
ScanSettings = autoclass("android.bluetooth.le.ScanSettings")
ScanSettingsBuilder = autoclass("android.bluetooth.le.ScanSettings$Builder")

Manifest = autoclass("android.content.Manifest")
Intent = autoclass("android.content.Intent")
PackageManager = autoclass("android.content.pm.PackageManager")
ParcelUuid = autoclass("android.os.ParcelUuid")
Build = autoclass("android.os.Build")

ArrayList = autoclass("java.util.ArrayList")
UUID = autoclass("java.util.UUID")
HashMap = autoclass("java.util.HashMap")

PythonActivity = autoclass("org.kivy.android.PythonActivity")
activity = cast("android.app.Activity", PythonActivity.mActivity)
context = cast("android.content.Context", activity.getApplicationContext())

BLEAK_JNI_NAMESPACE = "com.github.hbldh.bleak"
PythonScanCallback = autoclass(BLEAK_JNI_NAMESPACE + ".PythonScanCallback")
PythonBluetoothGattCallback = autoclass(
    BLEAK_JNI_NAMESPACE + ".PythonBluetoothGattCallback"
)
