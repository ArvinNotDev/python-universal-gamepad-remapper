from core.emulator import EmulateX360, EmulateKeyboard
from core.mouse import Mouse
import json
import pyautogui

class Mapper:

    def __init__(self, controller, controller_type, emulate_to, settings, debug=False):
        self.controller = controller
        self.controller_type = controller_type
        self._connected = False
        self.debug = debug
        self.settings = settings
        self.mouse_mode = True
        self._prev_back = False
        self._prev_a = False
        self._prev_b = False

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
        
        byte_idx = cfg.get("index", cfg.get("byte"))
        val = self._read_byte_safe(report, byte_idx)
        
        mask = cfg.get("mask")
        if mask is not None:
            if isinstance(mask, str):
                mask_int = int(mask, 16)
            else:
                mask_int = int(mask)
            val = val & mask_int

        if "value" in cfg:
            return val == cfg["value"]
        
        return val != 0
    
    def _get_dpad_from_hat(self, report, cfg):
        """
        Decodes 0-7 Hat Switch value into (Up, Down, Left, Right) booleans.
        0=N, 1=NE, 2=E, 3=SE, 4=S, 5=SW, 6=W, 7=NW, 8=Released
        """
        if cfg is None:
            return False, False, False, False
            
        byte_idx = cfg.get("byte")
        raw_val = self._read_byte_safe(report, byte_idx)
        
        mask = cfg.get("mask", 0x0F)
        if isinstance(mask, str):
            mask = int(mask, 16)
            
        hat_val = raw_val & mask

        up = hat_val in [0, 1, 7]
        down = hat_val in [3, 4, 5]
        right = hat_val in [1, 2, 3]
        left = hat_val in [5, 6, 7]

        return up, down, left, right

    def _apply_deadzone(self, raw_x, raw_y, deadzone, invertion):
        invert_x, invert_y = invertion
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
        dpad_cfg = self.controller_config.get("dpad_hat", {})
        
        left_x_cfg = axes_cfg.get("left_stick_x", {})
        left_y_cfg = axes_cfg.get("left_stick_y", {})
        right_x_cfg = axes_cfg.get("right_stick_x", {})
        right_y_cfg = axes_cfg.get("right_stick_y", {})
        lt_cfg = axes_cfg.get("left_trigger", {})
        rt_cfg = axes_cfg.get("right_trigger", {})

        raw_ljx = self._read_byte_safe(report, left_x_cfg.get("byte"))
        raw_ljy = self._read_byte_safe(report, left_y_cfg.get("byte"))
        raw_rjx = self._read_byte_safe(report, right_x_cfg.get("byte"))
        raw_rjy = self._read_byte_safe(report, right_y_cfg.get("byte"))
        raw_lt  = self._read_byte_safe(report, lt_cfg.get("byte"))
        raw_rt  = self._read_byte_safe(report, rt_cfg.get("byte"))
        
        left_stick_deadzone, right_stick_deadzone = self.settings.get_deadzones()
        left_stick_invertion, right_stick_invertion = self.settings.get_invertion()

        ljx, ljy = self._apply_deadzone(raw_ljx, raw_ljy, left_stick_deadzone, left_stick_invertion)
        rjx, rjy = self._apply_deadzone(raw_rjx, raw_rjy, right_stick_deadzone, right_stick_invertion)

        lt = int(raw_lt)
        rt = int(raw_rt)

        a  = self._get_button_from_cfg(report, buttons_cfg.get("cross"))
        b  = self._get_button_from_cfg(report, buttons_cfg.get("circle"))
        x_ = self._get_button_from_cfg(report, buttons_cfg.get("square"))
        y_ = self._get_button_from_cfg(report, buttons_cfg.get("triangle"))
        lb = self._get_button_from_cfg(report, buttons_cfg.get("l1"))
        rb = self._get_button_from_cfg(report, buttons_cfg.get("r1"))
        
        back  = self._get_button_from_cfg(report, buttons_cfg.get("share"))
        start = self._get_button_from_cfg(report, buttons_cfg.get("option"))
        l3    = self._get_button_from_cfg(report, buttons_cfg.get("l3"))
        r3    = self._get_button_from_cfg(report, buttons_cfg.get("r3"))

        dpu, dpd, dpl, dpr = self._get_dpad_from_hat(report, dpad_cfg)

        if self.debug:
            print(f"Hat: U={dpu} D={dpd} L={dpl} R={dpr} | Btns: Back={back} Start={start}")
        
        self.mouse_mode = self.settings.get_mouse_mode()
        if self.mouse_mode:
            if not hasattr(self, "_mx"):
                self._mx = 0.0
                self._my = 0.0

            try:
                sensitivity = self.settings.get_mouse_sensitivity()
            except Exception:
                sensitivity = 1.0

            nx = ljx / 32768.0
            ny = ljy / 32768.0

            speed = 35.0 * sensitivity
            target_dx = nx * speed
            target_dy = -ny * speed

            alpha = 0.25
            self._mx = self._mx * (1.0 - alpha) + target_dx * alpha
            self._my = self._my * (1.0 - alpha) + target_dy * alpha

            Mouse.moveRel(self._mx, self._my, duration=0)

            if a and not self._prev_a:
                Mouse.leftClick()
                self._prev_a = True
            if not a:
                self._prev_a = False
            if b and not self._prev_b:
                Mouse.rightClick()
                self._prev_b = True
            if not b:
                self._prev_b = False
            if back and not self._prev_back:
                self.mouse_mode = False
            self._prev_back = back
        else:
            self.emulator.update(
                ljx, ljy, rjx, rjy,
                a, x_, b, y_,
                rb, rt, lb, lt,
                dpu, dpd, dpr, dpl,
                back, start, l3, r3
            )

    def _handle_keyboard_input(self, data: bytes):
        pass

    def handle_error(self, msg):
        print(f"[Mapper] Error from device {self.controller.name}: {msg}")
        self.stop()