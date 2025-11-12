from core.emulator import EmulateX360, EmulateKeyboard
from core.hid_manager import HIDWorker
import json


class Mapper:
    """Connects a physical HID controller to a virtual Xbox 360 controller."""

    def __init__(self, controller, controller_type, emulate_to, poll_interval=0.008):
        self.controller = controller
        self.poll_interval = poll_interval

        if emulate_to == "x360":
            self.emulator = EmulateX360(controller.device_path)
        elif emulate_to == "keyboard":
            self.emulator = EmulateKeyboard()
        else:
            raise ValueError(f"Invalid emulate_to target: {emulate_to}")
        
        self.hid_worker = HIDWorker(controller, poll_interval)
        self._connected = False
        self.controller_config = None

        self.load_json(f"{controller_type}.json")
        if isinstance(self.emulator, EmulateX360):
            self.hid_worker.data_received.connect(self.x360_handle_input)
        elif isinstance(self.emulator, EmulateKeyboard):
            self.hid_worker.data_received.connect(self.keyboard_handle_input)
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
            print(f"[Mapper] Starting mapper for {self.controller.name}")
            self.hid_worker.run()

    def stop(self):
        self.hid_worker.stop()
        self._connected = False

    def x360_handle_input(self, data: bytes):
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

        self.emulator.update(
            ljx, ljy, rjx, rjy, a, x, b, y, rb, rt, lb, lt, dpu, dpd, dpr, dpl
        )

    def keyboard_handle_input(self, data: bytes):
        pass

    def handle_error(self, err_msg):
        print(f"[Mapper] Error on {self.controller}: {err_msg}")
        self.stop()
