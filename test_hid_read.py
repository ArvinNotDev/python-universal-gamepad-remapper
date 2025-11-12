import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton
from PySide6.QtCore import QObject, Signal, QThread, Slot
import hid
import time


# -------------------------
# Worker
# -------------------------
class HIDWorker(QObject):
    data_received = Signal(int, int)
    finished = Signal()

    def __init__(self, path, poll_interval=0.01):
        super().__init__()
        self.path = path
        self.poll_interval = poll_interval
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        try:
            device = hid.device()
            device.open_path(self.path)
            while self._running:
                data = device.read(64)
                if data:
                    # emit only left analog (indexes 1 and 2)
                    self.data_received.emit(data[1], data[2])
                time.sleep(self.poll_interval)
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.finished.emit()


# -------------------------
# GUI
# -------------------------
class SimpleHIDTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Left Analog Test")
        self.resize(300, 150)

        self.manager = {}  # path -> (thread, worker)

        layout = QVBoxLayout(self)

        self.device_combo = QComboBox()
        layout.addWidget(self.device_combo)

        self.start_btn = QPushButton("Start Reading")
        layout.addWidget(self.start_btn)

        self.left_x_label = QLabel("Left X: 0")
        self.left_y_label = QLabel("Left Y: 0")
        layout.addWidget(self.left_x_label)
        layout.addWidget(self.left_y_label)

        # Scan devices
        self.devices = hid.enumerate()
        for d in self.devices:
            name = d.get('product_string', 'Unknown')
            self.device_combo.addItem(f"{name} ({d['vendor_id']:04X}:{d['product_id']:04X})", d)

        self.start_btn.clicked.connect(self.start_reading)

    @Slot(int, int)
    def update_analog(self, x, y):
        self.left_x_label.setText(f"Left X: {x}")
        self.left_y_label.setText(f"Left Y: {y}")

    def start_reading(self):
        index = self.device_combo.currentIndex()
        if index < 0:
            return
        d = self.device_combo.itemData(index)
        path = d['path']

        if path in self.manager:
            return  # already running

        thread = QThread()
        worker = HIDWorker(path)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        worker.data_received.connect(self.update_analog)

        thread.start()
        self.manager[path] = (thread, worker)


# -------------------------
# Main
# -------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleHIDTest()
    window.show()
    sys.exit(app.exec())
