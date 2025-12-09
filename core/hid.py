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
        self._workers = {}  # device_path -> (thread, worker, controller)

    def scan_devices(self):
        """Scan all connected HID devices."""
        self.devices = hid.enumerate()
        return self.devices

    def start_polling(self, vendor_id, product_id, path, name=None, on_data=None, on_error=None):
        """Start polling a single controller."""
        if path in self._workers:
            print(f"[HIDManager] Already polling device at path: {path}")
            return self._workers[path][2]  # return the controller

        controller = Controller(vendor_id, product_id, path, name)

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
        self._workers[path] = (thread, worker, controller)
        return controller

    def stop_polling(self, device_path):
        if device_path in self._workers:
            thread, worker, controller = self._workers[device_path]

            worker.stop()

            def on_thread_finished():
                if device_path in self._workers:
                    self._workers.pop(device_path, None)

            thread.finished.connect(on_thread_finished)


    def stop_all(self):
        for device_path, (thread, worker, controller) in list(self._workers.items()):
            worker.stop()

            def cleanup(dp=device_path):
                self._workers.pop(dp, None)

            thread.finished.connect(cleanup)
