from PySide6.QtCore import QObject, QThread, Signal
import hid
import time


class HIDWorker(QObject):
    data_received = Signal(bytes)
    error = Signal(str)
    finished = Signal()

    def __init__(self, controller, poll_interval=0.008):
        super().__init__()
        self.controller = controller
        self.poll_interval = poll_interval
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        ds = hid.device()
        try:
            ds.open_path(self.controller.device_path)
            # for rid in [0x05, 0x09, 0x20]:
            #     try:
            #         data = ds.get_feature_report(rid, 65)
            #         print(hex(rid), data)
            #     except Exception as e:
            #         print("fail", hex(rid), e)
            ds.get_feature_report(0x05, 65)     # feature report to make the controller give more data
        except Exception as e:
            self.error.emit(f"Failed to open {self.controller}: {e}")
            self.finished.emit()
            return

        try:
            while self._running:
                try:
                    try:
                        report = ds.read(65, timeout_ms=1)
                        # for i, r in enumerate(report):
                        #     if not r:
                        #         report = report[:i] + report[i+1:]
                        # print(report)
                    except TypeError:
                        report = ds.read(65, timeout=1)

                    if report:
                        self.data_received.emit(bytes(report))

                    time.sleep(self.poll_interval)

                except Exception as e:
                    self.error.emit(str(e))
                    break

        finally:
            ds.close()
            self.finished.emit()
