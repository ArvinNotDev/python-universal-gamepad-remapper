from PySide6.QtCore import QObject, QThread, Signal
import hid
import time


class HIDWorker(QObject):
    """Background HID polling worker that runs in a QThread."""
    data_received = Signal(bytes)
    error = Signal(str)
    finished = Signal()

    def __init__(self, device_path: str, poll_interval: float = 0.008):
        super().__init__()
        self.device_path = device_path
        self.poll_interval = poll_interval
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        """Main loop running inside QThread."""
        try:
            with hid.Device(path=self.device_path) as dev:
                while self._running:
                    try:
                        data = dev.read(64)
                        if data:
                            self.data_received.emit(bytes(data))
                        time.sleep(self.poll_interval)
                    except Exception as e:
                        self.error.emit(str(e))
                        break
        except Exception as e:
            self.error.emit(f"Failed to open HID device: {e}")
        finally:
            self.finished.emit()
