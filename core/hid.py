from PySide6.QtCore import QObject
from .hid_manager import HIDWorker
from PySide6.QtCore import QThread
import hid


class HIDManager(QObject):
    """High-level manager that handles scanning and thread management."""

    def __init__(self, poll_interval=0.008):
        super().__init__()
        self.devices = []
        self.poll_interval = poll_interval
        self._thread = None
        self._worker = None

    def scan_devices(self):
        """List all HID devices currently connected."""
        self.devices = hid.enumerate()
        return self.devices

    def start_polling(self, device_path, on_data=None, on_error=None):
        """Start a polling worker in a QThread."""
        if self._thread is not None:
            print("Polling already running.")
            return

        self._thread = QThread()
        self._worker = HIDWorker(device_path, self.poll_interval)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        if on_data:
            self._worker.data_received.connect(on_data)
        if on_error:
            self._worker.error.connect(on_error)

        self._thread.start()

    def stop(self):
        """Stop the polling loop cleanly."""
        if self._worker:
            self._worker.stop()
        self._worker = None
        self._thread = None
