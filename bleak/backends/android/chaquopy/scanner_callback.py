import asyncio

from android.bluetooth.le import (
    ScanCallback,
    ScanResult,
)
from java import Override, jint, jvoid, static_proxy

from bleak.backends.android.dispatcher import (
    CallbackDispatcher,
)
from bleak.backends.android.scanner_callback import OnScanCallback, OnScanResult
from bleak.backends.android.status import ScanFailed


class _PythonScanCallback(static_proxy(ScanCallback)):
    """Callback class for LE Scan. PRIVATE.

    This class holds methods that receive and handle
    data from Android's BluetoothLeScanner methods.
    It is not intended to call this class directly.
    """

    def __init__(self, scanner, loop: asyncio.AbstractEventLoop):
        super(_PythonScanCallback, self).__init__()
        self._loop = loop
        self._scanner = scanner
        self.java = self
        self.dispatcher = CallbackDispatcher(loop)

    @Override(jvoid, [jint])
    def onScanFailed(self, errorCode: jint):
        self.dispatcher.result_state_threadsafe(
            ScanFailed(int(errorCode)).name,
            OnScanCallback(),
            OnScanResult(None),
        )

    @Override(jvoid, [jint, ScanResult])
    def onScanResult(self, callbackType: jint, result: ScanResult):
        self._loop.call_soon_threadsafe(self._scanner._handle_scan_result, result)

        if OnScanCallback() not in self.dispatcher.states:
            self.dispatcher.result_state_threadsafe(
                None,
                OnScanCallback(),
                OnScanResult(result),
            )
