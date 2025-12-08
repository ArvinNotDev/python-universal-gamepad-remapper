from core.emulator import EmulateX360, EmulateKeyboard
import json


class Mapper:
    """
    Connects HIDWorker output (data_received signal) to a virtual emulator.
    Mapper never polls hardware directly.
    """

    def __init__(self, controller, controller_type, emulate_to):
        self.controller = controller
        self.controller_type = controller_type
        self._connected = False

        if emulate_to == "x360":
            self.emulator = EmulateX360(controller.device_path)
        elif emulate_to == "keyboard":
            self.emulator = EmulateKeyboard()
        else:
            raise ValueError(f"Invalid emulate_to target: {emulate_to}")

        self.controller_config = self._load_json(f"{controller_type}.json")

    def _load_json(self, filename):
        try:
            with open(f"profiles/{filename}", "r") as config:
                return json.load(config)
        except FileNotFoundError:
            raise ValueError(f"Profile '{filename}' not found")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in profile '{filename}'")

    def start(self):
        if not self._connected:
            self._connected = True
            print(f"[Mapper] Started mapping for {self.controller.name}")

    def stop(self):
        if self._connected:
            print(f"[Mapper] Stopped mapping for {self.controller.name}")
        self._connected = False

    def handle_hid_data(self, data: bytes):
        if not self._connected:
            return

        if isinstance(self.emulator, EmulateX360):
            self._handle_x360_input(data)
        else:
            self._handle_keyboard_input(data)

    def _handle_x360_input(self, data: bytes):
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

    def _handle_keyboard_input(self, data: bytes):
        pass

    def handle_error(self, msg):
        print(f"[Mapper] Error from device {self.controller}: {msg}")
        self.stop()
