import asyncio

from jnius import PythonJavaClass, java_method  # type: ignore

from bleak.backends.android.dispatcher import (
    CallbackDispatcher,
)
from bleak.backends.android.p4android.defs import (
    PythonScanCallback,
)
from bleak.backends.android.scanner import BleakScannerAndroid
from bleak.backends.android.scanner_callback import OnScanCallback, OnScanResult
from bleak.backends.android.status import ScanFailed


class _PythonScanCallback(PythonJavaClass):
    __javacontext__ = "app"
    __javainterfaces__ = ["com.github.hbldh.bleak.PythonScanCallback$Interface"]

    def __init__(self, scanner: BleakScannerAndroid, loop: asyncio.AbstractEventLoop):
        super().__init__(loop)
        self._loop = loop
        self._scanner = scanner
        self.java = PythonScanCallback(self)
        self.dispatcher = CallbackDispatcher(loop)

    @java_method("(I)V")
    def onScanFailed(self, errorCode):
        self.dispatcher.result_state_threadsafe(
            ScanFailed(errorCode).name,
            OnScanCallback(),
            OnScanResult(None),
        )

    @java_method("(Landroid/bluetooth/le/ScanResult;)V")
    def onScanResult(self, result):
        self._loop.call_soon_threadsafe(self._scanner._handle_scan_result, result)

        if OnScanCallback() not in self.dispatcher.states:
            self.dispatcher.result_state_threadsafe(
                None,
                OnScanCallback(),
                OnScanResult(result),
            )
