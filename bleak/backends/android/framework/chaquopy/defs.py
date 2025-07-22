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
from android.content import Context, Intent  # noqa: F401, E402
from android.content.pm import PackageManager
from android.os import Build, ParcelUuid  # noqa: F401, E402
from java.util import UUID, ArrayList, HashMap  # noqa: F401, E402
from org.beeware.android import MainActivity  # noqa: F401, E402

activity = MainActivity.singletonThis
context = activity.getApplicationContext()
