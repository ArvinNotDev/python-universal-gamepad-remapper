from core.emulator import EmulateX360, EmulateKeyboard
import json


class Mapper:
    """
    Simple-syntax Mapper that keeps the old variable style (ljx, ljy, ...) but
    applies proper scaling and supports per-axis 'invert' in the JSON profile.
    """

    def __init__(self, controller, controller_type, emulate_to, settings, debug=False):
        self.controller = controller
        self.controller_type = controller_type
        self._connected = False
        self.debug = debug
        self.settings = settings

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

    @staticmethod
    def _clamp(v, lo, hi):
        return max(lo, min(hi, v))

    @staticmethod
    def _scale_stick_0_255_to_x360(val, invert_y):
        """
        Scale unsigned 0..255 (center ~128) to X360 signed 16-bit -32768..32767.
        """
        centered = float(val) - 128.0
        if invert_y:
            normalized = -1 * centered / 127.0
        else:
            normalized = centered / 127.0
        scaled = int(round(normalized * 32767.0))
        return int(Mapper._clamp(scaled, -32768, 32767))

    def _read_byte_safe(self, report, idx):
        if idx is None:
            return 0
        if idx < 0 or idx >= len(report):
            return 0
        return report[idx]

    def _get_button_from_cfg(self, report, cfg):
        if cfg is None:
            return False
        val = self._read_byte_safe(report, cfg.get("index", cfg.get("byte")))
        if "value" in cfg:
            return val == cfg["value"]
        mask = cfg.get("mask")
        if mask is None:
            return False
        if isinstance(mask, str):
            mask_int = int(mask, 16)
        else:
            mask_int = int(mask)
        return (val & mask_int) != 0
    
    def _apply_deadzone(self, raw_x, raw_y, deadzone, invert_y, invert_x):
        cx = raw_x - 128
        cy = raw_y - 128
        if abs(cx) < deadzone * 127:
            cx = 0
        if abs(cy) < deadzone * 127:
            cy = 0
        x_scaled = self._scale_stick_0_255_to_x360(cx + 128, invert_x)
        y_scaled = self._scale_stick_0_255_to_x360(cy + 128, invert_y)
        return x_scaled, y_scaled

    def _handle_x360_input(self, data: bytes):
        report = list(data)
        if len(report) < 10:
            return

        axes_cfg = self.controller_config.get("axes", {})
        buttons_cfg = self.controller_config.get("buttons", {})
        deadzone_cfg = self.controller_config.get("deadzones")

        left_x_cfg = axes_cfg.get("left_stick_x", {})
        left_y_cfg = axes_cfg.get("left_stick_y", {})
        right_x_cfg = axes_cfg.get("right_stick_x", {})
        right_y_cfg = axes_cfg.get("right_stick_y", {})
        lt_cfg = axes_cfg.get("left_trigger", {})
        rt_cfg = axes_cfg.get("right_trigger", {})

        raw_ljx = self._read_byte_safe(report, left_x_cfg.get("index", left_x_cfg.get("byte")))
        raw_ljy = self._read_byte_safe(report, left_y_cfg.get("index", left_y_cfg.get("byte")))
        raw_rjx = self._read_byte_safe(report, right_x_cfg.get("index", right_x_cfg.get("byte")))
        raw_rjy = self._read_byte_safe(report, right_y_cfg.get("index", right_y_cfg.get("byte")))
        raw_lt  = self._read_byte_safe(report, lt_cfg.get("index", lt_cfg.get("byte")))
        raw_rt  = self._read_byte_safe(report, rt_cfg.get("index", rt_cfg.get("byte")))

        if left_x_cfg.get("signed", False) and raw_ljx > 127:
            raw_ljx -= 256
        if left_y_cfg.get("signed", False) and raw_ljy > 127:
            raw_ljy -= 256
        if right_x_cfg.get("signed", False) and raw_rjx > 127:
            raw_rjx -= 256
        if right_y_cfg.get("signed", False) and raw_rjy > 127:
            raw_rjy -= 256
        if lt_cfg.get("signed", False) and raw_lt > 127:
            raw_lt -= 256
        if rt_cfg.get("signed", False) and raw_rt > 127:
            raw_rt -= 256
        
        left_stick_deadzone, right_stick_deadzone = self.settings.get_deadzones()

        ljx, ljy = self._apply_deadzone(raw_ljx, raw_ljy, left_stick_deadzone, left_y_cfg.get("invert", False), left_x_cfg.get("invert", False))
        rjx, rjy = self._apply_deadzone(raw_rjx, raw_rjy, right_stick_deadzone, right_y_cfg.get("invert", False), right_x_cfg.get("invert", False))

        lt = int(raw_lt)
        rt = int(raw_rt)
        if lt_cfg.get("invert", False):
            lt = 255 - lt
        if rt_cfg.get("invert", False):
            rt = 255 - rt

        a  = self._get_button_from_cfg(report, buttons_cfg.get("cross"))
        b  = self._get_button_from_cfg(report, buttons_cfg.get("circle"))
        x_ = self._get_button_from_cfg(report, buttons_cfg.get("square"))
        y_ = self._get_button_from_cfg(report, buttons_cfg.get("triangle"))
        lb = self._get_button_from_cfg(report, buttons_cfg.get("l1"))
        rb = self._get_button_from_cfg(report, buttons_cfg.get("r1"))

        dpu = self._get_button_from_cfg(report, buttons_cfg.get("dpad_up"))
        dpd = self._get_button_from_cfg(report, buttons_cfg.get("dpad_down"))
        dpl = self._get_button_from_cfg(report, buttons_cfg.get("dpad_left"))
        dpr = self._get_button_from_cfg(report, buttons_cfg.get("dpad_right"))

        if self.debug:
            print(
                f"[Mapper][DEBUG] raw_ljx={raw_ljx} raw_ljy={raw_ljy} -> ljx={ljx} ljy={ljy} | "
                f"raw_rjx={raw_rjx} raw_rjy={raw_rjy} -> rjx={rjx} rjy={rjy} | "
                f"lt={lt} rt={rt}"
            )

        self.emulator.update(
            ljx, ljy, rjx, rjy,
            a, x_, b, y_,
            rb, rt, lb, lt,
            dpu, dpd, dpl, dpr
        )

    def _handle_keyboard_input(self, data: bytes):
        pass

    def handle_error(self, msg):
        print(f"[Mapper] Error from device {self.controller.name}: {msg}")
        self.stop()

