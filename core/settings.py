import configparser
from pathlib import Path

class SettingsManager:
    def __init__(self, path="config/settings.conf"):
        self.path = Path(path)
        self.config = configparser.ConfigParser()

        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.config["device"] = {
                "polling_rate": "1.0",
                "auto_reconnect": "false",
                "dpad_as_mouse": "true",
                "left_stick_deadzone": "0.000000",
                "right_stick_deadzone": "0.000000",
                "right_stick_invert_x": "false",
                "right_stick_invert_y": "false",
                "left_stick_invert_x": "false",
                "left_stick_invert_y": "true",
                "mouse_mode": "false",
                "mouse_sensitivity": "1.0"
            }
            self.config["ui"] = {
                "language": "eng",
                "theme": "dark"
            }
            self.config["developer"] = {
                "debug": "false",
                "raw_hid_debug": "false",
                "log_to_file": "false",
                "log_file_path": "logs/mapper.log"
            }
            with self.path.open("w", encoding="utf-8") as f:
                self.config.write(f)

        self.config.read(self.path)

    # -------- device --------
    def get_polling_rate(self):
        return self.config.getfloat("device", "polling_rate", fallback=1.0)

    def set_polling_rate(self, v: float):
        if not self.config.has_section("device"):
            self.config.add_section("device")
        self.config.set("device", "polling_rate", str(float(v)))

    def get_auto_reconnect(self):
        return self.config.getboolean("device", "auto_reconnect", fallback=False)

    def set_auto_reconnect(self, enabled: bool):
        if not self.config.has_section("device"):
            self.config.add_section("device")
        self.config.set("device", "auto_reconnect", "true" if enabled else "false")

    def get_dpad_as_mouse(self):
        return self.config.getboolean("device", "dpad_as_mouse", fallback=True)

    def set_dpad_as_mouse(self, enabled: bool):
        if not self.config.has_section("device"):
            self.config.add_section("device")
        self.config.set("device", "dpad_as_mouse", "true" if enabled else "false")

    def get_deadzones(self):
        left = self.config.getfloat("device", "left_stick_deadzone", fallback=0.1)
        right = self.config.getfloat("device", "right_stick_deadzone", fallback=0.1)
        left = max(0.0, min(1.0, left))
        right = max(0.0, min(1.0, right))
        return left, right

    def set_deadzones(self, left: float, right: float):
        if not self.config.has_section("device"):
            self.config.add_section("device")
        left = max(0.0, min(1.0, float(left)))
        right = max(0.0, min(1.0, float(right)))
        self.config.set("device", "left_stick_deadzone", f"{left:.6f}")
        self.config.set("device", "right_stick_deadzone", f"{right:.6f}")

    def get_invertion(self):
        left_x = self.config.getboolean("device", "left_stick_invert_x", fallback=False)
        left_y = self.config.getboolean("device", "left_stick_invert_y", fallback=False)
        right_x = self.config.getboolean("device", "right_stick_invert_x", fallback=False)
        right_y = self.config.getboolean("device", "right_stick_invert_y", fallback=False)
        return ((left_x, left_y), (right_x, right_y))
    
    def set_invertion(self, left: tuple, right: tuple):
        if not self.config.has_section("device"):
            self.config.add_section("device")
        self.config.set("device", "left_stick_invert_x", "true" if bool(left[0]) else "false")
        self.config.set("device", "left_stick_invert_y", "true" if bool(left[1]) else "false")
        self.config.set("device", "right_stick_invert_x", "true" if bool(right[0]) else "false")
        self.config.set("device", "right_stick_invert_y", "true" if bool(right[1]) else "false")

    def get_mouse_mode(self):
        return self.config.getboolean("device", "mouse_mode", fallback=False)
    
    def set_mouse_mode(self, enabled: bool):
        if not self.config.has_section("device"):
            self.config.add_section("device")
        self.config.set("device", "mouse_mode", "true" if enabled else "false")

    def get_mouse_sensitivity(self):
        return self.config.getfloat("device", "mouse_sensitivity", fallback=1.0)
    
    def set_mouse_sensitivity(self, sens: float):
        if not self.config.has_section("device"):
            self.config.add_section("device")
        self.config.set("device", "mouse_sensitivity", f"{float(sens):.6f}")
        
    # -------- ui --------
    def get_ui_language(self):
        return self.config.get("ui", "language", fallback="eng")

    def set_ui_language(self, lang: str):
        if not self.config.has_section("ui"):
            self.config.add_section("ui")
        self.config.set("ui", "language", str(lang))

    def get_ui_theme(self):
        return self.config.get("ui", "theme", fallback="dark")

    def set_ui_theme(self, theme_name: str):
        if not self.config.has_section("ui"):
            self.config.add_section("ui")
        self.config.set("ui", "theme", str(theme_name))

    # -------- developer --------
    def get_developer_debug(self):
        return self.config.getboolean("developer", "debug", fallback=False)

    def set_developer_debug(self, enabled: bool):
        if not self.config.has_section("developer"):
            self.config.add_section("developer")
        self.config.set("developer", "debug", "true" if enabled else "false")

    def get_raw_hid_debug(self):
        return self.config.getboolean("developer", "raw_hid_debug", fallback=False)

    def set_raw_hid_debug(self, enabled: bool):
        if not self.config.has_section("developer"):
            self.config.add_section("developer")
        self.config.set("developer", "raw_hid_debug", "true" if enabled else "false")

    def get_log_to_file(self):
        return self.config.getboolean("developer", "log_to_file", fallback=False)

    def set_log_to_file(self, enabled: bool):
        if not self.config.has_section("developer"):
            self.config.add_section("developer")
        self.config.set("developer", "log_to_file", "true" if enabled else "false")

    def get_log_file_path(self):
        return self.config.get("developer", "log_file_path", fallback="logs/mapper.log")

    def set_log_file_path(self, path: str):
        if not self.config.has_section("developer"):
            self.config.add_section("developer")
        self.config.set("developer", "log_file_path", str(path))

    # -------- save/load --------
    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            self.config.write(f)
