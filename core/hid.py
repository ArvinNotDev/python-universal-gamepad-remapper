from PySide6.QtCore import QObject, QThread
from .hid_manager import HIDWorker
import hid
from core.controller import Controller


class HIDManager(QObject):
    """Manages multiple HID controllers with polling in QThreads."""

    def __init__(self, poll_interval=0.008):
        super().__init__()
        self.poll_interval = poll_interval
        self.devices = []
        self._workers = {}  # unique_id -> (thread, worker)

    def scan_devices(self):
        """Scan all connected HID devices."""
        self.devices = hid.enumerate()
        return self.devices

    def start_polling(self, vendor_id, product_id, path, name=None, on_data=None, on_error=None):
        """Start polling a single controller."""
        controller = Controller(vendor_id, product_id, path, name)
        key = controller.unique_id

        if key in self._workers:
            print(f"[HIDManager] Already polling {controller}")
            return controller

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
        self._workers[key] = (thread, worker)
        return controller

    def stop_polling(self, vendor_id, product_id, path):
        """Stop polling a controller by its unique identifiers."""
        key = f"{vendor_id:04X}:{product_id:04X}:{path}"
        if key in self._workers:
            thread, worker = self._workers.pop(key)
            worker.stop()

    def stop_all(self):
        """Stop all polling workers."""
        for key in list(self._workers.keys()):
            thread, worker = self._workers.pop(key)
            worker.stop()
