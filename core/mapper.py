from core.emulator import EmulateX360
from core.hid_manager import HIDWorker
import json


class Mapper:
    """Connects a physical HID controller to a virtual Xbox 360 controller."""

    def __init__(self, controller, controller_type, poll_interval=0.008):
        self.controller = controller
        self.poll_interval = poll_interval
        self.emulator = EmulateX360(controller.device_path)
        self.hid_worker = HIDWorker(controller, poll_interval)
        self._connected = False
        self.controller_config = None

        self.load_json(f"{controller_type}.json")

        self.hid_worker.data_received.connect(self.handle_input)
        self.hid_worker.error.connect(self.handle_error)

    def load_json(self, filename):
        try:
            with open(f"profiles/{filename}", "r") as config:
                self.controller_config = json.load(config)
        except FileNotFoundError:
            raise ValueError(f"Profile '{filename}' not found (try remapping manually)")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in profile '{filename}'")

    def start(self):
        if not self._connected:
            self._connected = True
            self.hid_worker.run()

    def stop(self):
        self.hid_worker.stop()
        self._connected = False

    def handle_input(self, data: bytes):
        report = list(data)
        if len(report) < 10:
            return

        ljx = report[1]
        ljy = report[2]
        rjx = report[3]
        rjy = report[4]

        a = bool(report[5] & 0x20)
        b = bool(report[5] & 0x40)
        x = bool(report[5] & 0x10)
        y = bool(report[5] & 0x80)
        lb = bool(report[6] & 0x01)
        rb = bool(report[6] & 0x02)
        lt = report[7]
        rt = report[8]

        dpu = bool(report[9] & 0x01)
        dpd = bool(report[9] & 0x02)
        dpl = bool(report[9] & 0x04)
        dpr = bool(report[9] & 0x08)

        self.emulator.update_controller(
            ljx, ljy, rjx, rjy, a, x, b, y, rb, rt, lb, lt, dpu, dpd, dpr, dpl
        )

    def handle_error(self, err_msg):
        print(f"[Mapper] Error on {self.controller}: {err_msg}")
        self.stop()
