from PySide6.QtCore import QObject, QThread
from .hid_manager import HIDWorker
import hid
from core.controller import Controller


class HIDManager(QObject):
    """High-level manager to scan devices and poll multiple controllers simultaneously."""

    def __init__(self, poll_interval=0.008):
        super().__init__()
        self.poll_interval = poll_interval
        self.devices = []
        self._workers = {}  # each key is a device path

    def scan_devices(self):
        """Return all connected HID devices."""
        self.devices = hid.enumerate()
        return self.devices

    def start_polling(self, vendor_id, product_id, path, name=None, on_data=None, on_error=None):
        """Start a worker for a specific controller."""
        if path in self._workers:
            print(f"Already polling device {path}")
            return

        controller = Controller(vendor_id, product_id, name, path)

        thread = QThread()
        worker = HIDWorker(controller, self.poll_interval)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        if on_data:
            worker.data_received.connect(on_data)
        if on_error:
            worker.error.connect(on_error)

        thread.start()

        self._workers[path] = (thread, worker)

        return controller

    def stop_polling(self, path):
        """Stop polling a specific device."""
        if path in self._workers:
            thread, worker = self._workers.pop(path)
            worker.stop()

    def stop_all(self):
        """Stop all polling workers."""
        for path in list(self._workers.keys()):
            self.stop_polling(path)
