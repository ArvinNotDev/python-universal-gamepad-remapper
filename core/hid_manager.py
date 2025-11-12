from PySide6.QtCore import QObject, Signal
import hid
import time


class HIDWorker(QObject):
    """Background HID polling worker for a single controller."""
    data_received = Signal(bytes)
    error = Signal(str)
    finished = Signal()

    def __init__(self, controller, poll_interval: float = 0.008):
        super().__init__()
        self.controller = controller
        self.poll_interval = poll_interval
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        """Poll the device in a loop."""
        try:
            with hid.Device(path=self.controller.path) as dev:
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
