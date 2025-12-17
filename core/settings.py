import configparser
from pathlib import Path

class SettingsManager:
    def __init__(self, path="config/settings.conf"):
        self.path = Path(path)
        self.config = configparser.ConfigParser()

        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.config["device"] = {
                "polling_rate": "2",
                "auto_reconnect": "false",
                "dpad_as_mouse": "true",
                "left_stick_deadzone": "0.1",
                "right_stick_deadzone": "0.1",
            }
            self.config["ui"] = {
                "language": "eng",
                "theme": "dark",
            }
            self.config["developer"] = {
                "debug": "false",
                "raw_hid_debug": "false",
                "log_to_file": "false",
                "log_file_path": "logs/mapper.log",
            }
            with self.path.open("w") as f:
                self.config.write(f)
        
        self.config.read(path)

    def get_device_section(self):
        return self.config["device"]

    def get_ui_section(self):
        return self.config["ui"]

    def get_developer_section(self):
        return self.config["developer"]

    def get_deadzones(self):
        left = self.config.getfloat("device", "left_stick_deadzone")
        right = self.config.getfloat("device", "right_stick_deadzone")
        return left, right

    def set_deadzone(self, left, right):
        self.config.set("device", "left_stick_deadzone", str(left))
        self.config.set("device", "right_stick_deadzone", str(right))

    def save(self):
        with open(self.path, "w") as f:
            self.config.write(f)